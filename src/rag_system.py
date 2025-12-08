"""
Main RAG System integrating all components
主RAG系统，集成所有组件
"""

import time
import uuid
from typing import List, Dict, Any, Optional
from pathlib import Path

from .encryption import EncryptionManager, KeyManager
from .retrieval import EmbeddingModel, VectorStore
from .generation import LLMClient
from .audit import AuditLogger
from .utils import ConfigLoader, DocumentProcessor


class PrivacyEnhancedRAG:
    """Privacy-Enhanced Lightweight RAG System"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize the RAG system
        
        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        self.config = ConfigLoader(config_path)
        
        # Initialize audit logger
        audit_config = self.config.get_section('audit')
        self.audit_logger = AuditLogger(
            log_dir=audit_config.get('log_dir', 'logs'),
            log_level=audit_config.get('log_level', 'INFO'),
            include_query_metadata=audit_config.get('include_query_metadata', True),
            exclude_sensitive_data=audit_config.get('exclude_sensitive_data', True),
            integrity_check=audit_config.get('integrity_check', True)
        )
        
        # Initialize encryption
        enc_config = self.config.get_section('encryption')
        self.encryption_manager = EncryptionManager(
            key_file=enc_config.get('key_file', 'config/encryption.key')
        )
        
        # Initialize embedding model
        emb_config = self.config.get_section('embedding')
        self.embedding_model = EmbeddingModel(
            model_name=emb_config.get('model_name', 'sentence-transformers/all-MiniLM-L6-v2'),
            device=emb_config.get('device', 'cpu'),
            max_seq_length=emb_config.get('max_seq_length', 256)
        )
        
        # Initialize vector store
        vdb_config = self.config.get_section('vector_db')
        self.vector_store = VectorStore(
            collection_name=vdb_config.get('collection_name', 'private_documents'),
            path=vdb_config.get('storage_path', 'data/vector_db'),
            vector_size=self.embedding_model.get_embedding_dimension(),
            distance=getattr(__import__('qdrant_client.models', fromlist=['Distance']), 
                           vdb_config.get('distance', 'COSINE'))
        )
        
        # Initialize LLM client
        llm_config = self.config.get_section('llm')
        self.llm_client = LLMClient(
            base_url=llm_config.get('base_url', 'http://localhost:11434'),
            model_name=llm_config.get('model_name', 'llama2:7b'),
            temperature=llm_config.get('temperature', 0.7),
            max_tokens=llm_config.get('max_tokens', 512),
            top_p=llm_config.get('top_p', 0.9)
        )
        
        # Initialize document processor
        doc_config = self.config.get_section('document_processing')
        self.document_processor = DocumentProcessor(
            chunk_size=doc_config.get('chunk_size', 500),
            chunk_overlap=doc_config.get('chunk_overlap', 50)
        )
        
        # Get retrieval configuration
        self.retrieval_config = self.config.get_section('retrieval')
        
        self.audit_logger.log_system_event(
            'system_initialization',
            {'status': 'success', 'components': 'all'}
        )
    
    def ingest_document(self, file_path: str) -> Dict[str, Any]:
        """
        Ingest a document into the system
        
        Args:
            file_path: Path to the document file
        
        Returns:
            dict: Ingestion result with statistics
        """
        try:
            # Process document
            chunks = self.document_processor.process_document(file_path)
            
            if not chunks:
                raise ValueError("No chunks created from document")
            
            # Extract texts
            texts = [chunk['text'] for chunk in chunks]
            
            # Generate embeddings
            embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
            
            # Encrypt texts
            encrypted_data = []
            nonces = []
            
            for text in texts:
                encrypted_base64 = self.encryption_manager.encrypt_to_base64(text)
                encrypted_data.append(encrypted_base64)
                nonces.append('')  # Nonce is included in base64 encoding
            
            # Log encryption operation
            self.audit_logger.log_encryption_operation(
                operation='encrypt',
                num_items=len(texts),
                success=True
            )
            
            # Prepare metadata
            metadata = [
                {
                    'source': chunk['source'],
                    'chunk_id': chunk['id'],
                    'file_path': chunk['file_path']
                }
                for chunk in chunks
            ]
            
            # Store in vector database
            doc_ids = self.vector_store.add_documents(
                embeddings=embeddings,
                encrypted_texts=encrypted_data,
                nonces=nonces,
                metadata=metadata
            )
            
            # Log successful ingestion
            file_name = Path(file_path).name
            self.audit_logger.log_document_ingestion(
                file_name=file_name,
                num_chunks=len(chunks),
                success=True
            )
            
            return {
                'status': 'success',
                'file_name': file_name,
                'num_chunks': len(chunks),
                'document_ids': doc_ids
            }
        
        except Exception as e:
            # Log failed ingestion
            file_name = Path(file_path).name if file_path else 'unknown'
            self.audit_logger.log_document_ingestion(
                file_name=file_name,
                num_chunks=0,
                success=False,
                error=str(e)
            )
            raise
    
    def query(self, question: str, top_k: int = None) -> Dict[str, Any]:
        """
        Query the RAG system
        
        Args:
            question: User question
            top_k: Number of documents to retrieve (uses config default if None)
        
        Returns:
            dict: Response with answer and metadata
        """
        query_id = str(uuid.uuid4())
        
        if top_k is None:
            top_k = self.retrieval_config.get('top_k', 3)
        
        score_threshold = self.retrieval_config.get('score_threshold', 0.5)
        
        try:
            # Phase 1: Retrieval
            retrieval_start = time.time()
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode_single(question)
            
            # Search vector store
            search_results = self.vector_store.search(
                query_embedding=query_embedding,
                top_k=top_k,
                score_threshold=score_threshold
            )
            
            # Decrypt retrieved texts
            decrypted_chunks = []
            for result in search_results:
                try:
                    decrypted_text = self.encryption_manager.decrypt_from_base64(
                        result['encrypted_text']
                    )
                    decrypted_chunks.append({
                        'text': decrypted_text,
                        'score': result['score'],
                        'metadata': result['metadata']
                    })
                except Exception as e:
                    self.audit_logger.log_system_event(
                        'decryption_error',
                        {'error': str(e)},
                        level='ERROR'
                    )
            
            retrieval_time = time.time() - retrieval_start
            
            # Log decryption operation
            self.audit_logger.log_encryption_operation(
                operation='decrypt',
                num_items=len(decrypted_chunks),
                success=True
            )
            
            # Phase 2: Generation
            generation_start = time.time()
            
            if not decrypted_chunks:
                answer = "I couldn't find relevant information to answer your question."
            else:
                # Extract context texts
                context_texts = [chunk['text'] for chunk in decrypted_chunks]
                
                # Generate answer
                answer = self.llm_client.generate(
                    prompt=question,
                    context=context_texts
                )
            
            generation_time = time.time() - generation_start
            
            # Log query
            self.audit_logger.log_query(
                query_id=query_id,
                num_results=len(search_results),
                retrieval_time=retrieval_time,
                generation_time=generation_time,
                success=True
            )
            
            return {
                'status': 'success',
                'query_id': query_id,
                'answer': answer,
                'retrieved_chunks': len(search_results),
                'sources': [chunk['metadata'].get('source', 'unknown') 
                          for chunk in decrypted_chunks],
                'retrieval_time': retrieval_time,
                'generation_time': generation_time,
                'total_time': retrieval_time + generation_time
            }
        
        except Exception as e:
            # Log failed query
            self.audit_logger.log_query(
                query_id=query_id,
                num_results=0,
                retrieval_time=0,
                generation_time=0,
                success=False,
                error=str(e)
            )
            raise
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the document collection
        
        Returns:
            dict: Collection information
        """
        return self.vector_store.get_collection_info()
    
    def check_llm_connection(self) -> bool:
        """
        Check if LLM server is accessible
        
        Returns:
            bool: True if accessible
        """
        return self.llm_client.check_connection()
    
    def delete_collection(self) -> None:
        """Delete all documents from the collection"""
        self.vector_store.delete_collection()
        self.audit_logger.log_system_event(
            'collection_deleted',
            {'status': 'success'}
        )
