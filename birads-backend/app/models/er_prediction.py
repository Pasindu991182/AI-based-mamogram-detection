"""Tier 5 output: ER status prediction from 7 basic clinical inputs."""
from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class ERPrediction(Base, TimestampMixin):
    __tablename__ = "er_predictions"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), index=True)

    # 7 inputs
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tumor_size: Mapped[float | None] = mapped_column(Float, nullable=True)
    histologic_grade: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cellularity: Mapped[str | None] = mapped_column(String(32), nullable=True)
    menopausal_state: Mapped[str | None] = mapped_column(String(32), nullable=True)
    histologic_subtype: Mapped[str | None] = mapped_column(String(64), nullable=True)
    lymph_nodes_positive: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Outputs
    er_result: Mapped[str | None] = mapped_column(String(16), nullable=True)  # ER+/ER-
    confidence: Mapped[str | None] = mapped_column(String(16), nullable=True)
    probability_positive: Mapped[float | None] = mapped_column(Float, nullable=True)
    model_version: Mapped[str] = mapped_column(String(32), default="stub")

    case: Mapped["Case"] = relationship(back_populates="er_prediction")  # noqa: F821
