from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class FarmCreate(BaseModel):
    name: str
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[float] = None
    area_hectare: Optional[float] = None
    soil_type: Optional[str] = None
    soil_ph: Optional[float] = None
    soil_ec: Optional[float] = None
    description: Optional[str] = None


class FarmResponse(BaseModel):
    id: int
    name: str
    location: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    area_hectare: Optional[float]
    soil_type: Optional[str]
    soil_ph: Optional[float]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FieldCreate(BaseModel):
    farm_id: int
    name: str
    area_hectare: Optional[float] = None
    crop_type: Optional[str] = None
    planting_date: Optional[datetime] = None
    notes: Optional[str] = None


class FieldResponse(BaseModel):
    id: int
    farm_id: int
    name: str
    area_hectare: Optional[float]
    crop_type: Optional[str]
    planting_date: Optional[datetime]
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
