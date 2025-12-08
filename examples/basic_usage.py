"""Basic usage example of the Privacy-Preserving RAG System."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag_pipeline import RAGSystem
from src.encryption import generate_key, save_key, load_key


def main():
    """Main example function."""
    print("=" * 60)
    print("Privacy-Preserving RAG System - Basic Usage Example")
    print("=" * 60)
    
    # 1. Setup encryption key
    print("\n[1] Setting up encryption key...")
    base_dir = Path(__file__).parent.parent
    key_file = base_dir / "config" / "encryption.key"
    
    if key_file.exists():
        print(f"   Loading existing key from {key_file}")
        key = load_key(key_file)
    else:
        print("   Generating new encryption key...")
        key = generate_key()
        save_key(key, key_file)
        print(f"   Key saved to {key_file}")
    
    # 2. Initialize RAG system
    print("\n[2] Initializing RAG system...")
    print("   This may take a moment to load models...")
    
    try:
        rag_system = RAGSystem(
            encryption_key=key,
            embedding_model_name="sentence-transformers/all-MiniLM-L6-v2",
            llm_model_name="llama3.2:3b",
            enable_audit=True
        )
        print("   ✓ System initialized successfully!")
    except Exception as e:
        print(f"   ✗ Initialization failed: {e}")
        print("\n   Please ensure:")
        print("   - Qdrant is running (docker-compose up -d)")
        print("   - Ollama is running with llama3.2:3b model")
        return
    
    # 3. Create sample document
    print("\n[3] Creating sample document...")
    sample_doc_path = base_dir / "data" / "documents" / "sample.txt"
    sample_doc_path.parent.mkdir(parents=True, exist_ok=True)
    
    sample_text = """
Privacy-Preserving RAG System

This is a privacy-preserving RAG (Retrieval-Augmented Generation) system designed for local deployment.

Key Features:
1. End-to-end encryption using AES-256-GCM
2. Lightweight models for efficient processing
3. Local deployment with no data transmission
4. Complete audit logging for compliance

The system uses a lightweight embedding model (all-MiniLM-L6-v2) to generate 384-dimensional vectors.
These vectors are stored in a Qdrant vector database alongside encrypted text chunks.

When a user submits a query, the system:
- Converts the query to a vector
- Retrieves the most similar chunks
- Decrypts the retrieved text
- Generates an answer using a local LLM (Llama 3.2 3B)

All processing happens locally, ensuring complete data privacy and security.
"""
    
    with open(sample_doc_path, 'w', encoding='utf-8') as f:
        f.write(sample_text)
    
    print(f"   Sample document created at {sample_doc_path}")
    
    # 4. Ingest document
    print("\n[4] Ingesting document into the system...")
    print("   This will: parse → chunk → embed → encrypt → store")
    
    success = rag_system.ingest_document(str(sample_doc_path))
    
    if success:
        print("   ✓ Document ingested successfully!")
        
        # Show stats
        stats = rag_system.get_stats()
        print(f"   - Vector count: {stats['vector_count']}")
        print(f"   - Embedding dimension: {stats['embedding_dimension']}")
    else:
        print("   ✗ Document ingestion failed!")
        return
    
    # 5. Query the system
    print("\n[5] Querying the system...")
    
    questions = [
        "What encryption algorithm does the system use?",
        "What is the embedding model dimension?",
        "How does the query process work?"
    ]
    
    for idx, question in enumerate(questions, 1):
        print(f"\n   Question {idx}: {question}")
        print("   Processing query...")
        
        result = rag_system.query(question, top_k=3)
        
        if result['success']:
            print(f"   ✓ Answer: {result['answer']}")
            print(f"   - Response time: {result['response_time']:.2f}s")
            print(f"   - Chunks retrieved: {result['num_chunks_retrieved']}")
        else:
            print(f"   ✗ Query failed: {result['answer']}")
    
    # 6. System statistics
    print("\n[6] System Statistics:")
    stats = rag_system.get_stats()
    for key, value in stats.items():
        print(f"   - {key}: {value}")
    
    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Try the web interface: streamlit run src/web/app.py")
    print("2. Add your own documents to data/documents/")
    print("3. Check the audit logs in logs/audit.log")
    print("=" * 60)


if __name__ == "__main__":
    main()
