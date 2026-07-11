"""Tier 4 output: the NLP / template-generated radiology report."""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Report(Base, TimestampMixin):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), index=True)

    generated_text: Mapped[str] = mapped_column(Text, default="")
    edited_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    generator: Mapped[str] = mapped_column(String(32), default="template")  # template|t5
    finalized_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    case: Mapped["Case"] = relationship(back_populates="report")  # noqa: F821
