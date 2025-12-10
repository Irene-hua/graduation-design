"""
Embedding Model for generating vector representations
嵌入模型，用于生成向量表示
"""

import os
from sentence_transformers import SentenceTransformer
from typing import List, Union, Optional
import numpy as np
import torch


class EmbeddingModel:
    """Lightweight embedding model for text vectorization"""
    
    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        device: str = "cpu",
        max_seq_length: int = 256,
        local_model_path: Optional[str] = None,
        offline: bool = False
    ):
        """
        Initialize the embedding model
        
        Args:
            model_name: Name of the sentence-transformers model (HuggingFace id or local folder)
            device: Device to run the model on ('cpu' or 'cuda')
            max_seq_length: Maximum sequence length
            local_model_path: If provided, load the model from this local path (preferred for offline use)
            offline: If True, force transformers/huggingface clients to run in offline mode
        """
        self.model_name = model_name
        self.device = device
        self.max_seq_length = max_seq_length
        self.local_model_path = local_model_path
        self.offline = offline

        # If offline mode requested, set standard env vars so HF/transformers will not attempt network calls
        if self.offline:
            os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
            os.environ.setdefault("HF_DATASETS_OFFLINE", "1")
            os.environ.setdefault("HUGGINGFACE_HUB_OFFLINE", "1")

        # Prefer local_model_path when provided
        load_target = None
        if self.local_model_path:
            # If a local path is provided and exists, load from there
            if os.path.isdir(self.local_model_path):
                load_target = self.local_model_path
            else:
                # allow passing a file-like reference; if not found, fall back to model_name
                load_target = None

        if load_target is None:
            load_target = self.model_name

        # Load the SentenceTransformer model
        try:
            # SentenceTransformer accepts both HuggingFace ids and local folders
            self.model = SentenceTransformer(load_target, device=device)
            self.model.max_seq_length = max_seq_length
        except Exception as e:
            # Provide a clearer error message to help with fully-offline setups
            raise RuntimeError(
                f"Failed to load embedding model '{load_target}' (device={device}). "
                "If you expect to run offline, ensure the model is available locally and pass its path via `local_model_path`, "
                "or set `offline=False` to allow downloads. Original error: " + str(e)
            )

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
