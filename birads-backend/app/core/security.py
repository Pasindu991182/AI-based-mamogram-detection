"""Authentication helpers: password hashing, app JWTs and refresh tokens."""
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from fastapi import HTTPException, status

from app.core.config import settings

# Argon2id with the library's (RFC 9106 low-memory) defaults.
_hasher = PasswordHasher()

# Verified against when the email is unknown, so a login attempt costs the
# same time whether or not the account exists.
_DUMMY_HASH = _hasher.hash(secrets.token_urlsafe(16))

PASSWORD_MAX_LENGTH = 128


# --------------------------------------------------------------------------
# Passwords
# --------------------------------------------------------------------------
def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str | None) -> bool:
    """Constant-shape check; a missing hash still burns one verification."""
    try:
        return _hasher.verify(password_hash or _DUMMY_HASH, password) and bool(
            password_hash
        )
    except (VerificationError, InvalidHashError):
        return False


def password_needs_rehash(password_hash: str) -> bool:
    return _hasher.check_needs_rehash(password_hash)


def password_policy_error(password: str, email: str = "") -> str | None:
    """Return why `password` is unacceptable, or None when it passes."""
    if len(password) < settings.PASSWORD_MIN_LENGTH:
        return f"Password must be at least {settings.PASSWORD_MIN_LENGTH} characters."
    if len(password) > PASSWORD_MAX_LENGTH:
        return f"Password must be at most {PASSWORD_MAX_LENGTH} characters."
    if not any(c.isalpha() for c in password) or not any(c.isdigit() for c in password):
        return "Password must contain both letters and numbers."
    local_part = email.split("@")[0].lower()
    if len(local_part) >= 4 and local_part in password.lower():
        return "Password must not contain your email name."
    return None


# --------------------------------------------------------------------------
# App JWT issuance / decoding
# --------------------------------------------------------------------------
def create_access_token(subject: str, extra: Optional[dict] = None) -> str:
    """Issue a signed, short-lived application JWT for an authenticated user."""
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        "type": "access",
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            options={"require": ["exp", "sub"]},
        )
    except jwt.PyJWTError:
        payload = None
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


# --------------------------------------------------------------------------
# Refresh tokens (opaque; only their SHA-256 is stored server-side)
# --------------------------------------------------------------------------
def new_refresh_token() -> tuple[str, str]:
    """Return (raw_token_for_cookie, hash_for_database)."""
    raw = secrets.token_urlsafe(48)
    return raw, hash_refresh_token(raw)


def hash_refresh_token(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()
