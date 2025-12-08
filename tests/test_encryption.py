"""Tests for encryption module."""
import pytest
from src.encryption import AESEncryption, generate_key


class TestAESEncryption:
    """Test AES encryption functionality."""
    
    def test_key_generation(self):
        """Test key generation."""
        key = generate_key()
        assert len(key) == 32  # 256 bits
    
    def test_encryption_decryption(self):
        """Test basic encryption and decryption."""
        key = generate_key()
        encryptor = AESEncryption(key)
        
        plaintext = "This is a test message."
        
        # Encrypt
        ciphertext = encryptor.encrypt(plaintext)
        assert ciphertext != plaintext
        assert len(ciphertext) > 0
        
        # Decrypt
        decrypted = encryptor.decrypt(ciphertext)
        assert decrypted == plaintext
    
    def test_empty_string(self):
        """Test encryption of empty string."""
        key = generate_key()
        encryptor = AESEncryption(key)
        
        plaintext = ""
        ciphertext = encryptor.encrypt(plaintext)
        decrypted = encryptor.decrypt(ciphertext)
        
        assert decrypted == plaintext
    
    def test_unicode_text(self):
        """Test encryption of unicode text."""
        key = generate_key()
        encryptor = AESEncryption(key)
        
        plaintext = "你好，世界！こんにちは世界！"
        ciphertext = encryptor.encrypt(plaintext)
        decrypted = encryptor.decrypt(ciphertext)
        
        assert decrypted == plaintext
    
    def test_long_text(self):
        """Test encryption of long text."""
        key = generate_key()
        encryptor = AESEncryption(key)
        
        plaintext = "A" * 10000
        ciphertext = encryptor.encrypt(plaintext)
        decrypted = encryptor.decrypt(ciphertext)
        
        assert decrypted == plaintext
    
    def test_different_keys(self):
        """Test that different keys produce different ciphertexts."""
        key1 = generate_key()
        key2 = generate_key()
        
        encryptor1 = AESEncryption(key1)
        encryptor2 = AESEncryption(key2)
        
        plaintext = "Test message"
        
        ciphertext1 = encryptor1.encrypt(plaintext)
        ciphertext2 = encryptor2.encrypt(plaintext)
        
        # Different keys should produce different ciphertexts
        assert ciphertext1 != ciphertext2
        
        # Decryption with wrong key should fail
        with pytest.raises(Exception):
            encryptor1.decrypt(ciphertext2)
