from cryptography.fernet import Fernet
import os
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get encryption key from environment variable
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

# Initialize Fernet cipher
if ENCRYPTION_KEY:
    # Ensure the key is properly formatted (32 url-safe base64-encoded bytes)
    if len(ENCRYPTION_KEY) < 32:
        ENCRYPTION_KEY = ENCRYPTION_KEY.ljust(32, '0')
    elif len(ENCRYPTION_KEY) > 32:
        ENCRYPTION_KEY = ENCRYPTION_KEY[:32]
    
    # Convert to bytes and encode to base64
    key = base64.urlsafe_b64encode(ENCRYPTION_KEY.encode())
    cipher = Fernet(key)
else:
    # Generate a key if not provided (for development only)
    key = Fernet.generate_key()
    cipher = Fernet(key)
    print("WARNING: Using a generated encryption key. Set ENCRYPTION_KEY in .env for production.")

def encrypt_data(data: str) -> str:
    """Encrypt sensitive data"""
    if not data:
        return None
    encrypted_data = cipher.encrypt(data.encode())
    return encrypted_data.decode()

def decrypt_data(encrypted_data: str) -> str:
    """Decrypt sensitive data"""
    if not encrypted_data:
        return None
    decrypted_data = cipher.decrypt(encrypted_data.encode())
    return decrypted_data.decode()
