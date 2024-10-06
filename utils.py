# utils.py
from cryptography.fernet import Fernet
from passlib.context import CryptContext
from credential_manager import CredentialManager
import base64
import hashlib

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_encryption_key():
    # Use a fixed key for encryption/decryption
    key = CredentialManager.get_encryption_key()
    # Derive a 32-byte key for Fernet
    digest = hashlib.sha256(key.encode()).digest()
    return base64.urlsafe_b64encode(digest)

def encrypt_password(plain_text_password: str) -> str:
    key = get_encryption_key()
    f = Fernet(key)
    return f.encrypt(plain_text_password.encode()).decode()

def decrypt_password(encrypted_password: str) -> str:
    key = get_encryption_key()
    f = Fernet(key)
    return f.decrypt(encrypted_password.encode()).decode()

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
