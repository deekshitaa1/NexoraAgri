from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.crop import Crop
from app.models.field import Field as FieldModel
from app.models.field_observation import FieldObservation
from app.models.growing_season import GrowingSeason
from app.services.irrigation_decision import build_irrigation_decision

from ml.features.engineering import build_features
from ml.inference.irrigation import predict_irrigation


router = APIRouter(
    prefix="/predictions",
    tags=["AI Predictions"],
)


class IrrigationPredictionRequest(BaseModel):
    soil_moisture: float = Field(ge=0, le=100)
    soil_temperature: float
    air_temperature: float
    humidity: float = Field(ge=0, le=100)
    rainfall_mm: float = Field(ge=0)
    observed_at: datetime
    moisture_change: float
    temperature_change: float
    rainfall_24h: float = Field(ge=0)
    rainfall_72h: float = Field(ge=0)
    moisture_24h_mean: float = Field(ge=0, le=100)
    temperature_24h_mean: float
    moisture_deficit: float = Field(ge=0)
    heat_stress: float = Field(ge=0)
    crop: str = Field(min_length=1, max_length=100)
    soil_type: str = Field(min_length=1, max_length=100)
    crop_stage: float = Field(ge=0, le=1)


class IrrigationPredictionResponse(BaseModel):
    predicted_class: str
    confidence: float
    probabilities: dict[str, float]


class FieldIrrigationPredictionResponse(BaseModel):
    field_id: UUID
    observed_at: datetime
    crop: str
    soil_type: str | None
    crop_stage: float
    soil_moisture: float | None
    rainfall_mm: float | None
    predicted_class: str
    confidence: float
    probabilities: dict[str, float]
    recommended_irrigation_mm: float
    action: str
    urgency: str
    reasons: list[str]


@router.post(
    "/irrigation",
    response_model=IrrigationPredictionResponse,
)
def predict_irrigation_demand(
    payload: IrrigationPredictionRequest,
) -> IrrigationPredictionResponse:

    features: dict[str, Any] = {
        "soil_moisture": payload.soil_moisture,
        "soil_temperature": payload.soil_temperature,
        "air_temperature": payload.air_temperature,
        "humidity": payload.humidity,
        "rainfall_mm": payload.rainfall_mm,
        "hour": payload.observed_at.hour,
        "day_of_year": payload.observed_at.timetuple().tm_yday,
        "moisture_change": payload.moisture_change,
        "temperature_change": payload.temperature_change,
        "rainfall_24h": payload.rainfall_24h,
        "rainfall_72h": payload.rainfall_72h,
        "moisture_24h_mean": payload.moisture_24h_mean,
        "temperature_24h_mean": payload.temperature_24h_mean,
        "moisture_deficit": payload.moisture_deficit,
        "heat_stress": payload.heat_stress,
        "crop": payload.crop,
        "soil_type": payload.soil_type,
        "crop_stage": payload.crop_stage,
    }

    return predict_irrigation(features)


