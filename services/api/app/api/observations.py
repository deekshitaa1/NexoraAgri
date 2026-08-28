from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.field_observation import FieldObservation
from app.services.observation_ingestion import store_observation


router = APIRouter(
    prefix="/observations",
    tags=["Field Observations"],
)


class ObservationCreate(BaseModel):
    field_id: UUID
    observed_at: datetime

    soil_moisture: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    soil_temperature: float | None = None
    air_temperature: float | None = None

    humidity: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    rainfall_mm: float | None = Field(
        default=None,
        ge=0,
    )

    source: str = Field(
        default="manual",
        min_length=1,
        max_length=50,
    )


class ObservationRead(ObservationCreate):
    id: UUID
    created_at: datetime


@router.post(
    "",
    response_model=ObservationRead,
    status_code=status.HTTP_201_CREATED,
)
def create_observation(
    payload: ObservationCreate,
    db: Session = Depends(get_db),
):
    return store_observation(
        db,
        field_id=payload.field_id,
        observed_at=payload.observed_at,
        soil_moisture=payload.soil_moisture,
        soil_temperature=payload.soil_temperature,
        air_temperature=payload.air_temperature,
        humidity=payload.humidity,
        rainfall_mm=payload.rainfall_mm,
        source=payload.source,
    )


@router.get(
    "",
    response_model=list[ObservationRead],
)
def list_observations(
    field_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
):
    statement = select(FieldObservation).order_by(
        FieldObservation.observed_at.desc()
    )

    if field_id is not None:
        statement = statement.where(
            FieldObservation.field_id == field_id
        )

    return db.scalars(statement).all()
