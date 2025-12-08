"""Complete RAG system with privacy protection."""
import time
import hashlib
from typing import List, Dict, Any, Optional
from pathlib import Path

from ..document_processor import DocumentParser, TextChunker
from ..encryption import AESEncryption
from ..embedding import EmbeddingModel
from ..vector_db import QdrantDB
from ..llm import OllamaClient
from ..audit import AuditLogger


class RAGSystem:
    """Privacy-preserving RAG system with end-to-end encryption."""
    
    def __init__(
        self,
        encryption_key: bytes,
        embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        llm_model_name: str = "llama3.2:3b",
        vector_db_config: Optional[Dict[str, Any]] = None,
        enable_audit: bool = True
    ):
        """
        Initialize RAG system.
        
        Args:
            encryption_key: AES encryption key
            embedding_model_name: Name of embedding model
            llm_model_name: Name of LLM model
            vector_db_config: Vector database configuration
            enable_audit: Enable audit logging
        """
        # Initialize components
        self.encryptor = AESEncryption(encryption_key)
        self.embedding_model = EmbeddingModel(model_name=embedding_model_name)
        self.llm = OllamaClient(model_name=llm_model_name)
        
        # Vector DB config
        vdb_config = vector_db_config or {}
        self.vector_db = QdrantDB(
            host=vdb_config.get('host', 'localhost'),
            port=vdb_config.get('port', 6333),
            collection_name=vdb_config.get('collection_name', 'encrypted_documents'),
            dimension=self.embedding_model.dimension,
            distance_metric=vdb_config.get('distance_metric', 'cosine')
        )
        
        # Document processing
        self.parser = DocumentParser()
        self.chunker = TextChunker()
        
        # Audit logger
        self.audit_logger = AuditLogger(enable=enable_audit) if enable_audit else None
        
        # Prompt template
        self.prompt_template = """Based on the following context, please answer the question.

Context:
{context}

Question: {question}

Answer:"""
    
    def ingest_document(
        self,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Ingest a document into the system.
        
        Process: Parse → Chunk → Embed → Encrypt → Store
        
        Args:
            file_path: Path to document file
            metadata: Optional metadata
            
        Returns:
            True if successful
        """
        file_path = Path(file_path)
        
        try:
            # 1. Parse document
            text = self.parser.parse(file_path)
            
            # 2. Chunk text
            doc_metadata = metadata or {}
            doc_metadata['source'] = file_path.name
            chunks = self.chunker.chunk_text(text, doc_metadata)
            
            if not chunks:
                return False
            
            # 3. Generate embeddings for original text
            chunk_texts = [chunk['text'] for chunk in chunks]
            embeddings = self.embedding_model.encode(chunk_texts)
            
            # 4. Encrypt the text chunks
            encrypted_texts = [self.encryptor.encrypt(text) for text in chunk_texts]
            
            # 5. Prepare metadata for storage
            storage_metadata = []
            for chunk in chunks:
                meta = chunk['metadata'].copy()
                meta['chunk_id'] = chunk['chunk_id']
                meta['chunk_size'] = chunk['chunk_size']
                storage_metadata.append(meta)
            
            # 6. Store in vector database
            self.vector_db.insert(
                vectors=embeddings,
                encrypted_texts=encrypted_texts,
                metadata=storage_metadata
            )
            
            # Log operation
            if self.audit_logger:
                doc_id = hashlib.sha256(file_path.name.encode()).hexdigest()[:16]
                self.audit_logger.log_document_operation('ingest', doc_id, True)
                self.audit_logger.log_encryption('encrypt', len(chunks))
            
            return True
        
        except Exception as e:
            print(f"Error ingesting document: {e}")
            if self.audit_logger:
                doc_id = hashlib.sha256(file_path.name.encode()).hexdigest()[:16]
                self.audit_logger.log_document_operation('ingest', doc_id, False)
            return False
    
    def ingest_directory(
        self,
        directory_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, bool]:
        """
        Ingest all documents in a directory.
        
        Args:
            directory_path: Path to directory
            metadata: Optional metadata to add to all documents
            
        Returns:
            Dictionary mapping filenames to success status
        """
        directory_path = Path(directory_path)
        results = {}
        
        for file_path in directory_path.iterdir():
            if file_path.is_file():
                extension = file_path.suffix.lower().lstrip('.')
                if extension in self.parser.supported_formats:
                    success = self.ingest_document(str(file_path), metadata)
                    results[file_path.name] = success
        
        return results
    
    def query(
        self,
        question: str,
        top_k: int = 5,
        return_context: bool = False
    ) -> Dict[str, Any]:
        """
        Query the RAG system.
        
        Process: Query → Retrieve → Decrypt → Generate
        
        Args:
            question: User question
            top_k: Number of chunks to retrieve
            return_context: Whether to return retrieved context
            
        Returns:
            Dictionary with answer and metadata
        """
        start_time = time.time()
        
        try:
            # 1. Embed query
            query_embedding = self.embedding_model.encode(question)
            
            # 2. Retrieve similar chunks
            search_results = self.vector_db.search(
                query_vector=query_embedding,
                top_k=top_k
            )
            
            if not search_results:
                return {
                    'answer': 'No relevant information found in the knowledge base.',
                    'success': False,
                    'response_time': time.time() - start_time
                }
            
            # 3. Decrypt retrieved chunks
            decrypted_chunks = []
            for result in search_results:
                encrypted_text = result['encrypted_text']
                decrypted_text = self.encryptor.decrypt(encrypted_text)
                decrypted_chunks.append({
                    'text': decrypted_text,
                    'score': result['score'],
                    'metadata': result['metadata']
                })
            
            # Log retrieval
            if self.audit_logger:
                query_hash = hashlib.sha256(question.encode()).hexdigest()[:16]
                self.audit_logger.log_retrieval(query_hash, len(decrypted_chunks), top_k)
                self.audit_logger.log_encryption('decrypt', len(decrypted_chunks))
            
            # 4. Format context
            context = '\n\n'.join([
                f"[Source: {chunk['metadata'].get('source', 'unknown')}]\n{chunk['text']}"
                for chunk in decrypted_chunks
            ])
            
            # 5. Generate answer using LLM
            gen_start_time = time.time()
            prompt = self.prompt_template.format(
                context=context,
                question=question
            )
            
            answer = self.llm.generate(prompt)
            gen_time = time.time() - gen_start_time
            
            # Log generation
            if self.audit_logger:
                query_hash = hashlib.sha256(question.encode()).hexdigest()[:16]
                self.audit_logger.log_generation(
                    query_hash,
                    self.llm.model_name,
                    gen_time,
                    True
                )
            
            response_time = time.time() - start_time
            
            # Log query
            if self.audit_logger:
                query_hash = hashlib.sha256(question.encode()).hexdigest()[:16]
                self.audit_logger.log_query(query_hash, len(search_results), response_time)
            
            result = {
                'answer': answer,
                'success': True,
                'num_chunks_retrieved': len(decrypted_chunks),
                'response_time': response_time,
                'generation_time': gen_time
            }
            
            if return_context:
                result['context'] = decrypted_chunks
            
            return result
        
        except Exception as e:
            print(f"Error processing query: {e}")
            
            if self.audit_logger:
                query_hash = hashlib.sha256(question.encode()).hexdigest()[:16]
                self.audit_logger.log_generation(
                    query_hash,
                    self.llm.model_name,
                    0,
                    False
                )
            
            return {
                'answer': f'Error processing query: {str(e)}',
                'success': False,
                'response_time': time.time() - start_time
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        return {
            'vector_count': self.vector_db.count(),
            'embedding_dimension': self.embedding_model.dimension,
            'llm_model': self.llm.model_name,
            'embedding_model': self.embedding_model.model_name
        }
