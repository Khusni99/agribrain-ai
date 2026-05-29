from fastapi import APIRouter, Depends, Query
from app.dependencies import get_current_user, get_optional_user
from app.models.user import User
from app.schemas.weather import WeatherResponse
from app.services.weather_service import WeatherService

router = APIRouter()
weather_service = WeatherService()


@router.get("/current", response_model=WeatherResponse)
async def get_current_weather(
    lat: float = Query(...),
    lon: float = Query(...),
    user: User | None = Depends(get_optional_user),
):
    return await weather_service.get_current_weather(lat, lon)


@router.get("/forecast")
async def get_forecast(
    lat: float = Query(...),
    lon: float = Query(...),
    days: int = Query(7, ge=1, le=14),
    user: User | None = Depends(get_optional_user),
):
    return await weather_service.get_forecast(lat, lon, days)


@router.get("/alerts")
async def get_weather_alerts(
    lat: float = Query(...),
    lon: float = Query(...),
    crop_type: str = Query(...),
    user: User | None = Depends(get_optional_user),
):
    return await weather_service.get_alerts(lat, lon, crop_type)
