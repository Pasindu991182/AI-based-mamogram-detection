"""Storage abstraction so the rest of the app never hard-codes a provider."""
from abc import ABC, abstractmethod


class StorageBackend(ABC):
    @abstractmethod
    def save_bytes(self, data: bytes, filename: str, content_type: str = "image/png") -> str:
        """Persist raw bytes under `filename` and return its `/uploads/...` path."""
        raise NotImplementedError

    @abstractmethod
    def read_bytes(self, filename: str) -> tuple[bytes, str] | None:
        """Return (data, content_type), or None when nothing is stored there."""
        raise NotImplementedError

    @abstractmethod
    def delete_prefix(self, prefix: str) -> None:
        """Remove everything stored under `prefix` (e.g. "cases/12/")."""
        raise NotImplementedError
