"""Authentication helpers: Google ID-token verification and app JWTs."""
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from fastapi import HTTPException, status
from jose import JWTError, jwt

from app.core.config import settings


# --------------------------------------------------------------------------
# App JWT issuance / decoding
# --------------------------------------------------------------------------
def create_access_token(subject: str, extra: Optional[dict] = None) -> str:
    """Issue a signed application JWT for an authenticated user."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload: dict[str, Any] = {"sub": subject, "exp": expire}
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# --------------------------------------------------------------------------
# Google ID-token verification
# --------------------------------------------------------------------------
def verify_google_id_token(id_token_str: str) -> dict:
    """Validate a Google OAuth ID token and return the user claims.

    Returns a dict with at least: sub, email, name, picture.
    """
    # Imported lazily so the rest of the app loads even if the lib is absent.
    from google.auth.transport import requests as google_requests
    from google.oauth2 import id_token as google_id_token

    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GOOGLE_CLIENT_ID is not configured on the server.",
        )

    try:
        claims = google_id_token.verify_oauth2_token(
            id_token_str,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google ID token.",
        )

    if claims.get("iss") not in ("accounts.google.com", "https://accounts.google.com"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Untrusted token issuer.",
        )

    return {
        "sub": claims["sub"],
        "email": claims.get("email", ""),
        "name": claims.get("name", ""),
        "picture": claims.get("picture", ""),
        "email_verified": claims.get("email_verified", False),
    }
