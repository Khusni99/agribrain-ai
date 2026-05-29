from typing import Optional
from app.schemas.diagnosis import FertilizerRequest, FertilizerResponse


class FertilizerService:
    def __init__(self):
        self.fertilizer_db = {
            "npk": {
                "urea": {"n": 46, "p": 0, "k": 0},
                "npk_16": {"n": 16, "p": 16, "k": 16},
                "npk_15": {"n": 15, "p": 15, "k": 15},
                "za": {"n": 21, "p": 0, "k": 0},
                "kno3": {"n": 13, "p": 0, "k": 46},
                "mkp": {"n": 0, "p": 52, "k": 34},
                "calcium_nitrate": {"n": 15.5, "p": 0, "k": 0},
                "magnesium_sulfate": {"n": 0, "p": 0, "k": 0},
            },
            "growth_stages": {
                "seedling": {"n": "high", "p": "high", "k": "low"},
                "vegetative": {"n": "high", "p": "medium", "k": "medium"},
                "flowering": {"n": "medium", "p": "high", "k": "high"},
                "fruiting": {"n": "medium", "p": "medium", "k": "high"},
                "maturity": {"n": "low", "p": "low", "k": "low"},
            },
        }

    async def recommend(self, data: FertilizerRequest) -> FertilizerResponse:
        recommendations = self._generate_recommendations(data)
        return FertilizerResponse(
            daily_recommendation=recommendations["daily"],
            weekly_recommendation=recommendations["weekly"],
            fertigation_schedule=recommendations["fertigation"],
            cost_estimation=recommendations["cost"],
        )

    def _generate_recommendations(self, data: FertilizerRequest) -> dict:
        stage = data.growth_stage.lower()
        stage_needs = self.fertilizer_db["growth_stages"].get(stage, {})

        daily_rec = [
            {
                "fertilizer": "NPK 16-16-16",
                "dosage_per_plant": "2-3 g",
                "dosage_per_hectare": "150-200 kg",
                "frequency": "Setiap 7 hari",
                "method": "Kocor atau tabur",
            },
            {
                "fertilizer": "KNO3",
                "dosage_per_plant": "1-2 g",
                "dosage_per_hectare": "50-75 kg",
                "frequency": "Setiap 10 hari",
                "method": "Kocor",
            },
        ]

        weekly_rec = [
            {
                "week": "Minggu 1-2",
                "fertilizer": "NPK 16-16-16 + Urea",
                "dosage": "NPK 100 kg/ha + Urea 50 kg/ha",
                "notes": "Fase pertumbuhan vegetatif awal",
            },
            {
                "week": "Minggu 3-4",
                "fertilizer": "NPK 16-16-16 + KNO3",
                "dosage": "NPK 150 kg/ha + KNO3 30 kg/ha",
                "notes": "Fase vegetatif aktif",
            },
            {
                "week": "Minggu 5-6",
                "fertilizer": "NPK 16-16-16 + MKP",
                "dosage": "NPK 100 kg/ha + MKP 20 kg/ha",
                "notes": "Fase pembungaan",
            },
            {
                "week": "Minggu 7-8",
                "fertilizer": "KNO3 + MKP",
                "dosage": "KNO3 40 kg/ha + MKP 15 kg/ha",
                "notes": "Fase pembentukan buah",
            },
        ]

        fertigation = [
            {
                "day": "Senin",
                "fertilizer": "NPK 16-16-16",
                "concentration": "1 g/L",
                "duration": "30 menit",
            },
            {
                "day": "Rabu",
                "fertilizer": "KNO3",
                "concentration": "0.5 g/L",
                "duration": "20 menit",
            },
            {
                "day": "Jumat",
                "fertilizer": "Calcium Nitrate",
                "concentration": "0.5 g/L",
                "duration": "20 menit",
            },
        ]

        cost = {
            "total_cost_per_hectare": 4500000,
            "breakdown": [
                {"item": "NPK 16-16-16", "qty": "400 kg", "price": 1600000},
                {"item": "Urea", "qty": "100 kg", "price": 250000},
                {"item": "KNO3", "qty": "100 kg", "price": 1200000},
                {"item": "MKP", "qty": "50 kg", "price": 750000},
                {"item": "Calcium Nitrate", "qty": "50 kg", "price": 350000},
                {"item": "Pupuk Organik", "qty": "500 kg", "price": 350000},
            ],
        }

        return {
            "daily": daily_rec,
            "weekly": weekly_rec,
            "fertigation": fertigation,
            "cost": cost,
        }
