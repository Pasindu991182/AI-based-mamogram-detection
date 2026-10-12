"""Append-only security audit trail (sign-ins, account changes)."""
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Who did it. The email is a snapshot so the trail survives account removal,
    # and records the address tried on a failed sign-in to an unknown account.
    actor_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    actor_email: Mapped[str] = mapped_column(String(320), default="")
    action: Mapped[str] = mapped_column(String(48), index=True)
    target: Mapped[str] = mapped_column(String(320), default="")  # e.g. affected user
    ip_address: Mapped[str] = mapped_column(String(64), default="")
