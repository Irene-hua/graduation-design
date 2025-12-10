"""
Main RAG System integrating all components
主RAG系统，集成所有组件
"""

import time
import uuid
import os
from typing import Dict, Any, List
from pathlib import Path
from qdrant_client.models import Distance

from .encryption import EncryptionManager
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
        # Support config keys: 'model' (HuggingFace id or local path), optional 'local_model_path', and 'offline'
        model_name = emb_config.get('model') or emb_config.get('model_name') or 'sentence-transformers/all-MiniLM-L6-v2'
        local_model_path = emb_config.get('local_model_path') or emb_config.get('model_path')
        offline_flag = emb_config.get('offline', False)
        # If env sets HUGGINGFACE_HUB_OFFLINE, respect it as well
        if not offline_flag:
            offline_flag = True if os.environ.get('HUGGINGFACE_HUB_OFFLINE') in ('1', 'true', 'True') else False

        # If the configured model_name points to a local directory, treat it as local_model_path
        # and force offline mode to avoid accidental network calls.
        try:
            # Normalize possible relative paths
            if isinstance(model_name, str) and os.path.isdir(os.path.expanduser(model_name)):
                # Use the directory as the local_model_path
                local_model_path = model_name
                offline_flag = True
        except Exception:
            pass

        # Ensure offline env vars are set if offline_flag is True to force HF/transformers offline
        if offline_flag:
            os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
            os.environ.setdefault("HF_DATASETS_OFFLINE", "1")
            os.environ.setdefault("HUGGINGFACE_HUB_OFFLINE", "1")

        self.embedding_model = EmbeddingModel(
            model_name=model_name,
            device=emb_config.get('device', 'cpu'),
            max_seq_length=emb_config.get('max_seq_length', 256),
            local_model_path=local_model_path,
            offline=offline_flag
        )
        
        # Initialize vector store
        vdb_config = self.config.get_section('vector_db')
        # support nested qdrant config: vector_db.qdrant
        q_cfg = vdb_config.get('qdrant', {}) if isinstance(vdb_config, dict) else {}
        collection_name = q_cfg.get('collection') or vdb_config.get('collection_name') or 'private_documents'
        host = q_cfg.get('host', vdb_config.get('host', '127.0.0.1'))
        port = q_cfg.get('port', vdb_config.get('port', 6333))
        storage_path = q_cfg.get('storage_path') or vdb_config.get('storage_path') or None
        distance_map = {
            'COSINE': Distance.COSINE,
            'EUCLID': Distance.EUCLID,
            'DOT': Distance.DOT
        }
        distance_str = (q_cfg.get('distance') or vdb_config.get('distance') or 'COSINE').upper()
        distance = distance_map.get(distance_str, Distance.COSINE)

        # If a storage path is provided, pass it to VectorStore (VectorStore will choose client mode)
        self.vector_store = VectorStore(
            collection_name=collection_name,
            host=host,
            port=port,
            path=storage_path,
            vector_size=self.embedding_model.get_embedding_dimension(),
            distance=distance
        )
        
        # Initialize LLM client
        llm_config = self.config.get_section('llm')
        # support nested llm.ollama config
        ollama_cfg = llm_config.get('ollama', {}) if isinstance(llm_config, dict) else {}
        base_url = ollama_cfg.get('host') or llm_config.get('base_url') or 'http://localhost:11434'
        llm_model_name = ollama_cfg.get('model') or llm_config.get('model_name') or 'llama3.2:3b'
        self.llm_client = LLMClient(
            base_url=base_url,
            model_name=llm_model_name,
            temperature=ollama_cfg.get('temperature', llm_config.get('temperature', 0.1)),
            max_tokens=ollama_cfg.get('max_tokens', llm_config.get('max_tokens', 1024)),
            top_p=ollama_cfg.get('top_p', llm_config.get('top_p', 0.95))
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

            # Generate embeddings (ensure a list of vectors)
            embeddings = list(self.embedding_model.encode(texts, show_progress_bar=True))

            # Encrypt texts
            encrypted_data = []
            nonces = []

            for text in texts:
                encrypted_base64 = self.encryption_manager.encrypt_to_base64(text)
                encrypted_data.append(encrypted_base64)
                # Nonce is embedded in the base64-encoded ciphertext, so we pass None as placeholder
                nonces.append(None)

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
            decrypted_chunks: List[Dict[str, Any]] = []
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
        # Retrieve raw info from the vector store and normalize it to a stable dict
        try:
            raw = self.vector_store.get_collection_info()
        except Exception as e:
            raise RuntimeError(f"failed to get collection info: {e}") from e

        return self._normalize_collection_info(raw)

    def _normalize_collection_info(self, info: Any) -> Dict[str, Any]:
        """
        Normalize various forms of collection info returned by different qdrant-client
        versions into a stable dict with keys: name, points_count, vectors_count, status, _raw
        """
        data = None
        # Try pydantic .dict()
        try:
            if hasattr(info, 'dict'):
                data = info.dict()
        except Exception:
            data = None

        # Fallback to __dict__
        if data is None:
            try:
                if hasattr(info, '__dict__'):
                    data = dict(info.__dict__)
            except Exception:
                data = None

        # If it's already a dict
        if data is None and isinstance(info, dict):
            data = info

        # Final fallback to vars()
        if data is None:
            try:
                data = dict(vars(info))
            except Exception:
                data = {}

        def pick(*keys):
            for k in keys:
                if isinstance(data, dict) and k in data and data[k] is not None:
                    return data[k]
            for k in keys:
                if hasattr(info, k):
                    try:
                        val = getattr(info, k)
                        if val is not None:
                            return val
                    except Exception:
                        pass
            return None

        name = pick('name', 'collection_name')
        points_count = pick('points_count', 'points', 'num_points', 'count')
        vectors_count = pick('vectors_count', 'vectors', 'num_vectors', 'size')
        status = pick('status', 'collection_status')

        # Some versions may return nested dicts with 'count'
        if isinstance(points_count, dict) and 'count' in points_count:
            points_count = points_count['count']
        if isinstance(vectors_count, dict) and 'count' in vectors_count:
            vectors_count = vectors_count['count']

        try:
            points_count = int(points_count) if points_count is not None else None
        except Exception:
            points_count = None
        try:
            vectors_count = int(vectors_count) if vectors_count is not None else None
        except Exception:
            vectors_count = None

        return {
            'name': name or 'unknown',
            'points_count': points_count,
            'vectors_count': vectors_count,
            'status': status or 'unknown',
            '_raw': data,
        }

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
