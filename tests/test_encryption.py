"""
Tests for encryption module
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.encryption import EncryptionManager, KeyManager


class TestKeyManager:
    """Tests for KeyManager"""
    
    def test_generate_key(self, tmp_path):
        """Test key generation"""
        key_manager = KeyManager()
        key = key_manager.generate_key()
        
        assert len(key) == 32  # 256 bits
        assert isinstance(key, bytes)
    
    def test_save_and_load_key(self, tmp_path):
        """Test saving and loading key"""
        key_file = tmp_path / "test.key"
        key_manager = KeyManager(str(key_file))
        
        original_key = key_manager.generate_and_save_key()
        loaded_key = key_manager.load_key()
        
        assert original_key == loaded_key
    
    def test_key_exists(self, tmp_path):
        """Test key existence check"""
        key_file = tmp_path / "test.key"
        key_manager = KeyManager(str(key_file))
        
        assert not key_manager.key_exists()
        
        key_manager.generate_and_save_key()
        
        assert key_manager.key_exists()
    
    def test_derive_key_from_password(self):
        """Test password-based key derivation"""
        password = "test_password_123"
        key1, salt1 = KeyManager.derive_key_from_password(password)
        
        assert len(key1) == 32
        assert len(salt1) == 16
        
        # Same password with same salt should produce same key
        key2, _ = KeyManager.derive_key_from_password(password, salt1)
        assert key1 == key2


class TestEncryptionManager:
    """Tests for EncryptionManager"""
    
    def test_encrypt_decrypt(self, tmp_path):
        """Test basic encryption and decryption"""
        key_file = tmp_path / "test.key"
        key_manager = KeyManager(str(key_file))
        key = key_manager.generate_and_save_key()
        
        enc_manager = EncryptionManager(key=key)
        
        plaintext = "This is a test message for encryption"
        ciphertext, nonce = enc_manager.encrypt(plaintext)
        
        assert ciphertext != plaintext.encode()
        assert len(nonce) == 12
        
        decrypted = enc_manager.decrypt(ciphertext, nonce)
        assert decrypted == plaintext
    
    def test_encrypt_decrypt_base64(self, tmp_path):
        """Test base64 encryption and decryption"""
        key_file = tmp_path / "test.key"
        key_manager = KeyManager(str(key_file))
        key = key_manager.generate_and_save_key()
        
        enc_manager = EncryptionManager(key=key)
        
        plaintext = "Test message with 中文字符"
        encrypted_b64 = enc_manager.encrypt_to_base64(plaintext)
        
        assert isinstance(encrypted_b64, str)
        
        decrypted = enc_manager.decrypt_from_base64(encrypted_b64)
        assert decrypted == plaintext
    
    def test_encrypt_batch(self, tmp_path):
        """Test batch encryption"""
        key_file = tmp_path / "test.key"
        key_manager = KeyManager(str(key_file))
        key = key_manager.generate_and_save_key()
        
        enc_manager = EncryptionManager(key=key)
        
        texts = ["Text 1", "Text 2", "Text 3"]
        encrypted_batch = enc_manager.encrypt_batch(texts)
        
        assert len(encrypted_batch) == len(texts)
        
        decrypted_batch = enc_manager.decrypt_batch(encrypted_batch)
        assert decrypted_batch == texts
    
    def test_different_nonces(self, tmp_path):
        """Test that different encryptions produce different nonces"""
        key_file = tmp_path / "test.key"
        key_manager = KeyManager(str(key_file))
        key = key_manager.generate_and_save_key()
        
        enc_manager = EncryptionManager(key=key)
        
        plaintext = "Same message"
        ciphertext1, nonce1 = enc_manager.encrypt(plaintext)
        ciphertext2, nonce2 = enc_manager.encrypt(plaintext)
        
        assert nonce1 != nonce2
        assert ciphertext1 != ciphertext2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
