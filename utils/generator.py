import secrets
import string


class PasswordGenerator:
    """Generates cryptographically secure random passwords."""

    def generate(self, length: int = 16, use_symbols: bool = True) -> str:
        """
        Generate a strong random password.
        Args:
            length: Length of the password (min 8)
            use_symbols: Whether to include special characters
        """
        if length < 8:
            length = 8

        chars = string.ascii_letters + string.digits
        if use_symbols:
            chars += string.punctuation

        while True:
            password = "".join(secrets.choice(chars) for _ in range(length))
            has_upper = any(c.isupper() for c in password)
            has_lower = any(c.islower() for c in password)
            has_digit = any(c.isdigit() for c in password)
            if has_upper and has_lower and has_digit:
                return password
