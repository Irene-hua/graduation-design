"""
Vector Store using Qdrant for storing and retrieving encrypted documents
向量存储，使用Qdrant存储和检索加密文档
"""

from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from qdrant_client.models import Filter, FieldCondition, MatchValue
import uuid
import numpy as np


class VectorStore:
    """Vector database for storing embeddings and encrypted text"""
    
    def __init__(
        self,
        collection_name: str = "private_documents",
        host: str = "localhost",
        port: int = 6333,
        path: str = None,
        vector_size: int = 384,
        distance: Distance = Distance.COSINE
    ):
        """
        Initialize the VectorStore
        
        Args:
            collection_name: Name of the collection
            host: Qdrant server host
            port: Qdrant server port
            path: Path for local storage (if not using server)
            vector_size: Dimension of vectors
            distance: Distance metric (COSINE, EUCLID, DOT)
        """
        self.collection_name = collection_name
        self.vector_size = vector_size
        
        # Initialize Qdrant client (local mode if path is provided)
        if path:
            self.client = QdrantClient(path=path)
        else:
            self.client = QdrantClient(host=host, port=port)
        
        # Create collection if it doesn't exist
        self._create_collection_if_not_exists(distance)
    
    def _create_collection_if_not_exists(self, distance: Distance) -> None:
        """Create collection if it doesn't exist"""
        collections = self.client.get_collections().collections
        collection_names = [col.name for col in collections]
        
        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=distance
                )
            )
    
    def add_documents(
        self,
        embeddings: List[np.ndarray],
        encrypted_texts: List[str],
        nonces: List[str],
        metadata: List[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Add documents to the vector store
        
        Args:
            embeddings: List of embedding vectors
            encrypted_texts: List of encrypted texts (base64)
            nonces: List of nonces used for encryption (base64)
            metadata: Optional list of metadata dictionaries
        
        Returns:
            list: List of document IDs
        """
        if metadata is None:
            metadata = [{}] * len(embeddings)
        
        if not (len(embeddings) == len(encrypted_texts) == len(nonces) == len(metadata)):
            raise ValueError("All input lists must have the same length")
        
        points = []
        ids = []
        
        for i, (embedding, encrypted_text, nonce, meta) in enumerate(
            zip(embeddings, encrypted_texts, nonces, metadata)
        ):
            doc_id = str(uuid.uuid4())
            ids.append(doc_id)
            
            # Prepare payload with encrypted data and metadata
            payload = {
                'encrypted_text': encrypted_text,
                'nonce': nonce,
                **meta
            }
            
            # Create point
            point = PointStruct(
                id=doc_id,
                vector=embedding.tolist() if isinstance(embedding, np.ndarray) else embedding,
                payload=payload
            )
            points.append(point)
        
        # Upload points to Qdrant
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        
        return ids
    
    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        score_threshold: float = 0.0,
        filter_dict: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            score_threshold: Minimum similarity score
            filter_dict: Optional filter conditions
        
        Returns:
            list: List of search results with encrypted text and metadata
        """
        # Prepare filter if provided
        query_filter = None
        if filter_dict:
            conditions = [
                FieldCondition(key=k, match=MatchValue(value=v))
                for k, v in filter_dict.items()
            ]
            query_filter = Filter(must=conditions)
        
        # Search
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding.tolist() if isinstance(query_embedding, np.ndarray) else query_embedding,
            limit=top_k,
            score_threshold=score_threshold,
            query_filter=query_filter
        )
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                'id': result.id,
                'score': result.score,
                'encrypted_text': result.payload.get('encrypted_text'),
                'nonce': result.payload.get('nonce'),
                'metadata': {k: v for k, v in result.payload.items() 
                           if k not in ['encrypted_text', 'nonce']}
            })
        
        return formatted_results
    
    def delete_collection(self) -> None:
        """Delete the collection"""
        self.client.delete_collection(collection_name=self.collection_name)
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get collection information
        
        Returns:
            dict: Collection information
        """
        info = self.client.get_collection(collection_name=self.collection_name)
        return {
            'name': self.collection_name,
            'vectors_count': info.vectors_count,
            'points_count': info.points_count,
            'status': info.status
        }
    
    def delete_documents(self, ids: List[str]) -> None:
        """
        Delete documents by IDs
        
        Args:
            ids: List of document IDs to delete
        """
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=ids
        )
