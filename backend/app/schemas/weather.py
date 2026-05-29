from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class WeatherAlert(BaseModel):
    type: str
    severity: str
    message: str
    recommendation: str


class WeatherResponse(BaseModel):
    temperature: float
    humidity: float
    rainfall_mm: float
    wind_speed: float
    condition: str
    disease_risk: Optional[dict] = None
    spray_suitability: Optional[str] = None
    irrigation_requirement: Optional[float] = None
    alerts: List[WeatherAlert] = []
    forecast: Optional[List[dict]] = None
