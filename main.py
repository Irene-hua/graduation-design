# python
"""
Main entry point for Privacy-Enhanced Lightweight RAG System
隐私增强轻量级RAG系统主入口
"""

import argparse
import sys
from pathlib import Path
from typing import Any, Dict

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.rag_system import PrivacyEnhancedRAG


def normalize_collection_info(info: Any) -> Dict[str, Any]:
    """将 qdrant 返回的 CollectionInfo\ 或 dict\ 或普通对象 归一化为简单 dict"""
    data = None
    # pydantic model 有 .dict()
    try:
        if hasattr(info, "dict"):
            data = info.dict()
    except Exception:
        data = None
    # 普通对象或 dataclass
    if data is None:
        try:
            if hasattr(info, "__dict__"):
                data = dict(info.__dict__)
        except Exception:
            data = None
    # 已经是 dict
    if data is None and isinstance(info, dict):
        data = info
    if data is None:
        # 尝试 vars()
        try:
            data = dict(vars(info))
        except Exception:
            data = {}

    # 常见字段名映射与回退
    def pick(*keys):
        for k in keys:
            if isinstance(data, dict) and k in data and data[k] is not None:
                return data[k]
        # 也尝试属性访问
        for k in keys:
            if hasattr(info, k):
                try:
                    val = getattr(info, k)
                    if val is not None:
                        return val
                except Exception:
                    pass
        return None

    name = pick("name", "collection_name")
    points_count = pick("points_count", "points", "num_points", "size", "vectors_count")
    vectors_count = pick("vectors_count", "vectors", "num_vectors")

    status = pick("status", "collection_status")

    # 若 points_count 是 dict（不同版本可能嵌套），尝试抽取 count
    if isinstance(points_count, dict) and "count" in points_count:
        points_count = points_count["count"]

    if isinstance(vectors_count, dict) and "count" in vectors_count:
        vectors_count = vectors_count["count"]

    # 确保为 int 或 None
    try:
        points_count = int(points_count) if points_count is not None else None
    except Exception:
        points_count = None
    try:
        vectors_count = int(vectors_count) if vectors_count is not None else None
    except Exception:
        vectors_count = None

    return {
        "name": name or "unknown",
        "points_count": points_count,
        "vectors_count": vectors_count,
        "status": status or "unknown",
        "_raw": data,  # 保留原始数据，便于调试
    }


