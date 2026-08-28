from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.farm import Farm
from app.models.field import Field
from app.schemas.field import FieldCreate, FieldRead


router = APIRouter(
    prefix="/fields",
    tags=["Fields"],
)


@router.post(
    "",
    response_model=FieldRead,
    status_code=status.HTTP_201_CREATED,
)
def create_field(
    payload: FieldCreate,
    db: Session = Depends(get_db),
):
    farm = db.get(Farm, payload.farm_id)

    if farm is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found",
        )

    if payload.area_hectares > farm.area_hectares:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Field area cannot exceed farm area",
        )

    field = Field(
        farm_id=payload.farm_id,
        name=payload.name.strip(),
        area_hectares=payload.area_hectares,
        soil_type=payload.soil_type.strip() if payload.soil_type else None,
    )

    db.add(field)
    db.commit()
    db.refresh(field)

    return field


@router.get(
    "",
    response_model=list[FieldRead],
)
def list_fields(
    db: Session = Depends(get_db),
):
    return db.scalars(
        select(Field).order_by(Field.created_at.desc())
    ).all()
