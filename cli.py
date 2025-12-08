#!/usr/bin/env python3
"""Command-line interface for Privacy-Preserving RAG System."""
import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.rag_pipeline import RAGSystem
from src.encryption import generate_key, save_key, load_key


def setup_key(args):
    """Setup encryption key."""
    key_file = Path(args.key_file)
    
    if key_file.exists() and not args.force:
        print(f"Error: Key file already exists at {key_file}")
        print("Use --force to overwrite")
        return 1
    
    key = generate_key()
    save_key(key, key_file)
    print(f"Encryption key saved to {key_file}")
    return 0


def ingest_documents(args):
    """Ingest documents into the system."""
    key_file = Path(args.key_file)
    
    if not key_file.exists():
        print(f"Error: Key file not found at {key_file}")
        print("Run 'python cli.py setup-key' first")
        return 1
    
    key = load_key(key_file)
    
    print("Initializing RAG system...")
    rag_system = RAGSystem(
        encryption_key=key,
        embedding_model_name=args.embedding_model,
        llm_model_name=args.llm_model
    )
    
    # Ingest documents
    if Path(args.input).is_dir():
        print(f"Ingesting documents from directory: {args.input}")
        results = rag_system.ingest_directory(args.input)
        
        # Print results
        success_count = sum(1 for v in results.values() if v)
        print(f"\nIngested {success_count}/{len(results)} documents successfully")
        
        if args.verbose:
            for filename, success in results.items():
                status = "✓" if success else "✗"
                print(f"  {status} {filename}")
    else:
        print(f"Ingesting document: {args.input}")
        success = rag_system.ingest_document(args.input)
        
        if success:
            print("✓ Document ingested successfully")
        else:
            print("✗ Document ingestion failed")
            return 1
    
    # Show stats
    stats = rag_system.get_stats()
    print(f"\nSystem statistics:")
    print(f"  Vector count: {stats['vector_count']}")
    
    return 0


def query_system(args):
    """Query the RAG system."""
    key_file = Path(args.key_file)
    
    if not key_file.exists():
        print(f"Error: Key file not found at {key_file}")
        return 1
    
    key = load_key(key_file)
    
    print("Initializing RAG system...")
    rag_system = RAGSystem(
        encryption_key=key,
        embedding_model_name=args.embedding_model,
        llm_model_name=args.llm_model
    )
    
    # Get query
    if args.query:
        questions = [args.query]
    else:
        # Interactive mode
        print("\nInteractive query mode (Ctrl+C to exit)")
        questions = []
        while True:
            try:
                q = input("\nQuestion: ").strip()
                if q:
                    questions.append(q)
                else:
                    break
            except (KeyboardInterrupt, EOFError):
                break
    
    # Process queries
    for question in questions:
        print(f"\nQuestion: {question}")
        print("Processing...")
        
        result = rag_system.query(
            question=question,
            top_k=args.top_k,
            return_context=args.show_context
        )
        
        if result['success']:
            print(f"\nAnswer: {result['answer']}")
            print(f"\nMetrics:")
            print(f"  Response time: {result['response_time']:.2f}s")
            print(f"  Generation time: {result['generation_time']:.2f}s")
            print(f"  Chunks retrieved: {result['num_chunks_retrieved']}")
            
            if args.show_context and 'context' in result:
                print(f"\nRetrieved Context:")
                for idx, chunk in enumerate(result['context'], 1):
                    print(f"\n[{idx}] (Score: {chunk['score']:.4f})")
                    print(chunk['text'][:200] + "...")
        else:
            print(f"Error: {result['answer']}")
    
    return 0


def show_stats(args):
    """Show system statistics."""
    key_file = Path(args.key_file)
    
    if not key_file.exists():
        print(f"Error: Key file not found at {key_file}")
        return 1
    
    key = load_key(key_file)
    
    print("Initializing RAG system...")
    rag_system = RAGSystem(
        encryption_key=key,
        embedding_model_name=args.embedding_model,
        llm_model_name=args.llm_model
    )
    
    stats = rag_system.get_stats()
    
    print("\nSystem Statistics:")
    print("=" * 50)
    print(f"Vector count: {stats['vector_count']}")
    print(f"Embedding dimension: {stats['embedding_dimension']}")
    print(f"Embedding model: {stats['embedding_model']}")
    print(f"LLM model: {stats['llm_model']}")
    print("=" * 50)
    
    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Privacy-Preserving RAG System CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Setup key command
    setup_parser = subparsers.add_parser('setup-key', help='Generate encryption key')
    setup_parser.add_argument(
        '--key-file',
        default='config/encryption.key',
        help='Path to key file (default: config/encryption.key)'
    )
    setup_parser.add_argument(
        '--force',
        action='store_true',
        help='Overwrite existing key file'
    )
    
    # Ingest command
    ingest_parser = subparsers.add_parser('ingest', help='Ingest documents')
    ingest_parser.add_argument(
        'input',
        help='Path to document or directory'
    )
    ingest_parser.add_argument(
        '--key-file',
        default='config/encryption.key',
        help='Path to key file'
    )
    ingest_parser.add_argument(
        '--embedding-model',
        default='sentence-transformers/all-MiniLM-L6-v2',
        help='Embedding model name'
    )
    ingest_parser.add_argument(
        '--llm-model',
        default='llama3.2:3b',
        help='LLM model name'
    )
    ingest_parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    # Query command
    query_parser = subparsers.add_parser('query', help='Query the system')
    query_parser.add_argument(
        '-q', '--query',
        help='Query text (interactive mode if not provided)'
    )
    query_parser.add_argument(
        '--key-file',
        default='config/encryption.key',
        help='Path to key file'
    )
    query_parser.add_argument(
        '--embedding-model',
        default='sentence-transformers/all-MiniLM-L6-v2',
        help='Embedding model name'
    )
    query_parser.add_argument(
        '--llm-model',
        default='llama3.2:3b',
        help='LLM model name'
    )
    query_parser.add_argument(
        '--top-k',
        type=int,
        default=5,
        help='Number of chunks to retrieve'
    )
    query_parser.add_argument(
        '--show-context',
        action='store_true',
        help='Show retrieved context'
    )
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show system statistics')
    stats_parser.add_argument(
        '--key-file',
        default='config/encryption.key',
        help='Path to key file'
    )
    stats_parser.add_argument(
        '--embedding-model',
        default='sentence-transformers/all-MiniLM-L6-v2',
        help='Embedding model name'
    )
    stats_parser.add_argument(
        '--llm-model',
        default='llama3.2:3b',
        help='LLM model name'
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Route to appropriate function
    if args.command == 'setup-key':
        return setup_key(args)
    elif args.command == 'ingest':
        return ingest_documents(args)
    elif args.command == 'query':
        return query_system(args)
    elif args.command == 'stats':
        return show_stats(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
