import base64
import os
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# For a production system, the key should come from an environment variable
# or a secure vault. We use a stable derivation for this workstation demo.
SECRET_KEY = os.getenv("WORKSTATION_SECRET", "super-secret-dev-key")

def get_cipher():
    salt = b'trading-workstation-salt'
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(SECRET_KEY.encode()))
    return Fernet(key)

def encrypt_password(password: str) -> str:
    if not password: return ""
    cipher = get_cipher()
    return cipher.encrypt(password.encode()).decode()

def decrypt_password(encrypted: str) -> str:
    if not encrypted: return ""
    try:
        cipher = get_cipher()
        return cipher.decrypt(encrypted.encode()).decode()
    except Exception as e:
        logging.error(f"Decryption error: {e}")
        return ""
