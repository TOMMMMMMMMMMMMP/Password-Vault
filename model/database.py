import sqlite3
from model.credential import Credential
from utils.crypto import CryptoManager

DB_FILE = "vault.db"


class VaultDB:
    """Handles all SQLite database operations for the password vault."""

    def __init__(self):
        self.crypto = CryptoManager()
        self.connection = sqlite3.connect(DB_FILE)
        self._init_table()

    def _init_table(self) -> None:
        """Create the credentials table if it doesn't exist."""
        query = """
            CREATE TABLE IF NOT EXISTS credentials (
                id                INTEGER PRIMARY KEY AUTOINCREMENT,
                site              TEXT NOT NULL,
                username          TEXT NOT NULL,
                password_encrypted TEXT NOT NULL,
                notes             TEXT DEFAULT ''
            )
        """
        self.connection.execute(query)
        self.connection.commit()

    def add_credential(self, site: str, username: str, password: str, notes: str = "") -> None:
        """
        Add a new credential to the vault.
        The password is encrypted before being stored.
        """
        encrypted = self.crypto.encrypt(password)
        query = """
            INSERT INTO credentials (site, username, password_encrypted, notes)
            VALUES (?, ?, ?, ?)
        """
        self.connection.execute(query, (site, username, encrypted, notes))
        self.connection.commit()

    def get_all_credentials(self) -> list[Credential]:
        """
        Retrieve all credentials from the vault.
        Passwords are decrypted before being returned.
        """
        query = "SELECT id, site, username, password_encrypted, notes FROM credentials"
        rows = self.connection.execute(query).fetchall()
        result = []
        for row in rows:
            decrypted = self.crypto.decrypt(row[3])
            result.append(Credential(
                id=row[0],
                site=row[1],
                username=row[2],
                password=decrypted,
                notes=row[4],
            ))
        return result

    def search_credentials(self, keyword: str) -> list[Credential]:
        """Search credentials by site or username (case-insensitive)."""
        query = """
            SELECT id, site, username, password_encrypted, notes
            FROM credentials
            WHERE LOWER(site) LIKE ? OR LOWER(username) LIKE ?
        """
        keyword = f"%{keyword.lower()}%"
        rows = self.connection.execute(query, (keyword, keyword)).fetchall()
        result = []
        for row in rows:
            decrypted = self.crypto.decrypt(row[3])
            result.append(Credential(
                id=row[0],
                site=row[1],
                username=row[2],
                password=decrypted,
                notes=row[4],
            ))
        return result

    def close(self) -> None:
        """Close the database connection."""
        self.connection.close()


    def update_credential(self, id: int, site: str, username: str, password: str, notes: str = "") -> bool:
        """
        Update an existing credential by ID.
        Returns True if a record was updated, False if ID not found.
        """
        encrypted = self.crypto.encrypt(password)
        query = """
            UPDATE credentials
            SET site=?, username=?, password_encrypted=?, notes=?
            WHERE id=?
        """
        cursor = self.connection.execute(query, (site, username, encrypted, notes, id))
        self.connection.commit()
        return cursor.rowcount > 0

    def delete_credential(self, id: int) -> bool:
        """
        Delete a credential by ID.
        Returns True if a record was deleted, False if ID not found.
        """
        cursor = self.connection.execute(
            "DELETE FROM credentials WHERE id=?", (id,)
        )
        self.connection.commit()
        return cursor.rowcount > 0
