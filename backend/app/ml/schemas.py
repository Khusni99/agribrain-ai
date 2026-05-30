from pydantic import BaseModel
from typing import Optional


class BoundingBox(BaseModel):
    x1: int
    y1: int
    x2: int
    y2: int
    confidence: float
    label: str


class EconomicRisk(BaseModel):
    estimated_yield_loss_percent: float
    estimated_revenue_loss_per_hectare: float
    currency: str = "IDR"
    risk_level: str


class DetectionResponse(BaseModel):
    id: Optional[int] = None
    disease_name: str
    confidence: float
    severity: float
    bounding_boxes: list[BoundingBox] = []
    recommendations: list[str] = []
    prevention: list[str] = []
    economic_risk: EconomicRisk
    detection_provider: Optional[str] = None
    processed_image_width: Optional[int] = None
    processed_image_height: Optional[int] = None
