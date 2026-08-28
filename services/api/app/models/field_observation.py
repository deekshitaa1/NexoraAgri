import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class FieldObservation(Base):
    __tablename__ = "field_observations"

    __table_args__ = (
        UniqueConstraint(
            "field_id",
            "observed_at",
            name="uq_field_observation_field_time",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    field_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("fields.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    soil_moisture: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    soil_temperature: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    air_temperature: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    humidity: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    rainfall_mm: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
