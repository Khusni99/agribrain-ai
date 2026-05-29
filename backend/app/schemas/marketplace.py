from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class ProductCreate(BaseModel):
    name: str
    category: Optional[str] = None
    quantity_kg: Optional[float] = None
    price_per_kg: Optional[float] = None
    quality_grade: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None


class ProductResponse(BaseModel):
    id: int
    user_id: int
    name: str
    category: Optional[str]
    quantity_kg: Optional[float]
    price_per_kg: Optional[float]
    quality_grade: Optional[str]
    location: Optional[str]
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
