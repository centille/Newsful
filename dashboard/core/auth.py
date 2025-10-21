from argon2 import PasswordHasher


# Removed custom create_salt, now handled by argon2 internally

ph = PasswordHasher()

def hash_password(password: str) -> str:
    """Hash a password using Argon2."""
    return ph.hash(password)


def check_password(password: str, hashed_password: str) -> bool:
    """Check if a password is correct using Argon2."""
    try:
        return ph.verify(hashed_password, password)
    except Exception:
        return False
