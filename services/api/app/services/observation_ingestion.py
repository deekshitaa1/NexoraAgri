from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.field_observation import FieldObservation


def store_observation(
    db: Session,
    *,
    field_id: UUID,
    observed_at: datetime,
    soil_moisture: float | None,
    soil_temperature: float | None,
    air_temperature: float | None,
    humidity: float | None,
    rainfall_mm: float | None,
    source: str,
) -> FieldObservation:
    observation = FieldObservation(
        field_id=field_id,
        observed_at=observed_at,
        soil_moisture=soil_moisture,
        soil_temperature=soil_temperature,
        air_temperature=air_temperature,
        humidity=humidity,
        rainfall_mm=rainfall_mm,
        source=source,
    )

    db.add(observation)
    db.commit()
    db.refresh(observation)

    return observation


def store_observations(
    db: Session,
    observations: list[dict],
) -> int:
    records = [
        FieldObservation(**observation)
        for observation in observations
    ]

    db.add_all(records)
    db.commit()

    return len(records)
