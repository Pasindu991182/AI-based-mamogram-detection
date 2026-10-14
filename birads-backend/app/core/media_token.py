"""Short-lived signed URLs for locally stored patient images.

Images are held encrypted by the storage backend and are never served by a
public static mount: a browser can only fetch one with a valid, unexpired HMAC
signature. Signatures are minted at response time (see schemas/case.py), so a
URL copied out of the page stops working once it expires.
"""
import hashlib
import hmac
import time
from urllib.parse import quote, urlencode

from app.core.config import settings

# Derived from the app secret so media links are invalidated along with
# sessions if JWT_SECRET is ever rotated.
_MEDIA_KEY = hashlib.sha256(f"media:{settings.JWT_SECRET}".encode()).digest()

MEDIA_URL_PREFIX = "/uploads/"


def _digest(rel_path: str, expires_at: int) -> str:
    msg = f"{rel_path}:{expires_at}".encode()
    return hmac.new(_MEDIA_KEY, msg, hashlib.sha256).hexdigest()


def sign_media_path(rel_path: str, ttl_seconds: int | None = None) -> str:
    """Return `/uploads/<rel_path>?exp=..&sig=..` valid for a limited window."""
    ttl = ttl_seconds or settings.MEDIA_URL_TTL_SECONDS
    expires_at = int(time.time()) + ttl
    query = urlencode({"exp": expires_at, "sig": _digest(rel_path, expires_at)})
    return f"{MEDIA_URL_PREFIX}{quote(rel_path)}?{query}"


def verify_media_token(rel_path: str, expires_at: int, signature: str) -> bool:
    if expires_at < int(time.time()):
        return False
    return hmac.compare_digest(_digest(rel_path, expires_at), signature)


def to_signed_url(stored_url: str | None) -> str | None:
    """Re-sign a stored `/uploads/...` value for this response.

    Anything else (an absolute URL from a previous storage backend, or None)
    is passed through untouched.
    """
    if not stored_url or not stored_url.startswith(MEDIA_URL_PREFIX):
        return stored_url
    return sign_media_path(stored_url[len(MEDIA_URL_PREFIX):])
