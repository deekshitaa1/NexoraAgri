from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.farm import Farm
from app.models.organization import Organization
from app.schemas.farm import FarmCreate, FarmRead


router = APIRouter(
    prefix="/farms",
    tags=["Farms"],
)


@router.post(
    "",
    response_model=FarmRead,
    status_code=status.HTTP_201_CREATED,
)
def create_farm(
    payload: FarmCreate,
    db: Session = Depends(get_db),
):
    organization = db.get(Organization, payload.organization_id)

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    farm = Farm(
        organization_id=payload.organization_id,
        name=payload.name.strip(),
        latitude=payload.latitude,
        longitude=payload.longitude,
        area_hectares=payload.area_hectares,
    )

    db.add(farm)
    db.commit()
    db.refresh(farm)

    return farm


@router.get(
    "",
    response_model=list[FarmRead],
)
def list_farms(
    db: Session = Depends(get_db),
):
    return db.scalars(
        select(Farm).order_by(Farm.created_at.desc())
    ).all()
