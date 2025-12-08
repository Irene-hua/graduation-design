"""
Main entry point for Privacy-Enhanced Lightweight RAG System
隐私增强轻量级RAG系统主入口
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.rag_system import PrivacyEnhancedRAG


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
    """Show collection information"""
    info = rag.get_collection_info()
    
    print("Collection Information:")
    print(f"  Name: {info['name']}")
    print(f"  Points count: {info['points_count']}")
    print(f"  Vectors count: {info['vectors_count']}")
    print(f"  Status: {info['status']}")


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
    """Check system components"""
    print("Checking system components...\n")
    
    # Check LLM connection
    print("1. LLM Server (Ollama):")
    if rag.check_llm_connection():
        print("   ✓ Connected")
        models = rag.llm_client.list_models()
        if models:
            print(f"   Available models: {', '.join(models[:5])}")
    else:
        print("   ✗ Not connected")
        print("   Please ensure Ollama is running: ollama serve")
    
    # Check vector store
    print("\n2. Vector Store:")
    try:
        info = rag.get_collection_info()
        print(f"   ✓ Collection '{info['name']}' ready")
        print(f"   Documents: {info['points_count']}")
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
