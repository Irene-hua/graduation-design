"""AES encryption/decryption utilities for protecting document content."""
import os
import base64
from pathlib import Path
from typing import Union
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2


class AESEncryption:
    """AES-GCM encryption handler for document protection."""
    
    def __init__(self, key: bytes = None):
        """
        Initialize AES encryption.
        
        Args:
            key: 256-bit encryption key. If None, generates a new key.
        """
        if key is None:
            key = AESGCM.generate_key(bit_length=256)
        
        if len(key) != 32:
            raise ValueError("Key must be 32 bytes (256 bits) for AES-256")
        
        self.key = key
        self.aesgcm = AESGCM(key)
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext string.
        
        Args:
            plaintext: Text to encrypt
            
        Returns:
            Base64-encoded encrypted text with nonce
        """
        if not plaintext:
            return ""
        
        # Convert string to bytes
        plaintext_bytes = plaintext.encode('utf-8')
        
        # Generate random nonce (12 bytes for GCM)
        nonce = os.urandom(12)
        
        # Encrypt
        ciphertext = self.aesgcm.encrypt(nonce, plaintext_bytes, None)
        
        # Combine nonce and ciphertext, then base64 encode
        encrypted_data = nonce + ciphertext
        return base64.b64encode(encrypted_data).decode('utf-8')
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt ciphertext string.
        
        Args:
            ciphertext: Base64-encoded encrypted text
            
        Returns:
            Decrypted plaintext
        """
        if not ciphertext:
            return ""
        
        # Decode from base64
        encrypted_data = base64.b64decode(ciphertext.encode('utf-8'))
        
        # Extract nonce and ciphertext
        nonce = encrypted_data[:12]
        ciphertext_bytes = encrypted_data[12:]
        
        # Decrypt
        plaintext_bytes = self.aesgcm.decrypt(nonce, ciphertext_bytes, None)
        
        return plaintext_bytes.decode('utf-8')
    
    def encrypt_file(self, input_path: Union[str, Path], output_path: Union[str, Path]) -> None:
        """
        Encrypt a file.
        
        Args:
            input_path: Path to input file
            output_path: Path to output encrypted file
        """
        with open(input_path, 'r', encoding='utf-8') as f:
            plaintext = f.read()
        
        ciphertext = self.encrypt(plaintext)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(ciphertext)
    
    def decrypt_file(self, input_path: Union[str, Path], output_path: Union[str, Path]) -> None:
        """
        Decrypt a file.
        
        Args:
            input_path: Path to encrypted file
            output_path: Path to output decrypted file
        """
        with open(input_path, 'r', encoding='utf-8') as f:
            ciphertext = f.read()
        
        plaintext = self.decrypt(ciphertext)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(plaintext)


def generate_key() -> bytes:
    """
    Generate a new 256-bit encryption key.
    
    Returns:
        32-byte encryption key
    """
    return AESGCM.generate_key(bit_length=256)


def save_key(key: bytes, key_path: Union[str, Path]) -> None:
    """
    Save encryption key to file.
    
    Args:
        key: Encryption key
        key_path: Path to save key file
    """
    key_path = Path(key_path)
    key_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(key_path, 'wb') as f:
        f.write(key)
    
    # Set restrictive permissions (owner only)
    os.chmod(key_path, 0o600)


def load_key(key_path: Union[str, Path]) -> bytes:
    """
    Load encryption key from file.
    
    Args:
        key_path: Path to key file
        
    Returns:
        Encryption key
    """
    with open(key_path, 'rb') as f:
        return f.read()
