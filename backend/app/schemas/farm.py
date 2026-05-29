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


class FarmUpdate(BaseModel):
    name: Optional[str] = None
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
    altitude: Optional[float]
    area_hectare: Optional[float]
    soil_type: Optional[str]
    soil_ph: Optional[float]
    description: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class FarmDetailResponse(FarmResponse):
    fields_count: int = 0


class FieldCreate(BaseModel):
    farm_id: int
    name: str
    area_hectare: Optional[float] = None
    crop_type: Optional[str] = None
    planting_date: Optional[datetime] = None
    notes: Optional[str] = None


class FieldUpdate(BaseModel):
    name: Optional[str] = None
    area_hectare: Optional[float] = None
    crop_type: Optional[str] = None
    planting_date: Optional[datetime] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class FieldResponse(BaseModel):
    id: int
    farm_id: int
    name: str
    area_hectare: Optional[float]
    crop_type: Optional[str]
    planting_date: Optional[datetime]
    status: str
    notes: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CropCycleCreate(BaseModel):
    field_id: int
    crop_id: int
    start_date: datetime
    expected_harvest_date: Optional[datetime] = None
    plant_count: Optional[int] = None
    spacing_meters: Optional[float] = None
    notes: Optional[str] = None


class CropCycleUpdate(BaseModel):
    start_date: Optional[datetime] = None
    expected_harvest_date: Optional[datetime] = None
    actual_harvest_date: Optional[datetime] = None
    plant_count: Optional[int] = None
    spacing_meters: Optional[float] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class CropCycleResponse(BaseModel):
    id: int
    field_id: int
    crop_id: int
    start_date: datetime
    expected_harvest_date: Optional[datetime]
    actual_harvest_date: Optional[datetime]
    plant_count: Optional[int]
    spacing_meters: Optional[float]
    status: str
    notes: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FertilizerRecordCreate(BaseModel):
    field_id: int
    crop_cycle_id: Optional[int] = None
    fertilizer_name: str
    fertilizer_type: Optional[str] = None
    dosage_per_hectare: Optional[float] = None
    dosage_per_plant: Optional[float] = None
    application_method: Optional[str] = None
    growth_stage: Optional[str] = None
    cost_estimate: Optional[float] = None
    is_organic: bool = False


class FertilizerRecordResponse(BaseModel):
    id: int
    field_id: int
    crop_cycle_id: Optional[int]
    fertilizer_name: str
    fertilizer_type: Optional[str]
    dosage_per_hectare: Optional[float]
    dosage_per_plant: Optional[float]
    application_method: Optional[str]
    growth_stage: Optional[str]
    cost_estimate: Optional[float]
    is_organic: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SprayRecordCreate(BaseModel):
    field_id: int
    crop_cycle_id: Optional[int] = None
    product_name: str
    active_ingredient: Optional[str] = None
    target_pest: Optional[str] = None
    dosage: Optional[float] = None
    dilution_rate: Optional[float] = None
    application_method: Optional[str] = None
    weather_suitable: bool = True
    is_applied: bool = False
    applied_date: Optional[datetime] = None


class SprayRecordResponse(BaseModel):
    id: int
    field_id: int
    crop_cycle_id: Optional[int]
    product_name: str
    active_ingredient: Optional[str]
    target_pest: Optional[str]
    dosage: Optional[float]
    dilution_rate: Optional[float]
    application_method: Optional[str]
    weather_suitable: bool
    is_applied: bool
    applied_date: Optional[datetime]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DiseaseRecordCreate(BaseModel):
    field_id: int
    crop_id: int
    disease_name: str
    severity_percentage: Optional[float] = None
    confidence_score: Optional[float] = None
    symptoms: Optional[str] = None
    causes: Optional[str] = None
    treatment: Optional[str] = None
    is_confirmed: bool = False


class DiseaseRecordResponse(BaseModel):
    id: int
    field_id: int
    crop_id: int
    disease_name: str
    severity_percentage: Optional[float]
    confidence_score: Optional[float]
    symptoms: Optional[str]
    causes: Optional[str]
    treatment: Optional[str]
    is_confirmed: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class HarvestRecordCreate(BaseModel):
    field_id: int
    crop_cycle_id: Optional[int] = None
    harvest_date: datetime
    quantity_kg: Optional[float] = None
    marketable_kg: Optional[float] = None
    reject_kg: Optional[float] = None
    yield_per_hectare: Optional[float] = None
    average_price: Optional[float] = None
    total_revenue: Optional[float] = None
    quality_grade: Optional[str] = None
    notes: Optional[str] = None


class HarvestRecordResponse(BaseModel):
    id: int
    field_id: int
    crop_cycle_id: Optional[int]
    harvest_date: datetime
    quantity_kg: Optional[float]
    marketable_kg: Optional[float]
    reject_kg: Optional[float]
    yield_per_hectare: Optional[float]
    average_price: Optional[float]
    total_revenue: Optional[float]
    quality_grade: Optional[str]
    notes: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ActivityResponse(BaseModel):
    id: int
    activity_type: str
    description: str
    field_name: Optional[str]
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class UpcomingTaskResponse(BaseModel):
    id: int
    task_type: str
    title: str
    description: Optional[str]
    field_name: Optional[str]
    due_date: datetime
    days_remaining: int
    priority: str

    model_config = ConfigDict(from_attributes=True)


class CropProgressResponse(BaseModel):
    cycle_id: int
    crop_name: str
    field_name: str
    start_date: datetime
    expected_harvest_date: Optional[datetime]
    days_elapsed: int
    total_days: int
    progress_percentage: float
    status: str

    model_config = ConfigDict(from_attributes=True)


class DashboardSummaryResponse(BaseModel):
    total_farms: int
    total_fields: int
    active_crop_cycles: int
    total_harvest_kg: float
    upcoming_tasks: list[UpcomingTaskResponse]
    recent_activities: list[ActivityResponse]
    crop_progress: list[CropProgressResponse]
