import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class GrowingSeason(Base):
    __tablename__ = "growing_seasons"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    field_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("fields.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    crop_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("crops.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    season_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    planting_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    expected_harvest_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
