"""Benchmark script for RAG system performance evaluation."""
import sys
import time
from pathlib import Path
import statistics
from typing import List, Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag_pipeline import RAGSystem
from src.encryption import generate_key


class Benchmark:
    """Benchmark suite for RAG system."""
    
    def __init__(self, rag_system: RAGSystem):
        """Initialize benchmark."""
        self.rag_system = rag_system
        self.results = {}
    
    def benchmark_embedding(self, texts: List[str], num_runs: int = 10) -> Dict[str, Any]:
        """Benchmark embedding generation."""
        print("\n[Embedding Benchmark]")
        print(f"Testing {len(texts)} texts, {num_runs} runs each")
        
        times = []
        
        for i in range(num_runs):
            start = time.time()
            self.rag_system.embedding_model.encode(texts)
            elapsed = time.time() - start
            times.append(elapsed)
            
            if (i + 1) % 5 == 0:
                print(f"  Run {i+1}/{num_runs}: {elapsed:.3f}s")
        
        result = {
            'mean': statistics.mean(times),
            'median': statistics.median(times),
            'stdev': statistics.stdev(times) if len(times) > 1 else 0,
            'min': min(times),
            'max': max(times)
        }
        
        print(f"\nResults:")
        print(f"  Mean: {result['mean']:.3f}s")
        print(f"  Median: {result['median']:.3f}s")
        print(f"  Std Dev: {result['stdev']:.3f}s")
        print(f"  Min: {result['min']:.3f}s")
        print(f"  Max: {result['max']:.3f}s")
        
        self.results['embedding'] = result
        return result
    
    def benchmark_encryption(self, texts: List[str], num_runs: int = 10) -> Dict[str, Any]:
        """Benchmark encryption/decryption."""
        print("\n[Encryption Benchmark]")
        print(f"Testing {len(texts)} texts, {num_runs} runs each")
        
        encrypt_times = []
        decrypt_times = []
        
        for i in range(num_runs):
            # Encryption
            start = time.time()
            ciphertexts = [self.rag_system.encryptor.encrypt(text) for text in texts]
            encrypt_time = time.time() - start
            encrypt_times.append(encrypt_time)
            
            # Decryption
            start = time.time()
            _ = [self.rag_system.encryptor.decrypt(ct) for ct in ciphertexts]
            decrypt_time = time.time() - start
            decrypt_times.append(decrypt_time)
            
            if (i + 1) % 5 == 0:
                print(f"  Run {i+1}/{num_runs}: Encrypt={encrypt_time:.3f}s, Decrypt={decrypt_time:.3f}s")
        
        result = {
            'encrypt_mean': statistics.mean(encrypt_times),
            'decrypt_mean': statistics.mean(decrypt_times),
            'encrypt_throughput': len(texts) / statistics.mean(encrypt_times),
            'decrypt_throughput': len(texts) / statistics.mean(decrypt_times)
        }
        
        print(f"\nResults:")
        print(f"  Encryption mean: {result['encrypt_mean']:.3f}s")
        print(f"  Decryption mean: {result['decrypt_mean']:.3f}s")
        print(f"  Encryption throughput: {result['encrypt_throughput']:.1f} texts/s")
        print(f"  Decryption throughput: {result['decrypt_throughput']:.1f} texts/s")
        
        self.results['encryption'] = result
        return result
    
    def benchmark_end_to_end(self, questions: List[str], num_runs: int = 5) -> Dict[str, Any]:
        """Benchmark end-to-end query processing."""
        print("\n[End-to-End Query Benchmark]")
        print(f"Testing {len(questions)} questions, {num_runs} runs each")
        
        all_times = []
        retrieval_times = []
        generation_times = []
        
        for i in range(num_runs):
            run_times = []
            run_retrieval = []
            run_generation = []
            
            for q_idx, question in enumerate(questions):
                start = time.time()
                result = self.rag_system.query(question, top_k=5)
                elapsed = time.time() - start
                
                if result['success']:
                    run_times.append(elapsed)
                    run_generation.append(result['generation_time'])
                    run_retrieval.append(elapsed - result['generation_time'])
                
                print(f"  Run {i+1}/{num_runs}, Q{q_idx+1}: {elapsed:.2f}s")
            
            all_times.extend(run_times)
            retrieval_times.extend(run_retrieval)
            generation_times.extend(run_generation)
        
        if all_times:
            result = {
                'total_mean': statistics.mean(all_times),
                'total_median': statistics.median(all_times),
                'retrieval_mean': statistics.mean(retrieval_times),
                'generation_mean': statistics.mean(generation_times),
                'total_stdev': statistics.stdev(all_times) if len(all_times) > 1 else 0
            }
            
            print(f"\nResults:")
            print(f"  Total mean: {result['total_mean']:.3f}s")
            print(f"  Total median: {result['total_median']:.3f}s")
            print(f"  Retrieval mean: {result['retrieval_mean']:.3f}s")
            print(f"  Generation mean: {result['generation_mean']:.3f}s")
            print(f"  Total std dev: {result['total_stdev']:.3f}s")
            
            self.results['end_to_end'] = result
            return result
        else:
            return {}
    
    def print_summary(self):
        """Print benchmark summary."""
        print("\n" + "=" * 60)
        print("BENCHMARK SUMMARY")
        print("=" * 60)
        
        if 'embedding' in self.results:
            print("\nEmbedding Performance:")
            print(f"  Average time: {self.results['embedding']['mean']:.3f}s")
        
        if 'encryption' in self.results:
            print("\nEncryption Performance:")
            print(f"  Encrypt throughput: {self.results['encryption']['encrypt_throughput']:.1f} texts/s")
            print(f"  Decrypt throughput: {self.results['encryption']['decrypt_throughput']:.1f} texts/s")
        
        if 'end_to_end' in self.results:
            print("\nEnd-to-End Performance:")
            print(f"  Average response: {self.results['end_to_end']['total_mean']:.3f}s")
            print(f"  - Retrieval: {self.results['end_to_end']['retrieval_mean']:.3f}s")
            print(f"  - Generation: {self.results['end_to_end']['generation_mean']:.3f}s")
        
        print("\n" + "=" * 60)


