"""Qdrant vector database integration."""
from typing import List, Dict, Any, Optional
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams,
    Distance,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue
)


class QdrantDB:
    """Qdrant vector database wrapper for encrypted document storage."""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        collection_name: str = "encrypted_documents",
        dimension: int = 384,
        distance_metric: str = "cosine"
    ):
        """
        Initialize Qdrant database connection.
        
        Args:
            host: Qdrant server host
            port: Qdrant server port
            collection_name: Name of the collection
            dimension: Vector dimension
            distance_metric: Distance metric ('cosine', 'euclidean', 'dot')
        """
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.dimension = dimension
        
        # Map distance metric
        distance_map = {
            'cosine': Distance.COSINE,
            'euclidean': Distance.EUCLID,
            'dot': Distance.DOT
        }
        self.distance = distance_map.get(distance_metric.lower(), Distance.COSINE)
        
        # Initialize client
        self.client = QdrantClient(host=host, port=port)
        
        # Create collection if it doesn't exist
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Create collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.dimension,
                    distance=self.distance
                )
            )
    
    def insert(
        self,
        vectors: np.ndarray,
        encrypted_texts: List[str],
        metadata: List[Dict[str, Any]],
        ids: Optional[List[int]] = None
    ) -> bool:
        """
        Insert vectors with encrypted texts and metadata.
        
        Args:
            vectors: Array of embedding vectors
            encrypted_texts: List of encrypted text chunks
            metadata: List of metadata dicts for each chunk
            ids: Optional list of IDs. If None, auto-generated.
            
        Returns:
            True if successful
        """
        if len(vectors) != len(encrypted_texts) != len(metadata):
            raise ValueError("Vectors, encrypted texts, and metadata must have same length")
        
        points = []
        
        for idx, (vector, encrypted_text, meta) in enumerate(
            zip(vectors, encrypted_texts, metadata)
        ):
            point_id = ids[idx] if ids else idx
            
            # Combine encrypted text with metadata
            payload = {
                'encrypted_text': encrypted_text,
                **meta
            }
            
            point = PointStruct(
                id=point_id,
                vector=vector.tolist() if isinstance(vector, np.ndarray) else vector,
                payload=payload
            )
            points.append(point)
        
        # Insert in batches
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        
        return True
    
    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 5,
        filter_conditions: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors.
        
        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            filter_conditions: Optional filter conditions
            
        Returns:
            List of search results with encrypted texts and metadata
        """
        # Convert numpy array to list
        if isinstance(query_vector, np.ndarray):
            query_vector = query_vector.tolist()
        
        # Build filter if provided
        query_filter = None
        if filter_conditions:
            # Simple filter by metadata fields
            conditions = []
            for key, value in filter_conditions.items():
                conditions.append(
                    FieldCondition(key=key, match=MatchValue(value=value))
                )
            if conditions:
                query_filter = Filter(must=conditions)
        
        # Search
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k,
            query_filter=query_filter
        )
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                'id': result.id,
                'score': result.score,
                'encrypted_text': result.payload.get('encrypted_text'),
                'metadata': {k: v for k, v in result.payload.items() if k != 'encrypted_text'}
            })
        
        return formatted_results
    
    def delete_collection(self) -> bool:
        """Delete the collection."""
        self.client.delete_collection(collection_name=self.collection_name)
        return True
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get collection information."""
        info = self.client.get_collection(collection_name=self.collection_name)
        return {
            'name': self.collection_name,
            'points_count': info.points_count,
            'vectors_config': info.config.params.vectors
        }
    
    def count(self) -> int:
        """Get number of vectors in collection."""
        info = self.client.get_collection(collection_name=self.collection_name)
        return info.points_count
