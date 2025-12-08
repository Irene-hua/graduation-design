"""Configuration management module."""
from pathlib import Path
import yaml
from typing import Any, Dict
from pydantic_settings import BaseSettings
from pydantic import Field


class Config(BaseSettings):
    """Application configuration."""
    
    # Paths
    base_dir: Path = Field(default=Path(__file__).parent.parent)
    config_file: Path = Field(default=Path(__file__).parent / "config.yaml")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_file.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_file}")
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    @property
    def embedding_config(self) -> Dict[str, Any]:
        """Get embedding configuration."""
        return self.load_config().get('embedding', {})
    
    @property
    def vector_db_config(self) -> Dict[str, Any]:
        """Get vector database configuration."""
        return self.load_config().get('vector_db', {})
    
    @property
    def document_processing_config(self) -> Dict[str, Any]:
        """Get document processing configuration."""
        return self.load_config().get('document_processing', {})
    
    @property
    def encryption_config(self) -> Dict[str, Any]:
        """Get encryption configuration."""
        return self.load_config().get('encryption', {})
    
    @property
    def llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration."""
        return self.load_config().get('llm', {})
    
    @property
    def rag_config(self) -> Dict[str, Any]:
        """Get RAG pipeline configuration."""
        return self.load_config().get('rag', {})
    
    @property
    def audit_config(self) -> Dict[str, Any]:
        """Get audit configuration."""
        return self.load_config().get('audit', {})
    
    @property
    def system_config(self) -> Dict[str, Any]:
        """Get system configuration."""
        return self.load_config().get('system', {})


# Global config instance
config = Config()
