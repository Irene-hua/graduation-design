"""
Tests for document processor
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils import DocumentProcessor


class TestDocumentProcessor:
    """Tests for DocumentProcessor"""
    
    def test_initialization(self):
        """Test processor initialization"""
        processor = DocumentProcessor(chunk_size=500, chunk_overlap=50)
        
        assert processor.chunk_size == 500
        assert processor.chunk_overlap == 50
    
    def test_chunk_text(self):
        """Test text chunking"""
        processor = DocumentProcessor(chunk_size=100, chunk_overlap=20)
        
        text = "This is a test. " * 50  # Create long text
        chunks = processor.chunk_text(text)
        
        assert len(chunks) > 0
        assert all('text' in chunk for chunk in chunks)
        assert all('id' in chunk for chunk in chunks)
        assert all('start' in chunk for chunk in chunks)
        assert all('end' in chunk for chunk in chunks)
    
    def test_load_txt(self, tmp_path):
        """Test loading text file"""
        test_file = tmp_path / "test.txt"
        test_content = "This is a test document.\nWith multiple lines."
        
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        processor = DocumentProcessor()
        content = processor.load_document(str(test_file))
        
        assert test_content in content
    
    def test_clean_text(self):
        """Test text cleaning"""
        processor = DocumentProcessor()
        
        dirty_text = "Text  with   multiple    spaces\n\n\nand  newlines"
        clean_text = processor._clean_text(dirty_text)
        
        assert "  " not in clean_text
        assert "\n\n" not in clean_text
    
    def test_process_document(self, tmp_path):
        """Test full document processing"""
        test_file = tmp_path / "test.txt"
        test_content = "This is a test document. " * 20
        
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        processor = DocumentProcessor(chunk_size=100, chunk_overlap=20)
        chunks = processor.process_document(str(test_file))
        
        assert len(chunks) > 0
        assert all('source' in chunk for chunk in chunks)
        assert all('file_path' in chunk for chunk in chunks)
        assert all(chunk['source'] == 'test.txt' for chunk in chunks)
    
    def test_unsupported_format(self, tmp_path):
        """Test unsupported file format"""
        test_file = tmp_path / "test.xyz"
        test_file.write_text("test")
        
        processor = DocumentProcessor()
        
        with pytest.raises(ValueError):
            processor.load_document(str(test_file))


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