@router.get(
    "/fields/{field_id}/irrigation",
    response_model=FieldIrrigationPredictionResponse,
)
def predict_field_irrigation(
    field_id: UUID,
    db: Session = Depends(get_db),
) -> FieldIrrigationPredictionResponse:

    field = db.get(FieldModel, field_id)

    if field is None:
        raise HTTPException(
            status_code=404,
            detail="Field not found",
        )

    observations = db.scalars(
        select(FieldObservation)
        .where(FieldObservation.field_id == field_id)
        .order_by(FieldObservation.observed_at.asc())
    ).all()

    if not observations:
        raise HTTPException(
            status_code=404,
            detail="No observations found for this field",
        )

    rows = [
        {
            "id": str(row.id),
            "field_id": str(row.field_id),
            "observed_at": row.observed_at,
            "soil_moisture": row.soil_moisture,
            "soil_temperature": row.soil_temperature,
            "air_temperature": row.air_temperature,
            "humidity": row.humidity,
            "rainfall_mm": row.rainfall_mm,
            "source": row.source,
        }
        for row in observations
    ]

    dataframe = pd.DataFrame(rows)

    dataframe["observed_at"] = pd.to_datetime(
        dataframe["observed_at"],
        utc=True,
    )

    required_measurements = [
        "soil_moisture",
        "soil_temperature",
        "air_temperature",
        "humidity",
        "rainfall_mm",
    ]

    latest_raw = dataframe.iloc[-1]

    missing = [
        column
        for column in required_measurements
        if pd.isna(latest_raw[column])
    ]

    if missing:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Latest observation is missing required measurements",
                "missing": missing,
            },
        )

    features = build_features(dataframe)
    latest = features.iloc[-1].copy()

    moisture_change = (
        0.0
        if pd.isna(latest["moisture_change"])
        else float(latest["moisture_change"])
    )

    temperature_change = (
        0.0
        if pd.isna(latest["temperature_change"])
        else float(latest["temperature_change"])
    )

    observation_time = latest["observed_at"]
    observation_date = observation_time.date()

    # ---------------------------------------------------------
    # ACTIVE GROWING SEASON
    # ---------------------------------------------------------
    season = db.scalars(
        select(GrowingSeason)
        .where(
            GrowingSeason.field_id == field_id,
            GrowingSeason.planting_date <= observation_date,
        )
        .order_by(
            GrowingSeason.planting_date.desc()
        )
    ).first()

    if season is None:
        raise HTTPException(
            status_code=422,
            detail="No growing season active for this observation date",
        )

    if (
        season.expected_harvest_date is not None
        and observation_date > season.expected_harvest_date
    ):
        raise HTTPException(
            status_code=422,
            detail={
                "message": "No active growing season for this observation date",
                "observation_date": str(observation_date),
                "latest_season": season.season_name,
                "season_end": str(season.expected_harvest_date),
            },
        )

    crop = db.get(Crop, season.crop_id)

    if crop is None:
        raise HTTPException(
            status_code=422,
            detail="Crop referenced by growing season was not found",
        )

    # ---------------------------------------------------------
    # CROP STAGE
    # ---------------------------------------------------------
    days_since_planting = (
        observation_date - season.planting_date
    ).days

    if season.expected_harvest_date is not None:
        total_days = (
            season.expected_harvest_date
            - season.planting_date
        ).days

        crop_stage = (
            days_since_planting / total_days
            if total_days > 0
            else 0.0
        )
    else:
        crop_stage = days_since_planting / 120.0

    crop_stage = max(
        0.0,
        min(1.0, crop_stage),
    )

    soil_type = field.soil_type or "loamy"

    model_features: dict[str, Any] = {
        "soil_moisture": float(latest["soil_moisture"]),
        "soil_temperature": float(latest["soil_temperature"]),
        "air_temperature": float(latest["air_temperature"]),
        "humidity": float(latest["humidity"]),
        "rainfall_mm": float(latest["rainfall_mm"]),
        "hour": int(latest["hour"]),
        "day_of_year": int(latest["day_of_year"]),
        "moisture_change": moisture_change,
        "temperature_change": temperature_change,
        "rainfall_24h": float(latest["rainfall_24h"]),
        "rainfall_72h": float(latest["rainfall_72h"]),
        "moisture_24h_mean": float(latest["moisture_24h_mean"]),
        "temperature_24h_mean": float(latest["temperature_24h_mean"]),
        "moisture_deficit": float(latest["moisture_deficit"]),
        "heat_stress": float(latest["heat_stress"]),
        "crop": crop.name,
        "soil_type": soil_type,
        "crop_stage": float(crop_stage),
    }

    prediction = predict_irrigation(
        model_features
    )

    decision = build_irrigation_decision(
        predicted_class=prediction["predicted_class"],
        confidence=prediction["confidence"],
        recommended_irrigation_mm=prediction["recommended_irrigation_mm"],
        soil_moisture=float(latest["soil_moisture"]),
        rainfall_mm=float(latest["rainfall_mm"]),
        rainfall_24h=float(latest["rainfall_24h"]),
        rainfall_72h=float(latest["rainfall_72h"]),
        moisture_deficit=float(latest["moisture_deficit"]),
        heat_stress=float(latest["heat_stress"]),
        crop_stage=float(crop_stage),
    )

    return FieldIrrigationPredictionResponse(
        field_id=field_id,
        observed_at=latest["observed_at"],
        crop=crop.name,
        soil_type=field.soil_type,
        crop_stage=round(crop_stage, 4),
        soil_moisture=float(latest["soil_moisture"]),
        rainfall_mm=float(latest["rainfall_mm"]),
        predicted_class=prediction["predicted_class"],
        confidence=prediction["confidence"],
        probabilities=prediction["probabilities"],
        recommended_irrigation_mm=prediction["recommended_irrigation_mm"],
        action=decision["action"],
        urgency=decision["urgency"],
        reasons=decision["reasons"],
    )








