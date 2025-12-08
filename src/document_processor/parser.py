"""Document parser for various file formats."""
import os
from pathlib import Path
from typing import Union, List
import PyPDF2
import docx


class DocumentParser:
    """Parse documents from various formats."""
    
    def __init__(self, supported_formats: List[str] = None):
        """
        Initialize document parser.
        
        Args:
            supported_formats: List of supported file extensions
        """
        self.supported_formats = supported_formats or ['pdf', 'txt', 'docx']
    
    def parse(self, file_path: Union[str, Path]) -> str:
        """
        Parse document and extract text.
        
        Args:
            file_path: Path to document file
            
        Returns:
            Extracted text content
            
        Raises:
            ValueError: If file format is not supported
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        extension = file_path.suffix.lower().lstrip('.')
        
        if extension not in self.supported_formats:
            raise ValueError(f"Unsupported format: {extension}. Supported: {self.supported_formats}")
        
        # Route to appropriate parser
        if extension == 'pdf':
            return self._parse_pdf(file_path)
        elif extension == 'txt':
            return self._parse_txt(file_path)
        elif extension == 'docx':
            return self._parse_docx(file_path)
        else:
            raise ValueError(f"No parser available for format: {extension}")
    
    def _parse_pdf(self, file_path: Path) -> str:
        """Parse PDF file."""
        text = []
        
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
        
        return '\n\n'.join(text)
    
    def _parse_txt(self, file_path: Path) -> str:
        """Parse text file."""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    
    def _parse_docx(self, file_path: Path) -> str:
        """Parse DOCX file."""
        doc = docx.Document(file_path)
        
        text = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text.append(paragraph.text)
        
        return '\n\n'.join(text)
    
    def parse_directory(self, directory_path: Union[str, Path]) -> dict:
        """
        Parse all supported documents in a directory.
        
        Args:
            directory_path: Path to directory
            
        Returns:
            Dictionary mapping filenames to extracted text
        """
        directory_path = Path(directory_path)
        
        if not directory_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {directory_path}")
        
        results = {}
        
        for file_path in directory_path.iterdir():
            if file_path.is_file():
                extension = file_path.suffix.lower().lstrip('.')
                if extension in self.supported_formats:
                    try:
                        results[file_path.name] = self.parse(file_path)
                    except Exception as e:
                        print(f"Error parsing {file_path.name}: {e}")
        
        return results
