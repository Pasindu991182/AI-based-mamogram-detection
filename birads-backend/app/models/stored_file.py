"""A patient image (original view, mask or overlay) held encrypted in the database."""
from sqlalchemy import Integer, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class StoredFile(Base, TimestampMixin):
    __tablename__ = "stored_files"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Logical path, e.g. "cases/12/cc.png" — what the signed /uploads URL names.
    path: Mapped[str] = mapped_column(String(512), unique=True, index=True)
    content_type: Mapped[str] = mapped_column(String(128), default="image/png")
    size: Mapped[int] = mapped_column(Integer)  # plaintext bytes
    # AES-256-GCM: 12-byte nonce followed by ciphertext + tag. Deferred so that
    # touching a row never drags megabytes of image data along by accident.
    data: Mapped[bytes] = mapped_column(LargeBinary, deferred=True)
