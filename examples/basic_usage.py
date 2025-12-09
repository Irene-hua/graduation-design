"""
Basic usage example for Privacy-Enhanced RAG System
基本使用示例
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag_system import PrivacyEnhancedRAG


def main():
    print("=" * 80)
    print("Privacy-Enhanced RAG System - Basic Usage Example")
    print("=" * 80)
    
    # Initialize the system
    print("\n1. Initializing RAG system...")
    rag = PrivacyEnhancedRAG(config_path='config/config.yaml')
    print("✓ System initialized")
    
    # Check system components
    print("\n2. Checking system components...")
    if rag.check_llm_connection():
        print("✓ LLM server connected")
    else:
        print("✗ LLM server not connected. Please start Ollama: ollama serve")
        return
    
    # Ingest a sample document
    print("\n3. Ingesting sample document...")
    doc_path = 'data/documents/example.txt'
    
    if not Path(doc_path).exists():
        print(f"✗ Sample document not found: {doc_path}")
        print("Please ensure the example document exists.")
        return
    
    try:
        result = rag.ingest_document(doc_path)
        print(f"✓ Document ingested successfully")
        print(f"  - File: {result['file_name']}")
        print(f"  - Chunks created: {result['num_chunks']}")
    except Exception as e:
        print(f"✗ Error ingesting document: {e}")
        return
    
    # Get collection info
    print("\n4. Collection information:")
    info = rag.get_collection_info()
    print(f"  - Name: {info['name']}")
    print(f"  - Documents: {info['points_count']}")
    
    # Query the system
    print("\n5. Querying the system...")
    questions = [
        "What is the Privacy-Enhanced RAG System?",
        "What encryption method is used?",
        "What are the key features?"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n  Question {i}: {question}")
        try:
            response = rag.query(question, top_k=3)
            print(f"  Answer: {response['answer'][:200]}...")
            print(f"  Time: {response['total_time']:.3f}s")
        except Exception as e:
            print(f"  Error: {e}")
    
    print("\n" + "=" * 80)
    print("Example completed!")
    print("=" * 80)


if __name__ == '__main__':
    main()
