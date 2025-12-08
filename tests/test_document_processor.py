"""Tests for document processor module."""
import pytest
from pathlib import Path
import tempfile
from src.document_processor import DocumentParser, TextChunker


class TestTextChunker:
    """Test text chunking functionality."""
    
    def test_chunk_text(self):
        """Test basic text chunking."""
        chunker = TextChunker(chunk_size=100, chunk_overlap=20)
        
        text = "This is a test. " * 50  # Create long text
        
        chunks = chunker.chunk_text(text)
        
        assert len(chunks) > 0
        assert all('text' in chunk for chunk in chunks)
        assert all('chunk_id' in chunk for chunk in chunks)
        assert all('metadata' in chunk for chunk in chunks)
    
    def test_chunk_size_limit(self):
        """Test that chunks respect size limit."""
        chunk_size = 100
        chunker = TextChunker(chunk_size=chunk_size, chunk_overlap=10)
        
        text = "A" * 500
        chunks = chunker.chunk_text(text)
        
        # Most chunks should be around the chunk_size
        for chunk in chunks:
            assert len(chunk['text']) <= chunk_size + 50  # Allow some flexibility
    
    def test_empty_text(self):
        """Test chunking empty text."""
        chunker = TextChunker()
        
        chunks = chunker.chunk_text("")
        assert len(chunks) == 0
    
    def test_metadata_preservation(self):
        """Test that metadata is preserved."""
        chunker = TextChunker()
        
        text = "Test text"
        metadata = {'source': 'test.txt', 'author': 'test'}
        
        chunks = chunker.chunk_text(text, metadata)
        
        assert len(chunks) > 0
        assert chunks[0]['metadata'] == metadata


class TestDocumentParser:
    """Test document parsing functionality."""
    
    def test_parse_txt_file(self):
        """Test parsing text file."""
        parser = DocumentParser()
        
        # Create temporary text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a test document.\nIt has multiple lines.")
            temp_path = f.name
        
        try:
            text = parser.parse(temp_path)
            assert "This is a test document" in text
            assert "multiple lines" in text
        finally:
            Path(temp_path).unlink()
    
    def test_unsupported_format(self):
        """Test handling of unsupported file format."""
        parser = DocumentParser()
        
        with tempfile.NamedTemporaryFile(suffix='.xyz', delete=False) as f:
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError):
                parser.parse(temp_path)
        finally:
            Path(temp_path).unlink()
    
    def test_file_not_found(self):
        """Test handling of non-existent file."""
        parser = DocumentParser()
        
        with pytest.raises(FileNotFoundError):
            parser.parse("/nonexistent/file.txt")
