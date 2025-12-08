"""
Encryption Manager for AES-GCM encryption and decryption
加密管理器，使用AES-GCM进行加密和解密
"""

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os
import base64
from typing import Tuple
from .key_manager import KeyManager


class EncryptionManager:
    """Manages AES-GCM encryption and decryption operations"""
    
    def __init__(self, key: bytes = None, key_file: str = None):
        """
        Initialize the EncryptionManager
        
        Args:
            key: Encryption key (32 bytes for AES-256)
            key_file: Path to key file (used if key is not provided)
        """
        if key is None:
            key_manager = KeyManager(key_file)
            if not key_manager.key_exists():
                key = key_manager.generate_and_save_key()
            else:
                key = key_manager.load_key()
        
        self.key = key
        self.aesgcm = AESGCM(key)
    
    def encrypt(self, plaintext: str) -> Tuple[bytes, bytes]:
        """
        Encrypt plaintext using AES-GCM
        
        Args:
            plaintext: The text to encrypt
        
        Returns:
            tuple: (ciphertext, nonce)
        """
        # Generate a random nonce (96 bits recommended for GCM)
        nonce = os.urandom(12)
        
        # Encrypt the plaintext
        plaintext_bytes = plaintext.encode('utf-8')
        ciphertext = self.aesgcm.encrypt(nonce, plaintext_bytes, None)
        
        return ciphertext, nonce
    
    def decrypt(self, ciphertext: bytes, nonce: bytes) -> str:
        """
        Decrypt ciphertext using AES-GCM
        
        Args:
            ciphertext: The encrypted data
            nonce: The nonce used during encryption
        
        Returns:
            str: The decrypted plaintext
        
        Raises:
            InvalidTag: If decryption fails (tampering detected)
        """
        plaintext_bytes = self.aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext_bytes.decode('utf-8')
    
    def encrypt_to_base64(self, plaintext: str) -> str:
        """
        Encrypt plaintext and return as base64-encoded string
        
        Args:
            plaintext: The text to encrypt
        
        Returns:
            str: Base64-encoded string containing nonce and ciphertext
        """
        ciphertext, nonce = self.encrypt(plaintext)
        # Combine nonce and ciphertext
        combined = nonce + ciphertext
        return base64.b64encode(combined).decode('utf-8')
    
    def decrypt_from_base64(self, encrypted_base64: str) -> str:
        """
        Decrypt from base64-encoded string
        
        Args:
            encrypted_base64: Base64-encoded string containing nonce and ciphertext
        
        Returns:
            str: The decrypted plaintext
        """
        combined = base64.b64decode(encrypted_base64.encode('utf-8'))
        # Extract nonce (first 12 bytes) and ciphertext
        nonce = combined[:12]
        ciphertext = combined[12:]
        return self.decrypt(ciphertext, nonce)
    
    def encrypt_batch(self, texts: list[str]) -> list[Tuple[bytes, bytes]]:
        """
        Encrypt multiple texts
        
        Args:
            texts: List of plaintext strings
        
        Returns:
            list: List of (ciphertext, nonce) tuples
        """
        return [self.encrypt(text) for text in texts]
    
    def decrypt_batch(self, encrypted_data: list[Tuple[bytes, bytes]]) -> list[str]:
        """
        Decrypt multiple encrypted texts
        
        Args:
            encrypted_data: List of (ciphertext, nonce) tuples
        
        Returns:
            list: List of decrypted plaintext strings
        """
        return [self.decrypt(ciphertext, nonce) for ciphertext, nonce in encrypted_data]
