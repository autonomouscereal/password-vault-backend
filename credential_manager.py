# credential_manager.py
import os

class CredentialManager:
    @staticmethod
    def get_db_credentials():
        return {
            'user': os.getenv('db_username', 'db_username'),
            'password': os.getenv('db_password', 'db_password'),
            'database': os.getenv('password_vault_db', 'password_vault_db'),
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', 5999),
        }

    @staticmethod
    def get_secret_key():
        # This should be a secure random key
        return os.getenv('SECRET_KEY', 'reallysecretkey')

    @staticmethod
    def get_encryption_key():
        # Key used for encryption/decryption
        return os.getenv('ENCRYPTION_KEY', 'your_encryption_key')
