"""Storage abstraction so the rest of the app never hard-codes a provider."""
from abc import ABC, abstractmethod


class StorageBackend(ABC):
    @abstractmethod
    def save_bytes(self, data: bytes, filename: str, content_type: str = "image/png") -> str:
        """Persist raw bytes and return a publicly retrievable URL (or path)."""
        raise NotImplementedError
