"""
Key Manager for generating and managing encryption keys
密钥管理器，用于生成和管理加密密钥
"""

import os
from pathlib import Path
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import secrets


class KeyManager:
    """Manages encryption keys for the system"""
    
    def __init__(self, key_file: str = None):
        """
        Initialize the KeyManager
        
        Args:
            key_file: Path to the encryption key file
        """
        self.key_file = key_file or "config/encryption.key"
        self.key_file_path = Path(self.key_file)
    
    def generate_key(self) -> bytes:
        """
        Generate a new 256-bit encryption key
        
        Returns:
            bytes: 32-byte encryption key
        """
        return secrets.token_bytes(32)  # 256 bits
    
    def save_key(self, key: bytes) -> None:
        """
        Save encryption key to file
        
        Args:
            key: The encryption key to save
        """
        # Create directory if it doesn't exist
        self.key_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write key to file with restricted permissions
        with open(self.key_file_path, 'wb') as f:
            f.write(key)
        
        # Set file permissions to read/write for owner only (Unix-like systems)
        if os.name != 'nt':  # Not Windows
            os.chmod(self.key_file_path, 0o600)
    
    def load_key(self) -> bytes:
        """
        Load encryption key from file
        
        Returns:
            bytes: The encryption key
            
        Raises:
            FileNotFoundError: If key file doesn't exist
        """
        if not self.key_file_path.exists():
            raise FileNotFoundError(
                f"Encryption key file not found: {self.key_file_path}\n"
                "Please generate a key first using generate_and_save_key()"
            )
        
        with open(self.key_file_path, 'rb') as f:
            return f.read()
    
    def generate_and_save_key(self) -> bytes:
        """
        Generate a new key and save it to file
        
        Returns:
            bytes: The generated encryption key
        """
        key = self.generate_key()
        self.save_key(key)
        return key
    
    def key_exists(self) -> bool:
        """
        Check if encryption key file exists
        
        Returns:
            bool: True if key file exists, False otherwise
        """
        return self.key_file_path.exists()
    
    @staticmethod
    def derive_key_from_password(password: str, salt: bytes = None) -> tuple[bytes, bytes]:
        """
        Derive an encryption key from a password using PBKDF2
        
        Args:
            password: The password to derive the key from
            salt: Optional salt bytes (will be generated if not provided)
        
        Returns:
            tuple: (derived_key, salt)
        """
        if salt is None:
            salt = secrets.token_bytes(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        key = kdf.derive(password.encode())
        return key, salt
