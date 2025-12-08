"""
Configuration Loader
配置加载器
"""

import yaml
from pathlib import Path
from typing import Any, Dict


class ConfigLoader:
    """Load and manage system configuration"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize the ConfigLoader
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = Path(config_path)
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file
        
        Returns:
            dict: Configuration dictionary
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        return config
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key (supports nested keys with dot notation)
        
        Args:
            key: Configuration key (e.g., "encryption.algorithm")
            default: Default value if key not found
        
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get entire configuration section
        
        Args:
            section: Section name
        
        Returns:
            dict: Section configuration
        """
        return self.config.get(section, {})
    
    def reload(self) -> None:
        """Reload configuration from file"""
        self.config = self.load_config()
