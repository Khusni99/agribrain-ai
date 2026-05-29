from typing import Optional


class YieldPredictor:
    def __init__(self):
        self.base_yields = {
            "chili": {"min": 8000, "max": 15000, "unit": "kg/ha"},
            "tomato": {"min": 15000, "max": 30000, "unit": "kg/ha"},
            "rice": {"min": 4000, "max": 7000, "unit": "kg/ha"},
            "cabbage": {"min": 20000, "max": 40000, "unit": "kg/ha"},
            "onion": {"min": 10000, "max": 20000, "unit": "kg/ha"},
            "corn": {"min": 6000, "max": 10000, "unit": "kg/ha"},
        }

    async def predict(
        self,
        crop_type: str,
        area_hectare: float,
        planting_date: str,
        historical_data: Optional[dict] = None,
        weather_data: Optional[dict] = None,
    ) -> dict:
        base = self.base_yields.get(crop_type.lower(), {"min": 5000, "max": 10000})

        adjustment = 0
        if weather_data:
            if weather_data.get("rainfall", 0) > 100:
                adjustment -= 0.1

        predicted_yield = (base["min"] + base["max"]) / 2 * (1 + adjustment)

        return {
            "crop_type": crop_type,
            "area_hectare": area_hectare,
            "predicted_yield_kg": round(predicted_yield * area_hectare, 0),
            "predicted_yield_per_hectare": round(predicted_yield, 0),
            "predicted_revenue": round(predicted_yield * area_hectare * 5000, 0),
            "confidence_range": {
                "min": round(base["min"] * area_hectare, 0),
                "max": round(base["max"] * area_hectare, 0),
            },
            "factors": [
                {"factor": "Kondisi cuaca", "impact": f"{adjustment*100:+.0f}%"},
                {"factor": "Kesuburan tanah", "impact": "Normal"},
            ],
        }
