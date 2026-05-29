from datetime import datetime, timezone
from app.schemas.ai import (
    FieldHealthResponse, RiskFactor, YieldForecast, RiskAssessmentResponse,
)


class CropHealthCalculator:
    def __init__(self):
        self.health_base_score = 100.0
        self.base_yields = {
            "cabai merah": {"min": 8000, "max": 15000},
            "cabai rawit": {"min": 6000, "max": 12000},
            "tomat": {"min": 15000, "max": 30000},
            "padi": {"min": 4000, "max": 7000},
            "kubis": {"min": 20000, "max": 40000},
            "bawang merah": {"min": 10000, "max": 20000},
            "jagung": {"min": 6000, "max": 10000},
        }

    async def calculate_field_health(
        self, context: dict
    ) -> FieldHealthResponse:
        field = context.get("field", {})
        score = self.health_base_score
        factors = []
        disease_history = context.get("disease_history", [])
        fertilizer_history = context.get("fertilizer_history", [])
        spray_history = context.get("spray_history", [])
        weather = context.get("weather", {})
        age = context.get("crop_age_days", 0)
        cycle = context.get("active_crop_cycle") or context.get("crop_cycle", {})
        growing_days = cycle.get("crop_growing_days", 90) if isinstance(cycle, dict) else 90
        crop_name = cycle.get("crop_name", field.get("crop_type", "Unknown")) if isinstance(cycle, dict) else field.get("crop_type", "Unknown")
        area = field.get("area_hectare", 1.0)

        # Disease impact
        active_diseases = [d for d in disease_history if d.get("severity_percentage", 0) > 10]
        for d in active_diseases:
            severity = d.get("severity_percentage", 0) / 100.0
            penalty = min(30, severity * 40)
            score -= penalty
            factors.append({
                "factor": f"Penyakit: {d['disease_name']}",
                "impact": f"-{penalty:.0f}",
                "severity": f"{d.get('severity_percentage', 0)}%",
            })

        # Weather impact
        current_weather = weather.get("current", {})
        humidity = current_weather.get("humidity", 0)
        rainfall = current_weather.get("rainfall", 0)
        temp = current_weather.get("temperature", 25)

        if humidity > 85:
            score -= 10
            factors.append({"factor": "Kelembaban sangat tinggi", "impact": "-10", "severity": f"{humidity}%"})
        elif humidity > 75:
            score -= 5
            factors.append({"factor": "Kelembaban tinggi", "impact": "-5", "severity": f"{humidity}%"})

        if rainfall > 20:
            score -= 8
            factors.append({"factor": "Curah hujan berlebihan", "impact": "-8", "severity": f"{rainfall}mm"})

        # Crop age impact
        if growing_days > 0:
            progress = age / growing_days
            if progress > 1.1:
                score -= 15
                factors.append({"factor": "Melebihi masa tanam", "impact": "-15", "severity": f"{age}/{growing_days} hari"})
            elif progress < 0.05 and age > 0:
                pass  # Early stage, minimal impact
        else:
            factors.append({"factor": "Data masa tanam tidak tersedia", "impact": "-5"})

        # Missing fertilizer events
        if not fertilizer_history and age > 21:
            score -= 15
            factors.append({"factor": "Tidak ada riwayat pemupukan", "impact": "-15"})

        # Missing spray events
        if not spray_history and age > 30 and humidity > 70:
            score -= 10
            factors.append({"factor": "Tidak ada penyemprotan preventif", "impact": "-10"})

        health_score = max(0, min(100, round(score, 1)))

        # Disease risk
        disease_risk = await self._calculate_disease_risk(context)
        # Nutrient risk
        nutrient_risk = await self._calculate_nutrient_risk(context)
        # Yield forecast
        yield_forecast = await self._calculate_yield_forecast(
            crop_name, area, health_score, context
        )

        status = "sehat" if health_score >= 70 else ("waspada" if health_score >= 40 else "kritis")

        return FieldHealthResponse(
            field_id=field.get("id", 0),
            field_name=field.get("name", "Unknown"),
            health_score=health_score,
            factors=factors,
            disease_risk=disease_risk,
            nutrient_risk=nutrient_risk,
            yield_forecast=yield_forecast,
            status=status,
        )

    async def assess_risks(self, context: dict) -> RiskAssessmentResponse:
        disease_risk = await self._calculate_disease_risk(context)
        nutrient_risk = await self._calculate_nutrient_risk(context)
        yield_risk = await self._calculate_yield_risk(context, disease_risk, nutrient_risk)

        overall = max(disease_risk.score, nutrient_risk.score, yield_risk.score)
        overall_level = "RENDAH" if overall < 30 else ("SEDANG" if overall < 60 else "TINGGI")

        return RiskAssessmentResponse(
            disease_risk=disease_risk,
            nutrient_deficiency_risk=nutrient_risk,
            yield_reduction_risk=yield_risk,
            overall_risk_score=round(overall, 1),
            overall_risk_level=overall_level,
        )

    async def _calculate_disease_risk(self, context: dict) -> RiskFactor:
        score = 0
        factors_list = []
        recommendations = []
        disease_history = context.get("disease_history", [])
        weather = context.get("weather", {})
        current_weather = weather.get("current", {})

        # Active diseases
        active = [d for d in disease_history if d.get("severity_percentage", 0) > 10]
        if active:
            max_severity = max(d.get("severity_percentage", 0) for d in active)
            score += min(40, max_severity * 0.8)
            factors_list.append(f"{len(active)} penyakit aktif (severitas tertinggi {max_severity:.0f}%)")
            recommendations.append("Lakukan pengendalian penyakit segera")
            recommendations.append("Konsultasi dengan agronomis untuk rekomendasi pestisida")

        # Weather factors
        humidity = current_weather.get("humidity", 60)
        rainfall = current_weather.get("rainfall", 0)
        if humidity > 80:
            score += 15
            factors_list.append("Kelembaban > 80% meningkatkan risiko penyakit jamur")
        if rainfall > 10:
            score += 10
            factors_list.append("Curah hujan tinggi meningkatkan risiko penyakit")
        if 20 <= current_weather.get("temperature", 25) <= 30:
            score += 10
            factors_list.append("Suhu optimal untuk perkembangan patogen")

        # Spray history gaps
        spray_history = context.get("spray_history", [])
        age = context.get("crop_age_days", 0)
        if not spray_history and age > 30:
            score += 15
            factors_list.append("Belum ada penyemprotan preventif")
            recommendations.append("Mulai program penyemprotan preventif")

        score = min(100, score)
        level = "RENDAH" if score < 30 else ("SEDANG" if score < 60 else "TINGGI")
        desc = "Risiko penyakit" + (" tinggi" if score >= 60 else " sedang" if score >= 30 else " rendah")

        if not recommendations:
            if score >= 30:
                recommendations.append("Pantau perkembangan tanaman secara rutin")
            else:
                recommendations.append("Kondisi penyakit terkendali")

        return RiskFactor(
            score=round(score, 1),
            level=level,
            description=desc,
            contributing_factors=factors_list,
            recommendations=recommendations,
        )

    async def _calculate_nutrient_risk(self, context: dict) -> RiskFactor:
        score = 0
        factors_list = []
        recommendations = []
        fertilizer_history = context.get("fertilizer_history", [])
        age = context.get("crop_age_days", 0)
        field = context.get("field", {})

        if not fertilizer_history and age > 21:
            score += 35
            factors_list.append("Tidak ada riwayat pemupukan tercatat")
            recommendations.append("Segera lakukan pemupukan dasar")
            recommendations.append("Lakukan uji tanah untuk kebutuhan nutrisi spesifik")

        if len(fertilizer_history) < 2 and age > 45:
            score += 25
            factors_list.append(f"Hanya {len(fertilizer_history)} kali pemupukan dalam {age} hari")
            recommendations.append("Tingkatkan frekuensi pemupukan sesuai fase pertumbuhan")

        if age > 60 and age < 80:
            score += 10
            factors_list.append("Fase pembuahan membutuhkan nutrisi tinggi (K, P)")
            recommendations.append("Aplikasi pupuk KNO3 dan MKP untuk mendukung pembuahan")

        score = min(100, score)
        level = "RENDAH" if score < 30 else ("SEDANG" if score < 60 else "TINGGI")
        desc = "Risiko defisiensi nutrisi" + (" tinggi" if score >= 60 else " sedang" if score >= 30 else " rendah")

        if not recommendations:
            recommendations.append("Program pemupukan berjalan baik")

        return RiskFactor(
            score=round(score, 1),
            level=level,
            description=desc,
            contributing_factors=factors_list,
            recommendations=recommendations,
        )

    async def _calculate_yield_risk(
        self, context: dict, disease_risk: RiskFactor, nutrient_risk: RiskFactor
    ) -> RiskFactor:
        score = disease_risk.score * 0.4 + nutrient_risk.score * 0.3
        factors_list = []
        recommendations = []
        age = context.get("crop_age_days", 0)
        cycle = context.get("active_crop_cycle") or context.get("crop_cycle", {})
        growing_days = cycle.get("crop_growing_days", 90) if isinstance(cycle, dict) else 90
        weather = context.get("weather", {})
        current_weather = weather.get("current", {})

        if growing_days > 0 and age > growing_days * 1.1:
            score += 20
            factors_list.append("Melebihi masa tanam normal")
            recommendations.append("Segera panen untuk menghindari penurunan kualitas")

        rainfall = current_weather.get("rainfall", 0)
        if rainfall > 25:
            score += 10
            factors_list.append("Curah hujan ekstrem dapat merusak tanaman")
            recommendations.append("Perbaiki drainase untuk menghindari genangan")

        if disease_risk.score > 50:
            factors_list.append("Risiko penyakit tinggi berdampak pada hasil panen")
        if nutrient_risk.score > 50:
            factors_list.append("Risiko defisiensi nutrisi berdampak pada kualitas hasil")

        score = min(100, score)
        level = "RENDAH" if score < 30 else ("SEDANG" if score < 60 else "TINGGI")
        desc = "Risiko penurunan hasil" + (" tinggi" if score >= 60 else " sedang" if score >= 30 else " rendah")

        if not recommendations:
            recommendations.append("Potensi hasil panen dalam kondisi normal")

        return RiskFactor(
            score=round(score, 1),
            level=level,
            description=desc,
            contributing_factors=factors_list,
            recommendations=recommendations,
        )

    async def _calculate_yield_forecast(
        self, crop_name: str, area_hectare: float, health_score: float, context: dict
    ) -> YieldForecast:
        base = self.base_yields.get(crop_name.lower(), {"min": 5000, "max": 10000})
        base_yield = (base["min"] + base["max"]) / 2

        # Adjust yield based on health score
        health_factor = health_score / 100.0
        adjusted_yield = base_yield * health_factor

        # Weather adjustment
        weather = context.get("weather", {})
        current = weather.get("current", {})
        rainfall = current.get("rainfall", 0)
        weather_adj = 1.0
        if rainfall > 30:
            weather_adj = 0.85
        elif rainfall > 20:
            weather_adj = 0.92

        predicted_yield_per_ha = adjusted_yield * weather_adj
        predicted_yield_kg = predicted_yield_per_ha * area_hectare

        price_per_kg = self._estimate_price(crop_name)
        revenue = predicted_yield_kg * price_per_kg

        return YieldForecast(
            predicted_yield_kg=round(predicted_yield_kg, 0),
            predicted_yield_per_hectare=round(predicted_yield_per_ha, 0),
            confidence_range={
                "min": round(base["min"] * area_hectare * health_factor, 0),
                "max": round(base["max"] * area_hectare * health_factor, 0),
            },
            predicted_revenue=round(revenue, 0),
            factors=[
                {"factor": "Kesehatan tanaman", "impact": f"{health_factor*100:.0f}%"},
                {"factor": "Kondisi cuaca", "impact": f"{(weather_adj-1)*100:+.0f}%"},
                {"factor": f"Area tanam {area_hectare} Ha", "impact": "Normal"},
            ],
        )

    def _estimate_price(self, crop_name: str) -> float:
        prices = {
            "cabai merah": 15000,
            "cabai rawit": 20000,
            "tomat": 5000,
            "padi": 4000,
            "kubis": 3000,
            "bawang merah": 18000,
            "jagung": 3500,
        }
        return prices.get(crop_name.lower(), 5000)