def main():
    parser = argparse.ArgumentParser(
        description='Privacy-Enhanced Lightweight RAG System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Ingest a document
  python main.py ingest --file path/to/document.pdf

  # Query the system
  python main.py query --question "What is the main topic?"

  # Get collection info
  python main.py info

  # Interactive mode
  python main.py interactive
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Ingest command
    ingest_parser = subparsers.add_parser('ingest', help='Ingest a document')
    ingest_parser.add_argument('--file', '-f', required=True, help='Path to document file')
    ingest_parser.add_argument('--config', '-c', default='config/config.yaml',
                              help='Path to configuration file')

    # Query command
    query_parser = subparsers.add_parser('query', help='Query the RAG system')
    query_parser.add_argument('--question', '-q', required=True, help='Question to ask')
    query_parser.add_argument('--top-k', '-k', type=int, help='Number of documents to retrieve')
    query_parser.add_argument('--config', '-c', default='config/config.yaml',
                              help='Path to configuration file')

    # Info command
    info_parser = subparsers.add_parser('info', help='Get collection information')
    info_parser.add_argument('--config', '-c', default='config/config.yaml',
                             help='Path to configuration file')

    # Interactive command
    interactive_parser = subparsers.add_parser('interactive', help='Interactive query mode')
    interactive_parser.add_argument('--config', '-c', default='config/config.yaml',
                                  help='Path to configuration file')

    # Check command
    check_parser = subparsers.add_parser('check', help='Check system components')
    check_parser.add_argument('--config', '-c', default='config/config.yaml',
                            help='Path to configuration file')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        # Initialize RAG system
        print("Initializing Privacy-Enhanced RAG System...")
        rag = PrivacyEnhancedRAG(config_path=args.config)
        print("✓ System initialized successfully\n")

        if args.command == 'ingest':
            ingest_document(rag, args.file)

        elif args.command == 'query':
            query_system(rag, args.question, args.top_k)

        elif args.command == 'info':
            show_info(rag)

        elif args.command == 'interactive':
            interactive_mode(rag)

        elif args.command == 'check':
            check_system(rag)

    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


def ingest_document(rag: PrivacyEnhancedRAG, file_path: str):
    """Ingest a document"""
    print(f"Ingesting document: {file_path}")

    result = rag.ingest_document(file_path)

    print(f"\n✓ Document ingested successfully!")
    print(f"  File: {result['file_name']}")
    print(f"  Chunks created: {result['num_chunks']}")
    print(f"  Document IDs: {len(result['document_ids'])}")


def query_system(rag: PrivacyEnhancedRAG, question: str, top_k: int = None):
    """Query the RAG system"""
    print(f"Question: {question}\n")
    print("Processing query...")

    result = rag.query(question, top_k=top_k)

    print(f"\n{'='*80}")
    print("ANSWER:")
    print(f"{'='*80}")
    print(result['answer'])
    print(f"{'='*80}\n")

    print("Metadata:")
    print(f"  Retrieved chunks: {result['retrieved_chunks']}")
    print(f"  Sources: {', '.join(set(result['sources']))}")
    print(f"  Retrieval time: {result['retrieval_time']:.3f}s")
    print(f"  Generation time: {result['generation_time']:.3f}s")
    print(f"  Total time: {result['total_time']:.3f}s")


def show_info(rag: PrivacyEnhancedRAG):
    """Show collection information (兼容多种 qdrant 返回格式)"""
    info = rag.get_collection_info()
    norm = normalize_collection_info(info)

    print("Collection Information:")
    print(f"  Name: {norm['name']}")
    print(f"  Points count: {norm['points_count'] if norm['points_count'] is not None else 'N/A'}")
    print(f"  Vectors count: {norm['vectors_count'] if norm['vectors_count'] is not None else 'N/A'}")
    print(f"  Status: {norm['status']}")
    # 若需要调试原始结构，解除下面注释
    # import pprint; pprint.pprint(norm['_raw'])


def interactive_mode(rag: PrivacyEnhancedRAG):
    """Interactive query mode"""
    print("=" * 80)
    print("Interactive Query Mode")
    print("=" * 80)
    print("Enter your questions (type 'exit' or 'quit' to stop)\n")

    while True:
        try:
            question = input("\n🤔 Question: ").strip()

            if question.lower() in ['exit', 'quit', 'q']:
                print("\nGoodbye!")
                break

            if not question:
                continue

            print("\n⏳ Processing...")
            result = rag.query(question)

            print(f"\n{'─'*80}")
            print("💡 Answer:")
            print(f"{'─'*80}")
            print(result['answer'])
            print(f"{'─'*80}")
            print(f"⏱️  Time: {result['total_time']:.3f}s | "
                  f"📚 Sources: {len(set(result['sources']))}")

        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n✗ Error: {e}")


def check_system(rag: PrivacyEnhancedRAG):
    """Check system components (使用归一化后的集合信息)"""
    print("Checking system components...\n")

    # Check LLM connection
    print("1. LLM Server (Ollama):")
    try:
        if rag.check_llm_connection():
            print("   ✓ Connected")
            try:
                models = rag.llm_client.list_models()
                if models:
                    print(f"   Available models: {', '.join(models[:5])}")
            except Exception:
                pass
        else:
            print("   ✗ Not connected")
            print("   Please ensure Ollama is running: ollama serve")
    except Exception as e:
        print(f"   ✗ Error checking LLM: {e}")

    # Check vector store
    print("\n2. Vector Store:")
    try:
        info = rag.get_collection_info()
        norm = normalize_collection_info(info)
        print(f"   ✓ Collection '{norm['name']}' ready")
        pc = norm['points_count']
        vc = norm['vectors_count']
        if pc is not None:
            print(f"   Documents: {pc}")
        else:
            print("   Documents: N/A (collection info missing points_count)")
        if vc is not None:
            print(f"   Vectors: {vc}")
        else:
            print("   Vectors: N/A (collection info missing vectors_count)")
        # 若需要查看原始结构，取消下面注释
        # import pprint; pprint.pprint(norm['_raw'])
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # Check encryption
    print("\n3. Encryption:")
    try:
        test_text = "Test encryption"
        encrypted = rag.encryption_manager.encrypt_to_base64(test_text)
        decrypted = rag.encryption_manager.decrypt_from_base64(encrypted)
        if decrypted == test_text:
            print("   ✓ Encryption/decryption working")
        else:
            print("   ✗ Encryption/decryption failed")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # Check embedding model
    print("\n4. Embedding Model:")
    try:
        embedding = rag.embedding_model.encode_single("Test")
        print(f"   ✓ Model loaded (dimension: {len(embedding)})")
    except Exception as e:
        print(f"   ✗ Error: {e}")


if __name__ == '__main__':
    main()