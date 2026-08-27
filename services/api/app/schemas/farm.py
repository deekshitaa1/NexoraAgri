from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FarmCreate(BaseModel):
    organization_id: UUID
    name: str = Field(min_length=1, max_length=200)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    area_hectares: float = Field(gt=0)


class FarmRead(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    latitude: float
    longitude: float
    area_hectares: float

    model_config = ConfigDict(from_attributes=True)
