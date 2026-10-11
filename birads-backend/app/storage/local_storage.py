"""Filesystem storage for development. Files are served via /uploads."""
from pathlib import Path

from app.core.config import settings
from app.storage.base import StorageBackend


class LocalStorage(StorageBackend):
    def __init__(self) -> None:
        self.root = Path(settings.LOCAL_STORAGE_DIR)
        self.root.mkdir(parents=True, exist_ok=True)

    def save_bytes(self, data: bytes, filename: str, content_type: str = "image/png") -> str:
        path = self.root / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        # URL path served by StaticFiles mount in main.py
        return f"/uploads/{filename}"
