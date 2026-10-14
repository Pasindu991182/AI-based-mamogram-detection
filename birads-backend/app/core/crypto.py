"""Encryption at rest for patient images (AES-256-GCM).

Each blob gets a fresh random nonce and is bound to its storage path as
associated data, so a ciphertext copied onto another row fails to decrypt.
"""
import base64
import hashlib
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_NONCE_BYTES = 12


def _load_key() -> bytes:
    if settings.DATA_ENCRYPTION_KEY:
        key = base64.urlsafe_b64decode(settings.DATA_ENCRYPTION_KEY)
        if len(key) != 32:
            raise ValueError("DATA_ENCRYPTION_KEY must be 32 bytes, base64url-encoded.")
        return key
    # Development convenience only (production refuses to start without a key):
    # images become unreadable if JWT_SECRET is later changed.
    logger.warning("DATA_ENCRYPTION_KEY is not set; deriving one from JWT_SECRET.")
    return hashlib.sha256(f"data:{settings.JWT_SECRET}".encode()).digest()


_aead = AESGCM(_load_key())


def encrypt(plaintext: bytes, context: str) -> bytes:
    nonce = os.urandom(_NONCE_BYTES)
    return nonce + _aead.encrypt(nonce, plaintext, context.encode())


def decrypt(blob: bytes, context: str) -> bytes:
    """Raises cryptography.exceptions.InvalidTag if the data was tampered with."""
    return _aead.decrypt(blob[:_NONCE_BYTES], blob[_NONCE_BYTES:], context.encode())
