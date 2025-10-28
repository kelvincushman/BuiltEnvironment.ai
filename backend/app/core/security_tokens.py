"""
Security tokens for email verification and password reset.

Uses JWT tokens with short expiration times for security.
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt

from .config import settings


def create_password_reset_token(email: str, expires_delta: timedelta = timedelta(hours=1)) -> str:
    """
    Create a password reset token.

    Args:
        email: User's email address
        expires_delta: Token expiration time (default: 1 hour)

    Returns:
        JWT token string
    """
    expire = datetime.utcnow() + expires_delta
    to_encode = {
        "sub": email,
        "type": "password_reset",
        "exp": expire,
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Verify a password reset token and extract email.

    Args:
        token: JWT token string

    Returns:
        Email address if token is valid, None otherwise
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        # Check token type
        if payload.get("type") != "password_reset":
            return None

        email: str = payload.get("sub")
        return email

    except JWTError:
        return None


def create_email_verification_token(email: str, expires_delta: timedelta = timedelta(hours=24)) -> str:
    """
    Create an email verification token.

    Args:
        email: User's email address
        expires_delta: Token expiration time (default: 24 hours)

    Returns:
        JWT token string
    """
    expire = datetime.utcnow() + expires_delta
    to_encode = {
        "sub": email,
        "type": "email_verification",
        "exp": expire,
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_email_verification_token(token: str) -> Optional[str]:
    """
    Verify an email verification token and extract email.

    Args:
        token: JWT token string

    Returns:
        Email address if token is valid, None otherwise
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        # Check token type
        if payload.get("type") != "email_verification":
            return None

        email: str = payload.get("sub")
        return email

    except JWTError:
        return None
