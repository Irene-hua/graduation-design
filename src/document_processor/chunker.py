"""Text chunking utilities for document processing."""
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter


class TextChunker:
    """Chunk text documents for RAG processing."""
    
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        """
        Initialize text chunker.
        
        Args:
            chunk_size: Maximum size of each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", "。", ".", " ", ""]
        )
    
    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Split text into chunks.
        
        Args:
            text: Text to chunk
            metadata: Optional metadata to attach to each chunk
            
        Returns:
            List of chunks with metadata
        """
        if not text or not text.strip():
            return []
        
        # Split text into chunks
        chunks = self.splitter.split_text(text)
        
        # Create chunk objects with metadata
        result = []
        for idx, chunk in enumerate(chunks):
            chunk_data = {
                'text': chunk,
                'chunk_id': idx,
                'chunk_size': len(chunk),
                'metadata': metadata or {}
            }
            result.append(chunk_data)
        
        return result
    
    def chunk_documents(self, documents: Dict[str, str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Chunk multiple documents.
        
        Args:
            documents: Dictionary mapping document names to text content
            
        Returns:
            Dictionary mapping document names to list of chunks
        """
        results = {}
        
        for doc_name, text in documents.items():
            metadata = {'source': doc_name}
            results[doc_name] = self.chunk_text(text, metadata)
        
        return results
