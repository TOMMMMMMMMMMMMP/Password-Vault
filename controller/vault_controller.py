from model.database import VaultDB
from model.credential import Credential
from utils.auth import MasterAuth
from utils.generator import PasswordGenerator


class VaultController:
    """Bridges the GUI views and the Model (VaultDB, Auth, Generator)."""

    def __init__(self):
        self.auth = MasterAuth()
        self.db = VaultDB()
        self.generator = PasswordGenerator()

    def is_first_launch(self) -> bool:
        """Return True if no master password has been configured yet."""
        return not self.auth.is_setup()

    def setup_master(self, password: str) -> tuple[bool, str]:
        """Set up the master password for the first time."""
        if len(password) < 6:
            return False, "Master password must be at least 6 characters."
        try:
            self.auth.setup(password)
            return True, "Master password configured."
        except Exception as e:
            return False, str(e)

    def verify_master(self, password: str) -> tuple[bool, str]:
        """Verify the master password."""
        if self.auth.verify(password):
            return True, "Access granted."
        return False, "Wrong master password."

    def get_all(self) -> list[Credential]:
        """Return all credentials from the vault."""
        return self.db.get_all_credentials()

    def search(self, keyword: str) -> list[Credential]:
        """Search credentials by site or username."""
        return self.db.search_credentials(keyword)

    def add(self, site: str, username: str, password: str, notes: str = "") -> tuple[bool, str]:
        """Add a new credential with validation."""
        if not site.strip():
            return False, "Site cannot be empty."
        if not username.strip():
            return False, "Username cannot be empty."
        if not password.strip():
            return False, "Password cannot be empty."
        try:
            self.db.add_credential(site.strip(), username.strip(), password.strip(), notes.strip())
            return True, "Credential added successfully."
        except Exception as e:
            return False, str(e)

    def update(self, id: int, site: str, username: str, password: str, notes: str = "") -> tuple[bool, str]:
        """Update an existing credential with validation."""
        if not site.strip() or not username.strip() or not password.strip():
            return False, "Site, username and password cannot be empty."
        result = self.db.update_credential(id, site.strip(), username.strip(), password.strip(), notes.strip())
        if result:
            return True, "Credential updated."
        return False, f"No credential found with ID {id}."

    def delete(self, id: int) -> tuple[bool, str]:
        """Delete a credential by ID."""
        result = self.db.delete_credential(id)
        if result:
            return True, "Credential deleted."
        return False, f"No credential found with ID {id}."

    def generate_password(self, length: int = 16, use_symbols: bool = True) -> str:
        """Generate a strong random password."""
        return self.generator.generate(length, use_symbols)

    def export_vault(self) -> tuple[bool, str]:
        """Export all credentials to an encrypted txt file."""
        from utils.crypto import CryptoManager
        import datetime
        creds = self.db.get_all_credentials()
        if not creds:
            return False, "No credentials to export."
        try:
            crypto = CryptoManager()
            lines = [f"=== Password Vault Export — {datetime.datetime.now()} ===\n"]
            for c in creds:
                lines.append(f"Site: {c.site}")
                lines.append(f"Username: {c.username}")
                lines.append(f"Password: {c.password}")
                lines.append(f"Notes: {c.notes}")
                lines.append("-" * 40)
            plain = "\n".join(lines)
            encrypted = crypto.encrypt(plain)
            filename = f"vault_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, "w") as f:
                f.write(encrypted)
            return True, f"Exported to {filename}"
        except Exception as e:
            return False, str(e)
