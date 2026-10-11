"""A patient case: the unit of work tying together all 5 tiers."""
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Case(Base, TimestampMixin):
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    patient_ref: Mapped[str] = mapped_column(String(64), default="")  # anonymised id
    patient_age: Mapped[int | None] = mapped_column(nullable=True)

    cc_image_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    mlo_image_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    # draft | analyzed | reported | completed
    status: Mapped[str] = mapped_column(String(32), default="draft")

    owner: Mapped["User"] = relationship(back_populates="cases")  # noqa: F821
    analysis: Mapped["Analysis | None"] = relationship(  # noqa: F821
        back_populates="case", cascade="all, delete-orphan", uselist=False
    )
    report: Mapped["Report | None"] = relationship(  # noqa: F821
        back_populates="case", cascade="all, delete-orphan", uselist=False
    )
    er_prediction: Mapped["ERPrediction | None"] = relationship(  # noqa: F821
        back_populates="case", cascade="all, delete-orphan", uselist=False
    )
