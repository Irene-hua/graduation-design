"""Lightweight embedding model for text vectorization."""
from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    """Lightweight embedding model wrapper."""
    
    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        device: str = "cpu",
        batch_size: int = 32
    ):
        """
        Initialize embedding model.
        
        Args:
            model_name: Name of the sentence transformer model
            device: Device to use ('cpu' or 'cuda')
            batch_size: Batch size for encoding
        """
        self.model_name = model_name
        self.device = device
        self.batch_size = batch_size
        
        # Load model
        self.model = SentenceTransformer(model_name, device=device)
        self.dimension = self.model.get_sentence_embedding_dimension()
    
    def encode(
        self,
        texts: Union[str, List[str]],
        show_progress: bool = False
    ) -> np.ndarray:
        """
        Encode text(s) into embeddings.
        
        Args:
            texts: Single text or list of texts to encode
            show_progress: Whether to show progress bar
            
        Returns:
            Numpy array of embeddings
        """
        if isinstance(texts, str):
            texts = [texts]
        
        embeddings = self.model.encode(
            texts,
            batch_size=self.batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True,
            normalize_embeddings=True  # Normalize for cosine similarity
        )
        
        return embeddings
    
    def encode_batch(
        self,
        text_batches: List[List[str]],
        show_progress: bool = False
    ) -> List[np.ndarray]:
        """
        Encode multiple batches of texts.
        
        Args:
            text_batches: List of text batches
            show_progress: Whether to show progress bar
            
        Returns:
            List of embedding arrays
        """
        results = []
        
        for batch in text_batches:
            embeddings = self.encode(batch, show_progress=show_progress)
            results.append(embeddings)
        
        return results
    
    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self.dimension
    
    def similarity(self, text1: str, text2: str) -> float:
        """
        Calculate cosine similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Cosine similarity score (0 to 1)
        """
        embeddings = self.encode([text1, text2])
        
        # Calculate cosine similarity
        similarity = np.dot(embeddings[0], embeddings[1])
        
        return float(similarity)
