from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class AIAdvisorRequest(BaseModel):
    farm_id: int
    field_id: Optional[int] = None
    query: str = ""


class AIAdvisorResponse(BaseModel):
    advice: str
    field_health: Optional["FieldHealthResponse"] = None
    recommendations: Optional["RecommendationListResponse"] = None
    risks: Optional["RiskAssessmentResponse"] = None


class RecommendationRequest(BaseModel):
    farm_id: int
    field_id: Optional[int] = None
    types: list[str] = ["fertilizer", "spray", "irrigation", "harvest"]


class RecommendationItem(BaseModel):
    type: str
    title: str
    description: str
    priority: str
    timing: Optional[str] = None
    dosage: Optional[str] = None
    method: Optional[str] = None
    reasoning: str


class RecommendationListResponse(BaseModel):
    today: list[RecommendationItem] = []
    this_week: list[RecommendationItem] = []
    urgent: list[RecommendationItem] = []
    all: list[RecommendationItem] = []


class FieldHealthResponse(BaseModel):
    field_id: int
    field_name: str
    health_score: float
    factors: list[dict]
    disease_risk: "RiskFactor"
    nutrient_risk: "RiskFactor"
    yield_forecast: "YieldForecast"
    status: str

    model_config = ConfigDict(from_attributes=True)


class RiskFactor(BaseModel):
    score: float
    level: str
    description: str
    contributing_factors: list[str] = []
    recommendations: list[str] = []


class YieldForecast(BaseModel):
    predicted_yield_kg: float
    predicted_yield_per_hectare: float
    confidence_range: dict
    predicted_revenue: float
    factors: list[dict]


class RiskAssessmentResponse(BaseModel):
    disease_risk: RiskFactor
    nutrient_deficiency_risk: RiskFactor
    yield_reduction_risk: RiskFactor
    overall_risk_score: float
    overall_risk_level: str


class CropRiskRequest(BaseModel):
    crop_cycle_id: int
    include_weather: bool = True


class FieldHealthRequest(BaseModel):
    field_id: int
    include_weather: bool = True
    include_forecast: bool = True
