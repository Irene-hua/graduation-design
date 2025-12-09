"""
Embedding Model for generating vector representations
嵌入模型，用于生成向量表示
"""

from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np
import torch


class EmbeddingModel:
    """Lightweight embedding model for text vectorization"""
    
    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        device: str = "cpu",
        max_seq_length: int = 256
    ):
        """
        Initialize the embedding model
        
        Args:
            model_name: Name of the sentence-transformers model
            device: Device to run the model on ('cpu' or 'cuda')
            max_seq_length: Maximum sequence length
        """
        self.model_name = model_name
        self.device = device
        self.max_seq_length = max_seq_length
        
        # Load the model
        self.model = SentenceTransformer(model_name, device=device)
        self.model.max_seq_length = max_seq_length
        
        # Get embedding dimension
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
    
    def encode(
        self,
        texts: Union[str, List[str]],
        batch_size: int = 32,
        show_progress_bar: bool = False,
        normalize: bool = True
    ) -> np.ndarray:
        """
        Encode texts into embeddings
        
        Args:
            texts: Single text or list of texts
            batch_size: Batch size for encoding
            show_progress_bar: Whether to show progress bar
            normalize: Whether to normalize embeddings
        
        Returns:
            np.ndarray: Embeddings of shape (n_texts, embedding_dim)
        """
        if isinstance(texts, str):
            texts = [texts]
        
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress_bar,
            convert_to_numpy=True,
            normalize_embeddings=normalize
        )
        
        return embeddings
    
    def encode_single(self, text: str) -> np.ndarray:
        """
        Encode a single text into embedding
        
        Args:
            text: Input text
        
        Returns:
            np.ndarray: Embedding vector
        """
        return self.encode(text)[0]
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings
        
        Returns:
            int: Embedding dimension
        """
        return self.embedding_dim
    
    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
        
        Returns:
            float: Cosine similarity score
        """
        # Normalize if not already normalized
        embedding1 = embedding1 / np.linalg.norm(embedding1)
        embedding2 = embedding2 / np.linalg.norm(embedding2)
        
        return np.dot(embedding1, embedding2)
    
    def batch_similarity(
        self,
        query_embedding: np.ndarray,
        embeddings: np.ndarray
    ) -> np.ndarray:
        """
        Calculate cosine similarity between query and multiple embeddings
        
        Args:
            query_embedding: Query embedding of shape (embedding_dim,)
            embeddings: Array of embeddings of shape (n, embedding_dim)
        
        Returns:
            np.ndarray: Array of similarity scores
        """
        # Normalize
        query_embedding = query_embedding / np.linalg.norm(query_embedding)
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        
        return np.dot(embeddings, query_embedding)
