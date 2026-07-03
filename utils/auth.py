import hashlib
import os
import json

AUTH_FILE = "master.json"


class MasterAuth:
    """
    Handles master password hashing and verification.
    Uses SHA-256 with a random salt for secure storage.
    """

    def __init__(self):
        self.auth_file = AUTH_FILE

    def _hash(self, password: str, salt: bytes) -> str:
        """Hash a password with a given salt using SHA-256."""
        return hashlib.sha256(salt + password.encode()).hexdigest()

    def is_setup(self) -> bool:
        """Return True if a master password has already been configured."""
        return os.path.exists(self.auth_file)

    def setup(self, password: str) -> None:
        """
        Create and store a new master password hash.
        Raises ValueError if a master password already exists.
        """
        if self.is_setup():
            raise ValueError("Master password already configured.")
        salt = os.urandom(16)
        hashed = self._hash(password, salt)
        with open(self.auth_file, "w") as f:
            json.dump({
                "salt": salt.hex(),
                "hash": hashed
            }, f)

    def verify(self, password: str) -> bool:
        """Verify a password against the stored master hash."""
        if not self.is_setup():
            raise FileNotFoundError("No master password configured.")
        with open(self.auth_file, "r") as f:
            data = json.load(f)
        salt = bytes.fromhex(data["salt"])
        return self._hash(password, salt) == data["hash"]
