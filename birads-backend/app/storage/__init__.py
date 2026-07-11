"""Storage factory — pick the backend from settings."""
from functools import lru_cache

from app.core.config import settings
from app.storage.base import StorageBackend


@lru_cache
def get_storage() -> StorageBackend:
    if settings.STORAGE_BACKEND == "cloudinary":
        from app.storage.cloudinary_storage import CloudinaryStorage

        return CloudinaryStorage()
    from app.storage.local_storage import LocalStorage

    return LocalStorage()
