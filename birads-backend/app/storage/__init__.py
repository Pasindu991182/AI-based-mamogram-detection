"""Storage factory. Patient images live encrypted in the database by default."""
from functools import lru_cache

from app.core.config import settings
from app.storage.base import StorageBackend


@lru_cache
def get_storage() -> StorageBackend:
    if settings.STORAGE_BACKEND == "local":
        from app.storage.local_storage import LocalStorage

        return LocalStorage()

    from app.storage.database_storage import DatabaseStorage

    return DatabaseStorage()
