from datetime import datetime, timedelta, timezone
from typing import Any
import jwt
import bcrypt
import uuid
from app.config.settings import settings

ALGORITHM = "HS256"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain text password against a stored bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Generates a secure BCrypt hash for a plain text password."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def create_access_token(
    subject: str | Any, expires_delta: timedelta | None = None
) -> str:
    """Generates a signed JWT access token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Default duration
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "access",
        "jti": str(uuid.uuid4()),
    }
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(
    subject: str | Any, expires_delta: timedelta | None = None
) -> str:
    """Generates a signed JWT refresh token for session recovery."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Default 7 days
        expire = datetime.now(timezone.utc) + timedelta(days=7)

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "refresh",
        "jti": str(uuid.uuid4()),
    }
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=ALGORITHM
    )
    return encoded_jwt
