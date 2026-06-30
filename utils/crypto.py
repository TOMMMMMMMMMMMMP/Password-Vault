from cryptography.fernet import Fernet
import os

KEY_FILE = "secret.key"


class CryptoManager:
    """Handles encryption and decryption of sensitive data using Fernet."""

    def __init__(self):
        self.key = self._load_or_create_key()
        self.fernet = Fernet(self.key)

    def _load_or_create_key(self) -> bytes:
        """Load the encryption key from disk, or create a new one if none exists."""
        if os.path.exists(KEY_FILE):
            with open(KEY_FILE, "rb") as f:
                return f.read()
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
        return key

    def encrypt(self, plain_text: str) -> str:
        """Encrypt a plain text string and return it as a string."""
        return self.fernet.encrypt(plain_text.encode()).decode()

    def decrypt(self, encrypted_text: str) -> str:
        """Decrypt an encrypted string and return the original plain text."""
        return self.fernet.decrypt(encrypted_text.encode()).decode()
