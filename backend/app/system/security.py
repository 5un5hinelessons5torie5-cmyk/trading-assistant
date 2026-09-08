import base64
import os
import logging
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# The encryption key must never be a fixed, hardcoded value (that would be
# public the moment this source code is). Prefer an explicit
# WORKSTATION_SECRET environment variable; if none is set, generate a
# random key on first run and persist it to a local, git-ignored file so
# it never leaves this machine.
_SECRET_FILE = Path(__file__).resolve().parent.parent.parent / ".workstation_secret"

def _load_or_create_secret() -> str:
    env_secret = os.getenv("WORKSTATION_SECRET")
    if env_secret:
        return env_secret
    if _SECRET_FILE.exists():
        return _SECRET_FILE.read_text().strip()
    generated = base64.urlsafe_b64encode(os.urandom(32)).decode()
    _SECRET_FILE.write_text(generated)
    return generated

SECRET_KEY = _load_or_create_secret()

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
