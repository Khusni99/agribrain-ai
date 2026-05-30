from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class DiagnosisRequest(BaseModel):
    query: str
    field_id: Optional[int] = None
    crop_type: Optional[str] = None
    language: str = "id"


class DiagnosisResponse(BaseModel):
    diagnosis: str
    possible_causes: List[dict]
    recommended_actions: List[str]
    fertilizer_recommendations: Optional[List[dict]] = None
    spray_recommendations: Optional[List[dict]] = None
    confidence_score: float
    follow_up_questions: List[str]


class DiseaseDetectionRequest(BaseModel):
    image_base64: str


class DiseaseDetectionResponse(BaseModel):
    disease_name: str
    severity_percentage: float
    confidence_score: float
    treatment_recommendations: List[str]
    economic_impact: Optional[dict] = None


class BoundingBoxSchema(BaseModel):
    x1: int
    y1: int
    x2: int
    y2: int
    confidence: float
    label: str


class EconomicRiskSchema(BaseModel):
    estimated_yield_loss_percent: float
    estimated_revenue_loss_per_hectare: float
    currency: str = "IDR"
    risk_level: str


class DiseaseDetectionCreateResponse(BaseModel):
    id: int
    disease_name: str
    confidence: float
    severity: float
    bounding_boxes: list[BoundingBoxSchema] = []
    recommendations: list[str] = []
    prevention: list[str] = []
    economic_risk: EconomicRiskSchema | dict = {}
    detection_provider: Optional[str] = None
    processed_image_width: Optional[int] = None
    processed_image_height: Optional[int] = None
    image_url: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class FertilizerRequest(BaseModel):
    crop_type: str
    plant_age_days: int
    growth_stage: str
    soil_ph: Optional[float] = None
    soil_ec: Optional[float] = None
    symptoms: Optional[str] = None
    weather_condition: Optional[str] = None


class FertilizerResponse(BaseModel):
    daily_recommendation: List[dict]
    weekly_recommendation: List[dict]
    fertigation_schedule: Optional[List[dict]] = None
    cost_estimation: dict


class CostCalculationRequest(BaseModel):
    field_id: int
    crop_type: str
    area_hectare: float
    items: List[dict]


class CostCalculationResponse(BaseModel):
    cost_per_plant: float
    cost_per_hectare: float
    cost_per_kg: float
    total_cost: float
    estimated_revenue: float
    profit_estimation: float
    roi_percentage: float
    breakdown: List[dict]
