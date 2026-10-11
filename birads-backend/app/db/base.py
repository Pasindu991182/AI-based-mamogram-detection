"""SQLAlchemy declarative base + common mixins."""
from datetime import datetime, timezone

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
    )


# Import models here so Alembic autogenerate / create_all sees every table.
def import_models() -> None:  # pragma: no cover - side-effect import
    from app.models import analysis, case, er_prediction, report, user  # noqa: F401
