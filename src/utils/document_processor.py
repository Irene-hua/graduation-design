"""
Document Processor for parsing and chunking documents
文档处理器，用于解析和切分文档
"""

import re
from pathlib import Path
from typing import List, Dict
import pypdf
import docx
import markdown
from bs4 import BeautifulSoup


class DocumentProcessor:
    """Process and chunk documents for RAG system"""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Initialize DocumentProcessor
        
        Args:
            chunk_size: Maximum size of each chunk in characters
            chunk_overlap: Overlap between consecutive chunks in characters
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def load_document(self, file_path: str) -> str:
        """
        Load document content from file
        
        Args:
            file_path: Path to the document file
        
        Returns:
            str: Document content
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")
        
        file_extension = path.suffix.lower()
        
        if file_extension == '.pdf':
            return self._load_pdf(path)
        elif file_extension == '.txt':
            return self._load_txt(path)
        elif file_extension == '.docx':
            return self._load_docx(path)
        elif file_extension == '.md':
            return self._load_markdown(path)
        elif file_extension in ['.html', '.htm']:
            return self._load_html(path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    
    def _load_pdf(self, path: Path) -> str:
        """Load content from PDF file"""
        text = ""
        with open(path, 'rb') as f:
            pdf_reader = pypdf.PdfReader(f)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    def _load_txt(self, path: Path) -> str:
        """Load content from text file"""
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _load_docx(self, path: Path) -> str:
        """Load content from DOCX file"""
        doc = docx.Document(path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    
    def _load_markdown(self, path: Path) -> str:
        """Load content from Markdown file"""
        with open(path, 'r', encoding='utf-8') as f:
            md_text = f.read()
        html = markdown.markdown(md_text)
        soup = BeautifulSoup(html, 'html.parser')
        return soup.get_text()
    
    def _load_html(self, path: Path) -> str:
        """Load content from HTML file"""
        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()
        soup = BeautifulSoup(html, 'html.parser')
        return soup.get_text()
    
    def chunk_text(self, text: str) -> List[Dict[str, any]]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Input text to chunk
        
        Returns:
            list: List of chunk dictionaries with text and metadata
        """
        # Clean text
        text = self._clean_text(text)
        
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Find the end of the last complete sentence within the chunk
            if end < len(text):
                # Look for sentence endings
                last_period = text.rfind('.', start, end)
                last_newline = text.rfind('\n', start, end)
                
                sentence_end = max(last_period, last_newline)
                
                if sentence_end > start:
                    end = sentence_end + 1
            
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunks.append({
                    'id': chunk_id,
                    'text': chunk_text,
                    'start': start,
                    'end': end,
                    'length': len(chunk_text)
                })
                chunk_id += 1
            
            # Move start position with overlap
            start = end - self.chunk_overlap
        
        return chunks
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text
        
        Args:
            text: Input text
        
        Returns:
            str: Cleaned text
        """
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        # Remove multiple newlines
        text = re.sub(r'\n+', '\n', text)
        # Strip leading/trailing whitespace
        text = text.strip()
        return text
    
    def process_document(self, file_path: str) -> List[Dict[str, any]]:
        """
        Load and chunk a document
        
        Args:
            file_path: Path to the document
        
        Returns:
            list: List of chunks with metadata
        """
        content = self.load_document(file_path)
        chunks = self.chunk_text(content)
        
        # Add file metadata to each chunk
        file_name = Path(file_path).name
        for chunk in chunks:
            chunk['source'] = file_name
            chunk['file_path'] = file_path
        
        return chunks
