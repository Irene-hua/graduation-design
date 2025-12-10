# python
import os
import sys
import base64
from pathlib import Path

try:
    import yaml
except Exception:
    print("ERROR: missing dependency 'pyyaml'. 安装: python -m pip install pyyaml")
    sys.exit(2)

cfg_path = Path("config") / "config.yaml"
if not cfg_path.exists():
    print("ERROR: config file not found at", str(cfg_path))
    sys.exit(2)

with cfg_path.open("r", encoding="utf-8") as f:
    try:
        cfg = yaml.safe_load(f)
    except Exception as e:
        print("ERROR: failed to parse YAML:", e)
        sys.exit(2)

key_spec = cfg.get("encryption", {}).get("key")
if not key_spec:
    print("WARN: 'encryption.key' not set in", str(cfg_path))
    sys.exit(1)

if isinstance(key_spec, str) and key_spec.startswith("env:"):
    envname = key_spec.split(":", 1)[1]
    b64 = os.getenv(envname)
    if not b64:
        print(f"ERROR: environment variable {envname} not set")
        sys.exit(2)
    try:
        raw = base64.b64decode(b64)
    except Exception as e:
        print("ERROR: environment variable content is not valid base64:", e)
        sys.exit(2)
    if len(raw) != 32:
        print(f"ERROR: decoded key length is {len(raw)} bytes; expected 32")
        sys.exit(2)
    print(f"OK: encryption key loaded from env:{envname} (32 bytes)")
    sys.exit(0)
else:
    print("WARN: encryption.key in config is not an env reference. Current value:", repr(key_spec))
    print("建议使用格式: env:RAG_ENC_KEY 并在环境变量中存放 base64 编码的 32 字节密钥")
    sys.exit(1)
