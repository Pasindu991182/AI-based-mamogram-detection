"""Patient images stored encrypted inside the application database.

Keeping them next to the case records means one access-controlled store, one
backup, and no image files readable from the server's filesystem.
"""
from app.core import crypto
from app.db.session import SessionLocal
from app.models.stored_file import StoredFile
from app.storage.base import StorageBackend


class DatabaseStorage(StorageBackend):
    def save_bytes(self, data: bytes, filename: str, content_type: str = "image/png") -> str:
        with SessionLocal() as db:
            row = db.query(StoredFile).filter(StoredFile.path == filename).first()
            if row is None:
                row = StoredFile(path=filename)
                db.add(row)
            row.content_type = content_type
            row.size = len(data)
            row.data = crypto.encrypt(data, filename)
            db.commit()
        return f"/uploads/{filename}"

    def read_bytes(self, filename: str) -> tuple[bytes, str] | None:
        with SessionLocal() as db:
            row = db.query(StoredFile).filter(StoredFile.path == filename).first()
            if row is None:
                return None
            return crypto.decrypt(row.data, filename), row.content_type

    def delete_prefix(self, prefix: str) -> None:
        with SessionLocal() as db:
            db.query(StoredFile).filter(
                StoredFile.path.startswith(prefix, autoescape=True)
            ).delete(synchronize_session=False)
            db.commit()
