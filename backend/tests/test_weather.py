import pytest
from app.services.weather_service import WeatherService


@pytest.mark.asyncio
async def test_weather_service():
    service = WeatherService()
    result = await service.get_current_weather(-6.2, 106.8)
    assert result.temperature > 0
    assert result.humidity > 0
    assert result.disease_risk is not None
