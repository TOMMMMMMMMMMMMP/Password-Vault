from dataclasses import dataclass


@dataclass
class Credential:
    """Represents a single credential entry in the vault."""
    id: int
    site: str
    username: str
    password: str
    notes: str = ""