def main():
    """Run benchmarks."""
    print("=" * 60)
    print("Privacy-Preserving RAG System - Benchmarks")
    print("=" * 60)
    
    # Initialize system
    print("\nInitializing RAG system...")
    key = generate_key()
    
    try:
        rag_system = RAGSystem(
            encryption_key=key,
            embedding_model_name="sentence-transformers/all-MiniLM-L6-v2",
            llm_model_name="llama3.2:3b",
            enable_audit=False  # Disable audit for benchmarking
        )
        print("✓ System initialized")
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        print("\nPlease ensure:")
        print("- Qdrant is running")
        print("- Ollama is running with llama3.2:3b")
        return 1
    
    # Create sample data
    print("\nCreating sample data...")
    sample_texts = [
        "This is a test document about privacy protection.",
        "Encryption is essential for data security.",
        "RAG systems combine retrieval and generation.",
        "Lightweight models are efficient for local deployment.",
        "Vector databases enable semantic search."
    ] * 10  # 50 texts total
    
    sample_questions = [
        "What is privacy protection?",
        "How does encryption work?",
        "What are RAG systems?"
    ]
    
    # Create benchmark suite
    benchmark = Benchmark(rag_system)
    
    # Run benchmarks
    try:
        print("\n" + "=" * 60)
        print("Starting benchmarks...")
        print("=" * 60)
        
        # Embedding benchmark
        benchmark.benchmark_embedding(sample_texts[:10], num_runs=10)
        
        # Encryption benchmark
        benchmark.benchmark_encryption(sample_texts[:10], num_runs=10)
        
        # Ingest sample document for end-to-end test
        print("\n[Setup] Ingesting sample document...")
        base_dir = Path(__file__).parent.parent
        sample_doc = base_dir / "data" / "documents" / "benchmark_sample.txt"
        sample_doc.parent.mkdir(parents=True, exist_ok=True)
        
        with open(sample_doc, 'w', encoding='utf-8') as f:
            f.write("\n\n".join(sample_texts))
        
        success = rag_system.ingest_document(str(sample_doc))
        if success:
            print("✓ Sample document ingested")
            
            # End-to-end benchmark
            benchmark.benchmark_end_to_end(sample_questions, num_runs=3)
        else:
            print("✗ Failed to ingest sample document")
        
        # Print summary
        benchmark.print_summary()
        
        print("\n✓ Benchmarks completed successfully!")
        return 0
        
    except KeyboardInterrupt:
        print("\n\nBenchmark interrupted by user")
        return 1
    except Exception as e:
        print(f"\n✗ Benchmark failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
