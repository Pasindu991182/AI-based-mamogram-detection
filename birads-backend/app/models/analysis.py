"""Tier 1-3 output: segmentation mask + 6 radiomics + BI-RADS category."""
from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Analysis(Base, TimestampMixin):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), index=True)

    mask_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    overlay_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    # 6 worst-case radiomic features (Tier 2)
    circularity: Mapped[float | None] = mapped_column(Float, nullable=True)
    margin_integrity: Mapped[float | None] = mapped_column(Float, nullable=True)
    orientation_index: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_diameter: Mapped[float | None] = mapped_column(Float, nullable=True)
    contrast_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)
    density_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Tier 3
    birads_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    birads_label: Mapped[str | None] = mapped_column(String(64), nullable=True)
    predicted_acr: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Full per-view JSON payload (string) for traceability
    raw_payload: Mapped[str | None] = mapped_column(Text, nullable=True)

    case: Mapped["Case"] = relationship(back_populates="analysis")  # noqa: F821
