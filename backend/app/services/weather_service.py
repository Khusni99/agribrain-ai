from typing import Optional
from app.config import settings
from app.schemas.weather import WeatherResponse, WeatherAlert


class WeatherService:
    def __init__(self):
        self.api_key = settings.WEATHER_API_KEY
        self.api_url = settings.WEATHER_API_URL

    async def _fetch_from_api(self, lat: float, lon: float, endpoint: str) -> dict:
        if self.api_key:
            import httpx
            url = f"{self.api_url}/{endpoint}"
            params = {"lat": lat, "lon": lon, "appid": self.api_key, "units": "metric"}
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                return response.json()
        return self._simulate_weather_data(lat, lon)

    def _simulate_weather_data(self, lat: float, lon: float) -> dict:
        import random
        return {
            "main": {
                "temp": round(random.uniform(22, 35), 1),
                "humidity": round(random.uniform(60, 95), 1),
                "pressure": 1010,
            },
            "rain": {"1h": round(random.uniform(0, 20), 1)},
            "wind": {"speed": round(random.uniform(2, 15), 1)},
            "weather": [{"description": "Cerah Berawan" if random.random() > 0.5 else "Hujan Ringan"}],
        }

    def _calculate_disease_risk(self, temp: float, humidity: float, rainfall: float) -> dict:
        risk_score = 0
        reasons = []

        if 20 <= temp <= 30:
            risk_score += 30
            reasons.append("Suhu optimal untuk perkembangan penyakit")

        if humidity > 80:
            risk_score += 35
            reasons.append("Kelembaban tinggi > 80%")
        elif humidity > 70:
            risk_score += 20
            reasons.append("Kelembaban cukup tinggi")

        if rainfall > 10:
            risk_score += 25
            reasons.append("Curah hujan tinggi")

        risk_level = "RENDAH"
        if risk_score > 70:
            risk_level = "TINGGI"
        elif risk_score > 40:
            risk_level = "SEDANG"

        return {
            "score": min(risk_score, 100),
            "level": risk_level,
            "reasons": reasons,
            "recommendation": "Lakukan aplikasi fungisida preventif" if risk_score > 50 else "Pantau perkembangan tanaman"
        }

    def _calculate_spray_suitability(self, wind_speed: float, rainfall: float) -> str:
        if wind_speed > 15:
            return "TIDAK DISARANKAN - Kecepatan angin terlalu tinggi"
        if rainfall > 5:
            return "TIDAK DISARANKAN - Hujan diperkirakan turun"
        if wind_speed > 10:
            return "HATI-HATI - Angin cukup kencang"
        return "DISARANKAN - Kondisi cuaca mendukung"

    async def get_current_weather(self, lat: float, lon: float) -> WeatherResponse:
        data = await self._fetch_from_api(lat, lon, "weather")
        main = data.get("main", {})
        rain = data.get("rain", {})

        temp = main.get("temp", 28)
        humidity = main.get("humidity", 75)
        rainfall = rain.get("1h", 0)
        wind_speed = data.get("wind", {}).get("speed", 5)

        disease_risk = self._calculate_disease_risk(temp, humidity, rainfall)
        spray_suitability = self._calculate_spray_suitability(wind_speed, rainfall)

        alerts = []
        if disease_risk["level"] == "TINGGI":
            alerts.append(WeatherAlert(
                type="disease_risk",
                severity="high",
                message="Risiko serangan penyakit tinggi",
                recommendation=disease_risk["recommendation"],
            ))

        return WeatherResponse(
            temperature=temp,
            humidity=humidity,
            rainfall_mm=rainfall,
            wind_speed=wind_speed,
            condition=data.get("weather", [{}])[0].get("description", "Cerah"),
            disease_risk=disease_risk,
            spray_suitability=spray_suitability,
            irrigation_requirement=max(0, 50 - rainfall),
            alerts=alerts,
        )

    async def get_forecast(self, lat: float, lon: float, days: int = 7) -> list:
        data = await self._fetch_from_api(lat, lon, "forecast")
        return data.get("list", [])[:days]

    async def get_alerts(self, lat: float, lon: float, crop_type: str) -> list:
        weather = await self.get_current_weather(lat, lon)
        return weather.alerts
