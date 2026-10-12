"""Plain filesystem storage. Unencrypted — for local debugging only."""
import shutil
from pathlib import Path

from app.core.config import settings
from app.storage.base import StorageBackend


class LocalStorage(StorageBackend):
    def __init__(self) -> None:
        self.root = Path(settings.LOCAL_STORAGE_DIR).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _resolve(self, filename: str) -> Path | None:
        """Map a logical path into the root, refusing `../` traversal."""
        target = (self.root / filename).resolve()
        return target if target.is_relative_to(self.root) else None

    def save_bytes(self, data: bytes, filename: str, content_type: str = "image/png") -> str:
        path = self._resolve(filename)
        if path is None:
            raise ValueError("Invalid storage path.")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return f"/uploads/{filename}"

    def read_bytes(self, filename: str) -> tuple[bytes, str] | None:
        path = self._resolve(filename)
        if path is None or not path.is_file():
            return None
        return path.read_bytes(), "image/png"

    def delete_prefix(self, prefix: str) -> None:
        path = self._resolve(prefix)
        if path is not None and path != self.root and path.is_dir():
            shutil.rmtree(path)
