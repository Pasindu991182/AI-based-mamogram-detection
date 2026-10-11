"""User account, created from a verified Google identity."""
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    google_sub: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(320), index=True)
    name: Mapped[str] = mapped_column(String(255), default="")
    picture: Mapped[str] = mapped_column(String(1024), default="")
    role: Mapped[str] = mapped_column(String(32), default="radiologist")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    cases: Mapped[list["Case"]] = relationship(  # noqa: F821
        back_populates="owner", cascade="all, delete-orphan"
    )
