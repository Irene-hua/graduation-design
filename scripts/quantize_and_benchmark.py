"""
Quantize and benchmark script
Supports: testing 4-bit loading with bitsandbytes (transformers) and measuring latency & memory

Usage examples (PowerShell):
$env:OMP_NUM_THREADS="2"; $env:MKL_NUM_THREADS="2"; python .\scripts\quantize_and_benchmark.py --model-path ./data/models/all-MiniLM-L6-v2 --device cuda --runs 10

Notes:
- For bitsandbytes 4-bit loading you need: transformers, accelerate, bitsandbytes, peft (optional)
- On Windows, bitsandbytes may require a compatible CUDA and a wheel; consider using WSL or a Linux machine if installation fails.
- This script measures GPU memory via torch.cuda and CPU memory via psutil.Process().memory_info().rss

"""
import argparse
import time
import os
import sys
from pathlib import Path

try:
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
except Exception:
    # We'll check at runtime and provide clear message
    pass

try:
    import psutil
    _HAS_PSUTIL = True
except Exception:
    psutil = None
    _HAS_PSUTIL = False
    # psutil is optional; script will still run but CPU memory measurements will be disabled


def now_ms():
    return int(time.time() * 1000)


def measure_inference(model, tokenizer, prompt, device, runs=10, warmup=2, max_new_tokens=64):
    # Prepare input ids
    inputs = tokenizer(prompt, return_tensors="pt")
    input_ids = inputs.input_ids.to(device if device in ['cpu','cuda'] else 'cpu')

    # Warmup
    for _ in range(warmup):
        with torch.no_grad():
            _ = model.generate(input_ids, max_new_tokens=max_new_tokens, do_sample=False)

    # Measure
    times = []
    proc = psutil.Process() if _HAS_PSUTIL else None
    peak_cpu_rss = 0 if _HAS_PSUTIL else None
    peak_gpu_mem = 0
    if device == 'cuda' and torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()

    for i in range(runs):
        t0 = time.time()
        with torch.no_grad():
            _ = model.generate(input_ids, max_new_tokens=max_new_tokens, do_sample=False)
        dt = (time.time() - t0) * 1000.0
        times.append(dt)
        # sample memory
        if _HAS_PSUTIL:
            rss = proc.memory_info().rss
            if rss > peak_cpu_rss:
                peak_cpu_rss = rss
        if device == 'cuda' and torch.cuda.is_available():
            current = torch.cuda.max_memory_allocated()
            if current > peak_gpu_mem:
                peak_gpu_mem = current

    avg = sum(times) / len(times) if times else None
    p50 = sorted(times)[len(times)//2] if times else None
    return {
        'times_ms': times,
        'avg_ms': avg,
        'p50_ms': p50,
        'peak_cpu_rss_bytes': peak_cpu_rss,
        'peak_gpu_bytes': peak_gpu_mem
    }


def run_bitsandbytes_benchmark(model_path, device, runs, warmup):
    # Check dependencies
    try:
        import transformers
        import bitsandbytes as bnb
        from transformers import AutoTokenizer, AutoModelForCausalLM
    except Exception as e:
        print("Missing required packages for bitsandbytes workflow. Install with:\n  pip install transformers bitsandbytes accelerate")
        raise

    # device detection
    use_cuda = (device == 'cuda') and torch.cuda.is_available()
    if device == 'cuda' and not use_cuda:
        print("Warning: CUDA requested but not available. Falling back to CPU.")
        device = 'cpu'

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=True)

    results = {}

    # Baseline: try to load full float model if possible (may OOM on GPU)
    print('\n== Baseline: attempt loading full-precision model (may OOM) ==')
    try:
        baseline_device = torch.device('cuda' if use_cuda else 'cpu')
        model_fp = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch.float32, device_map='auto' if use_cuda else None)
        model_fp.eval()
        print('Running baseline benchmark...')
        res_fp = measure_inference(model_fp, tokenizer, "This is a test prompt.", 'cuda' if use_cuda else 'cpu', runs=runs, warmup=warmup)
        results['baseline'] = res_fp
        del model_fp
        if use_cuda:
            torch.cuda.empty_cache()
        time.sleep(1)
    except Exception as e:
        print('Failed to load baseline full-precision model (this can happen for large models):', e)
        results['baseline_error'] = str(e)

    # 4-bit: load with load_in_4bit (requires bitsandbytes + compatible transformers)
    print('\n== 4-bit load via bitsandbytes (load_in_4bit=True) ==')
    try:
        model_4bit = AutoModelForCausalLM.from_pretrained(
            model_path,
            load_in_4bit=True,
            device_map='auto' if use_cuda else None,
            torch_dtype=torch.float16 if use_cuda else torch.float32,
        )
        model_4bit.eval()
        res_4b = measure_inference(model_4bit, tokenizer, "This is a test prompt.", 'cuda' if use_cuda else 'cpu', runs=runs, warmup=warmup)
        results['4bit'] = res_4b
        del model_4bit
        if use_cuda:
            torch.cuda.empty_cache()
    except Exception as e:
        print('Failed to load model in 4-bit with bitsandbytes:', e)
        results['4bit_error'] = str(e)

    return results


def parse_args():
    p = argparse.ArgumentParser(description='Quantize & benchmark LLM (bitsandbytes 4-bit workflow)')
    p.add_argument('--model-path', type=str, required=True, help='Path to pretrained model folder or HF id')
    p.add_argument('--device', type=str, choices=['cpu', 'cuda'], default='cpu')
    p.add_argument('--runs', type=int, default=6, help='Number of timed runs')
    p.add_argument('--warmup', type=int, default=2, help='Number of warmup runs')
    return p.parse_args()


def main():
    args = parse_args()
    model_path = os.path.expanduser(args.model_path)

    # allow HF id or path
    if not Path(model_path).exists() and not ("/" in model_path or ":" in model_path):
        print(f"Model path '{model_path}' does not exist and does not look like a HF id. Aborting.")
        sys.exit(1)

    print('Starting bitsandbytes 4-bit benchmark. This will try to load models and measure latency & memory.')

    try:
        results = run_bitsandbytes_benchmark(model_path, args.device, args.runs, args.warmup)
        print('\n=== Benchmark results ===')
        import json
        print(json.dumps(results, indent=2))
    except Exception as e:
        print('Benchmark failed:', e)
        sys.exit(2)


if __name__ == '__main__':
    main()
