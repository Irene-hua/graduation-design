"""
Encryption demonstration
加密演示
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.encryption import EncryptionManager, KeyManager


def main():
    print("=" * 80)
    print("Encryption Module Demonstration")
    print("=" * 80)
    
    # Generate encryption key
    print("\n1. Generating encryption key...")
    key_manager = KeyManager()
    key = key_manager.generate_key()
    print(f"✓ Key generated (256-bit): {len(key) * 8} bits")
    
    # Initialize encryption manager
    print("\n2. Initializing encryption manager...")
    enc_manager = EncryptionManager(key=key)
    print("✓ Encryption manager ready")
    
    # Encrypt text
    print("\n3. Encrypting sample text...")
    original_text = "This is sensitive information that needs to be protected. 这是需要保护的敏感信息。"
    print(f"Original text: {original_text}")
    
    encrypted_b64 = enc_manager.encrypt_to_base64(original_text)
    print(f"Encrypted (base64): {encrypted_b64[:50]}...")
    
    # Decrypt text
    print("\n4. Decrypting text...")
    decrypted_text = enc_manager.decrypt_from_base64(encrypted_b64)
    print(f"Decrypted text: {decrypted_text}")
    
    # Verify
    print("\n5. Verification:")
    if original_text == decrypted_text:
        print("✓ Encryption/decryption successful - text matches!")
    else:
        print("✗ Error - text does not match!")
    
    # Batch encryption
    print("\n6. Batch encryption demonstration...")
    texts = [
        "Document chunk 1",
        "Document chunk 2",
        "Document chunk 3"
    ]
    
    print(f"Encrypting {len(texts)} texts...")
    encrypted_batch = enc_manager.encrypt_batch(texts)
    print(f"✓ {len(encrypted_batch)} texts encrypted")
    
    print("Decrypting batch...")
    decrypted_batch = enc_manager.decrypt_batch(encrypted_batch)
    print(f"✓ {len(decrypted_batch)} texts decrypted")
    
    if texts == decrypted_batch:
        print("✓ Batch encryption/decryption successful!")
    else:
        print("✗ Batch verification failed!")
    
    print("\n" + "=" * 80)
    print("Encryption demonstration completed!")
    print("=" * 80)


if __name__ == '__main__':
    main()
