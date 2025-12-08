"""Streamlit web interface for Privacy-Preserving RAG System."""
import streamlit as st
import sys
from pathlib import Path
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.rag_pipeline import RAGSystem
from src.encryption import generate_key, save_key, load_key
from config import config


# Page configuration
st.set_page_config(
    page_title="Privacy-Preserving RAG System",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def init_rag_system():
    """Initialize RAG system (cached)."""
    base_dir = Path(__file__).parent.parent.parent
    key_file = base_dir / "config" / "encryption.key"
    
    # Load or generate encryption key
    if key_file.exists():
        key = load_key(key_file)
    else:
        key = generate_key()
        save_key(key, key_file)
        st.info("Generated new encryption key")
    
    # Load configuration
    cfg = config.load_config()
    
    # Initialize RAG system
    rag_system = RAGSystem(
        encryption_key=key,
        embedding_model_name=cfg['embedding']['model_name'],
        llm_model_name=cfg['llm']['model_name'],
        vector_db_config=cfg['vector_db'],
        enable_audit=cfg['audit']['enable']
    )
    
    return rag_system


def main():
    """Main application."""
    st.markdown('<div class="main-header">🔒 Privacy-Preserving RAG System</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📋 System Configuration")
        
        # Initialize system
        try:
            rag_system = init_rag_system()
            st.success("✅ System Initialized")
        except Exception as e:
            st.error(f"❌ Initialization Failed: {e}")
            st.stop()
        
        # System stats
        st.subheader("📊 System Statistics")
        stats = rag_system.get_stats()
        
        st.metric("Vector Count", stats['vector_count'])
        st.metric("Embedding Dimension", stats['embedding_dimension'])
        st.info(f"**LLM Model:** {stats['llm_model']}")
        st.info(f"**Embedding Model:** {stats['embedding_model'][:40]}...")
        
        st.divider()
        
        # Configuration
        st.subheader("⚙️ Query Settings")
        top_k = st.slider("Top-K Results", 1, 10, 5)
        show_context = st.checkbox("Show Retrieved Context", value=False)
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Query", "📁 Document Management", "📈 System Info", "📖 About"])
    
    # Tab 1: Query Interface
    with tab1:
        st.header("Ask Questions")
        st.write("Enter your question below to query the knowledge base.")
        
        question = st.text_area(
            "Your Question:",
            placeholder="Enter your question here...",
            height=100
        )
        
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            query_button = st.button("🔍 Search", type="primary", use_container_width=True)
        with col2:
            clear_button = st.button("🗑️ Clear", use_container_width=True)
        
        if clear_button:
            st.rerun()
        
        if query_button and question:
            with st.spinner("Processing query..."):
                start_time = time.time()
                result = rag_system.query(
                    question=question,
                    top_k=top_k,
                    return_context=show_context
                )
                
                if result['success']:
                    st.markdown('<div class="success-box">', unsafe_allow_html=True)
                    st.subheader("📝 Answer")
                    st.write(result['answer'])
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Response Time", f"{result['response_time']:.2f}s")
                    with col2:
                        st.metric("Generation Time", f"{result['generation_time']:.2f}s")
                    with col3:
                        st.metric("Chunks Retrieved", result['num_chunks_retrieved'])
                    
                    # Show context if requested
                    if show_context and 'context' in result:
                        st.divider()
                        st.subheader("📚 Retrieved Context")
                        for idx, chunk in enumerate(result['context'], 1):
                            with st.expander(f"Chunk {idx} (Score: {chunk['score']:.4f})"):
                                st.write(chunk['text'])
                                st.caption(f"Source: {chunk['metadata'].get('source', 'unknown')}")
                else:
                    st.markdown('<div class="error-box">', unsafe_allow_html=True)
                    st.error(f"❌ {result['answer']}")
                    st.markdown('</div>', unsafe_allow_html=True)
        elif query_button:
            st.warning("Please enter a question.")
    
    # Tab 2: Document Management
    with tab2:
        st.header("Document Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📤 Upload Documents")
            uploaded_files = st.file_uploader(
                "Choose files",
                accept_multiple_files=True,
                type=['pdf', 'txt', 'docx']
            )
            
            if st.button("Upload & Process", type="primary", use_container_width=True):
                if uploaded_files:
                    base_dir = Path(__file__).parent.parent.parent
                    upload_dir = base_dir / "data" / "documents"
                    upload_dir.mkdir(parents=True, exist_ok=True)
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    results = {}
                    for idx, uploaded_file in enumerate(uploaded_files):
                        status_text.text(f"Processing {uploaded_file.name}...")
                        
                        # Save file
                        file_path = upload_dir / uploaded_file.name
                        with open(file_path, 'wb') as f:
                            f.write(uploaded_file.getbuffer())
                        
                        # Ingest
                        success = rag_system.ingest_document(str(file_path))
                        results[uploaded_file.name] = success
                        
                        progress_bar.progress((idx + 1) / len(uploaded_files))
                    
                    status_text.text("Done!")
                    
                    # Show results
                    st.divider()
                    st.subheader("📊 Upload Results")
                    for filename, success in results.items():
                        if success:
                            st.success(f"✅ {filename}")
                        else:
                            st.error(f"❌ {filename}")
                    
                    # Clear cache to refresh stats
                    st.cache_resource.clear()
                    st.rerun()
                else:
                    st.warning("Please select files to upload.")
        
        with col2:
            st.subheader("📊 Current Documents")
            vector_count = rag_system.get_stats()['vector_count']
            
            if vector_count > 0:
                st.info(f"**Total Chunks in Database:** {vector_count}")
                st.write("Documents are stored as encrypted chunks in the vector database.")
            else:
                st.warning("No documents uploaded yet.")
    
    # Tab 3: System Information
    with tab3:
        st.header("System Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔒 Privacy Features")
            features = [
                "✅ AES-256-GCM Encryption",
                "✅ Local Vector Storage",
                "✅ Local LLM Inference",
                "✅ No Data Transmission",
                "✅ Audit Logging",
                "✅ Integrity Verification"
            ]
            for feature in features:
                st.write(feature)
        
        with col2:
            st.subheader("⚙️ Technical Details")
            cfg = config.load_config()
            
            st.write("**Embedding Model:**")
            st.code(cfg['embedding']['model_name'])
            
            st.write("**LLM Model:**")
            st.code(cfg['llm']['model_name'])
            
            st.write("**Vector Database:**")
            st.code(f"{cfg['vector_db']['type']} ({cfg['vector_db']['host']}:{cfg['vector_db']['port']})")
            
            st.write("**Encryption:**")
            st.code(f"{cfg['encryption']['algorithm']}-{cfg['encryption']['key_size']}")
    
    # Tab 4: About
    with tab4:
        st.header("About This System")
        
        st.markdown("""
        ### 🎓 Privacy-Preserving Lightweight RAG System
        
        This system is designed for **local deployment** with **end-to-end privacy protection**.
        
        #### Key Features:
        
        1. **Privacy Protection**
           - All documents are encrypted using AES-256-GCM before storage
           - Only encrypted text is stored in the vector database
           - Decryption happens only during query processing
           - All processing is done locally - no data leaves your machine
        
        2. **Lightweight Design**
           - Uses compact embedding models (all-MiniLM-L6-v2, 384 dimensions)
           - Supports quantized LLMs (4-bit quantization)
           - Optimized for resource-constrained environments
        
        3. **Complete RAG Pipeline**
           - Document parsing (PDF, TXT, DOCX)
           - Intelligent text chunking
           - Vector similarity search
           - Context-aware answer generation
        
        4. **Audit & Compliance**
           - Comprehensive audit logging
           - No sensitive data in logs
           - Integrity verification
           - Full operation traceability
        
        #### System Architecture:
        
        ```
        User Query
            ↓
        Embedding Model → Vector Search
            ↓
        Retrieve Encrypted Chunks
            ↓
        Decrypt Locally
            ↓
        Local LLM Generation
            ↓
        Answer
        ```
        
        #### Technology Stack:
        - **Embedding**: Sentence Transformers
        - **Vector DB**: Qdrant
        - **LLM**: Ollama (Local)
        - **Encryption**: AES-GCM
        - **Web UI**: Streamlit
        
        ---
        
        **Graduation Project**: Privacy-Preserving RAG System Design and Development
        
        © 2024 - All rights reserved
        """)


if __name__ == "__main__":
    main()
