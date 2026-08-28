from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FieldCreate(BaseModel):
    farm_id: UUID
    name: str = Field(min_length=1, max_length=200)
    area_hectares: float = Field(gt=0)
    soil_type: str | None = Field(default=None, max_length=100)


class FieldRead(BaseModel):
    id: UUID
    farm_id: UUID
    name: str
    area_hectares: float
    soil_type: str | None

    model_config = ConfigDict(from_attributes=True)
