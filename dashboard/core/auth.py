import hashlib
import secrets
from typing import Tuple, Union


def create_salt(n: int = 6) -> str:
    """Create a random string of length n."""
    return secrets.token_hex(n)


def hash_password(
    password: str, salt: Union[str, None] = None, n: int = 50
) -> Tuple[str, str]:
    """Hash a password with a salt."""

    # Create a salt if none is provided
    if salt is None:
        salt = create_salt()
    # Hash the password with the salt
    for _ in range(n):  # n rounds of hashing
        password = hashlib.sha512((password + salt).encode("utf-8")).hexdigest()
    return password, salt


def check_password(password: str, hashed_password: str, salt: str) -> bool:
    """Check if a password is correct."""
    return hash_password(password, salt)[0] == hashed_password
