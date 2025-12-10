"""
Vector Store using Qdrant for storing and retrieving encrypted documents
向量存储，使用Qdrant存储和检索加密文档
"""

from typing import List, Dict, Any
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

        # Normalize possible shapes: pydantic model (has .dict()), object attrs, or dict
        data = None
        try:
            # pydantic v2 uses model_dump(), v1 used dict()
            if hasattr(info, 'model_dump'):
                data = info.model_dump()
            elif hasattr(info, 'dict'):
                data = info.dict()
        except Exception:
            data = None

        if data is None:
            try:
                if hasattr(info, '__dict__'):
                    data = dict(info.__dict__)
            except Exception:
                data = None

        if data is None and isinstance(info, dict):
            data = info

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

        points = pick('points_count', 'points', 'num_points', 'count')
        vectors = pick('vectors_count', 'vectors', 'num_vectors')
        status = pick('status', 'collection_status')

        # Unwrap nested dicts with 'count'
        if isinstance(points, dict) and 'count' in points:
            points = points['count']
        if isinstance(vectors, dict) and 'count' in vectors:
            vectors = vectors['count']

        try:
            points = int(points) if points is not None else None
        except Exception:
            points = None
        try:
            vectors = int(vectors) if vectors is not None else None
        except Exception:
            vectors = None

        # If vectors_count is not provided by the server, it's usually safe to
        # fall back to the number of points (one vector per point) for display
        # and compatibility with older code paths.
        if vectors is None and points is not None:
            vectors = points
        # If both are None (older/newer client variations), try inspecting
        # the raw returned structure for common keys used by qdrant-server
        # (e.g., "points_count", "vectors_count", nested dicts). If still
        # not found, default to 0 instead of leaving the field missing which
        # caused AttributeError upstream.
        if vectors is None and points is None:
            # Attempt to inspect common nested shapes
            raw = data if isinstance(data, dict) else {}
            def try_get_int(keys):
                for k in keys:
                    v = raw.get(k) if isinstance(raw, dict) else None
                    if isinstance(v, dict) and 'count' in v:
                        try:
                            return int(v['count'])
                        except Exception:
                            continue
                    if v is not None:
                        try:
                            return int(v)
                        except Exception:
                            continue
                return None

            vectors = try_get_int(['vectors_count', 'vectors', 'num_vectors', 'vectors_count_total'])
            if vectors is None:
                points = try_get_int(['points_count', 'points', 'num_points', 'count'])
                if points is not None:
                    vectors = points
            # Final safe default
            if vectors is None:
                vectors = 0

        # Ensure points is set to an int or 0 as a safe default
        if points is None:
            points = 0

        return {
            'name': getattr(info, 'name', self.collection_name) or self.collection_name,
            'points_count': points,
            'vectors_count': vectors,
            'status': status or 'unknown',
            '_raw': data,
        }

    def delete_documents(self, ids: List[str]) -> None:
        """
        Delete documents by IDs

        Args:
            ids: List of document IDs to delete
        """
        # qdrant-client delete API expects a points selector; using list of ids is supported
        try:
            self.client.delete(collection_name=self.collection_name, points_selector=ids)
        except TypeError:
            # Older client versions may have a different signature; try selector dict
            try:
                self.client.delete(collection_name=self.collection_name, points=ids)
            except Exception as e:
                raise

