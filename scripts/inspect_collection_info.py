# python
"""
scripts\inspect_collection_info.py
用于诊断 rag.get_collection_info() 返回对象的结构，帮助定位 'vectors_count' 等字段名。
使用:
  python .\scripts\inspect_collection_info.py
或
  python .\scripts\inspect_collection_info.py --config config\config.yaml
"""

import argparse
import pprint
import sys
from pathlib import Path

# 将项目根加入 sys.path（脚本放在项目根/scripts 下，此处 parents[1] 指项目根）
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:
    from src.rag_system import PrivacyEnhancedRAG
except Exception as e:
    print("无法导入 src.rag_system.PrivacyEnhancedRAG:", e)
    print("请确认文件路径 `src/rag_system.py` 存在，或调整 sys.path。")
    sys.exit(1)


def inspect_info(info):
    print("Type:", type(info))
    print("\n--- dir(info) ---")
    pprint.pprint(dir(info))
    print("\n--- repr(info) ---")
    try:
        print(repr(info))
    except Exception:
        pass

    print("\n--- info.dict() if available ---")
    try:
        if hasattr(info, "dict"):
            pprint.pprint(info.dict())
        else:
            print("no .dict()")
    except Exception as e:
        print("info.dict() failed:", e)

    print("\n--- vars(info) / __dict__ ---")
    try:
        data = getattr(info, "__dict__", None)
        if not data:
            data = vars(info)
        pprint.pprint(data)
    except Exception as e:
        print("vars/info.__dict__ failed:", e)


def main():
    parser = argparse.ArgumentParser(description="Inspect CollectionInfo returned by RAG")
    parser.add_argument("--config", "-c", default="config/config.yaml", help="Path to config file")
    args = parser.parse_args()

    try:
        rag = PrivacyEnhancedRAG(config_path=args.config)
    except Exception as e:
        print("初始化 PrivacyEnhancedRAG 失败:", e)
        sys.exit(1)

    try:
        info = rag.get_collection_info()
    except Exception as e:
        print("调用 rag.get_collection_info() 抛出异常:", e)
        sys.exit(1)

    inspect_info(info)


if __name__ == "__main__":
    main()
