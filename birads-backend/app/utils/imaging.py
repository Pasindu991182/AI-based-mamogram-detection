"""Image I/O and preprocessing helpers shared by the CV tiers.

Ported and cleaned up from the original demo's utils/image_processing.py.
"""
import base64

import cv2
import numpy as np


def decode_upload(contents: bytes) -> np.ndarray:
    """Decode raw uploaded bytes into a BGR image array."""
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Invalid or unsupported image file.")
    return img


def to_clahe_gray(img: np.ndarray, size: int = 256) -> np.ndarray:
    """Resize to (size, size), grayscale, and apply CLAHE contrast."""
    resized = cv2.resize(img, (size, size))
    gray = (
        cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        if resized.ndim == 3
        else resized
    )
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    return clahe.apply(gray)


def png_to_base64(img: np.ndarray) -> str:
    """Encode an image array as base64 PNG string."""
    _, buffer = cv2.imencode(".png", img)
    return base64.b64encode(buffer).decode("utf-8")


def base64_to_png_bytes(b64: str) -> bytes:
    """Decode a base64 PNG string back into raw bytes (for storage upload)."""
    return base64.b64decode(b64)
