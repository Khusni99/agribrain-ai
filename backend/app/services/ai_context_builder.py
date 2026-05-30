from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone
from app.models.farm import Farm, Field
from app.models.crop import Crop, CropCycle
from app.models.fertilizer import FertilizerRecommendation
from app.models.spray import SpraySchedule
from app.models.disease import DiseaseRecord
from app.models.harvest import HarvestRecord
from app.models.weather import WeatherData
from app.models.marketplace import MarketPrice


class AIContextBuilder:
    async def build_farm_context(self, db: AsyncSession, farm_id: int) -> dict:
        result = await db.execute(
            select(Farm).where(Farm.id == farm_id).options(selectinload(Farm.fields))
        )
        farm = result.scalar_one_or_none()
        if not farm:
            return {}

        context = {
            "farm": {
                "id": farm.id,
                "name": farm.name,
                "location": farm.location,
                "area_hectare": farm.area_hectare,
                "soil_type": farm.soil_type,
                "soil_ph": farm.soil_ph,
            },
            "fields": [],
        }

        for field in farm.fields:
            field_ctx = await self.build_field_context(db, field.id)
            context["fields"].append(field_ctx)

        return context

    async def build_field_context(self, db: AsyncSession, field_id: int) -> dict:
        result = await db.execute(select(Field).where(Field.id == field_id))
        field = result.scalar_one_or_none()
        if not field:
            return {}

        cycles_result = await db.execute(
            select(CropCycle)
            .where(CropCycle.field_id == field_id)
            .options(selectinload(CropCycle.crop))
            .order_by(CropCycle.start_date.desc())
            .limit(1)
        )
        active_cycle = cycles_result.scalar_one_or_none()

        now = datetime.now(timezone.utc)
        context = {
            "field": {
                "id": field.id,
                "name": field.name,
                "area_hectare": field.area_hectare,
                "crop_type": field.crop_type,
                "planting_date": field.planting_date.isoformat() if field.planting_date else None,
                "status": field.status,
            },
            "active_crop_cycle": None,
            "crop_age_days": 0,
            "weather": await self._get_weather_data(db, field_id),
        }

        if active_cycle:
            crop_age = max(0, (now.date() - active_cycle.start_date.date()).days)
            context["active_crop_cycle"] = {
                "id": active_cycle.id,
                "start_date": active_cycle.start_date.isoformat(),
                "expected_harvest_date": active_cycle.expected_harvest_date.isoformat() if active_cycle.expected_harvest_date else None,
                "status": active_cycle.status,
                "crop_name": active_cycle.crop.name if active_cycle.crop else "Unknown",
                "crop_growing_days": active_cycle.crop.growing_days if active_cycle.crop else 90,
            }
            context["crop_age_days"] = crop_age

        context["fertilizer_history"] = await self._get_fertilizer_history(db, field_id)
        context["spray_history"] = await self._get_spray_history(db, field_id)
        context["disease_history"] = await self._get_disease_history(db, field_id)
        context["harvest_history"] = await self._get_harvest_history(db, field_id)
        context["market_prices"] = await self._get_market_prices(db)

        return context

    async def build_crop_cycle_context(self, db: AsyncSession, cycle_id: int) -> dict:
        result = await db.execute(
            select(CropCycle)
            .where(CropCycle.id == cycle_id)
            .options(
                selectinload(CropCycle.field).selectinload(Field.farm),
                selectinload(CropCycle.crop),
            )
        )
        cycle = result.scalar_one_or_none()
        if not cycle:
            return {}

        now = datetime.now(timezone.utc)
        field = cycle.field
        farm = field.farm if field else None
        context = {
            "crop_cycle": {
                "id": cycle.id,
                "field_id": cycle.field_id,
                "crop_id": cycle.crop_id,
                "start_date": cycle.start_date.isoformat(),
                "expected_harvest_date": cycle.expected_harvest_date.isoformat() if cycle.expected_harvest_date else None,
                "status": cycle.status,
            },
            "crop": {
                "name": cycle.crop.name if cycle.crop else "Unknown",
                "growing_days": cycle.crop.growing_days if cycle.crop else 90,
            },
            "field": {
                "id": field.id if field else 0,
                "name": field.name if field else "Unknown",
                "area_hectare": field.area_hectare if field else None,
                "crop_type": field.crop_type if field else None,
                "soil_type": farm.soil_type if farm else None,
                "soil_ph": farm.soil_ph if farm else None,
            },
            "crop_age_days": max(0, (now.date() - cycle.start_date.date()).days),
            "weather": await self._get_weather_data(db, cycle.field_id),
            "fertilizer_history": await self._get_fertilizer_history(db, cycle.field_id, cycle.id),
            "spray_history": await self._get_spray_history(db, cycle.field_id, cycle.id),
            "disease_history": await self._get_disease_history(db, cycle.field_id),
            "harvest_history": await self._get_harvest_history(db, cycle.field_id),
        }
        return context

    async def _get_weather_data(self, db: AsyncSession, field_id: int) -> dict:
        result = await db.execute(
            select(Farm)
            .join(Field)
            .where(Field.id == field_id)
        )
        farm = result.scalar_one_or_none()
        if not farm or not farm.latitude or not farm.longitude:
            return {}

        weather_result = await db.execute(
            select(WeatherData)
            .where(
                WeatherData.latitude == farm.latitude,
                WeatherData.longitude == farm.longitude,
            )
            .order_by(WeatherData.recorded_at.desc())
            .limit(7)
        )
        records = weather_result.scalars().all()
        if not records:
            return {}

        return {
            "current": {
                "temperature": records[0].temperature,
                "humidity": records[0].humidity,
                "rainfall": records[0].rainfall_mm,
                "condition": records[0].condition,
            },
            "recent": [
                {
                    "temperature": r.temperature,
                    "humidity": r.humidity,
                    "rainfall": r.rainfall_mm,
                    "date": r.recorded_at.isoformat() if r.recorded_at else None,
                }
                for r in records
            ],
        }

    async def _get_fertilizer_history(
        self, db: AsyncSession, field_id: int, cycle_id: Optional[int] = None
    ) -> list:
        query = (
            select(FertilizerRecommendation)
            .where(FertilizerRecommendation.field_id == field_id)
            .order_by(FertilizerRecommendation.created_at.desc())
            .limit(10)
        )
        if cycle_id:
            query = query.where(FertilizerRecommendation.crop_cycle_id == cycle_id)
        result = await db.execute(query)
        return [
            {
                "id": r.id,
                "fertilizer_name": r.fertilizer_name,
                "dosage_per_hectare": r.dosage_per_hectare,
                "application_method": r.application_method,
                "growth_stage": r.growth_stage,
                "date": r.created_at.isoformat() if r.created_at else None,
            }
            for r in result.scalars().all()
        ]

    async def _get_spray_history(
        self, db: AsyncSession, field_id: int, cycle_id: Optional[int] = None
    ) -> list:
        query = (
            select(SpraySchedule)
            .where(SpraySchedule.field_id == field_id)
            .order_by(SpraySchedule.created_at.desc())
            .limit(10)
        )
        if cycle_id:
            query = query.where(SpraySchedule.crop_cycle_id == cycle_id)
        result = await db.execute(query)
        return [
            {
                "id": r.id,
                "product_name": r.product_name,
                "target_pest": r.target_pest,
                "dosage": r.dosage,
                "is_applied": r.is_applied,
                "date": r.created_at.isoformat() if r.created_at else None,
            }
            for r in result.scalars().all()
        ]

    async def _get_disease_history(self, db: AsyncSession, field_id: int) -> list:
        result = await db.execute(
            select(DiseaseRecord)
            .where(DiseaseRecord.field_id == field_id)
            .order_by(DiseaseRecord.created_at.desc())
            .limit(10)
        )
        return [
            {
                "id": r.id,
                "disease_name": r.disease_name,
                "severity_percentage": r.severity_percentage,
                "is_confirmed": r.is_confirmed,
                "date": r.created_at.isoformat() if r.created_at else None,
            }
            for r in result.scalars().all()
        ]

    async def _get_harvest_history(self, db: AsyncSession, field_id: int) -> list:
        result = await db.execute(
            select(HarvestRecord)
            .where(HarvestRecord.field_id == field_id)
            .order_by(HarvestRecord.harvest_date.desc())
            .limit(5)
        )
        return [
            {
                "id": r.id,
                "quantity_kg": r.quantity_kg,
                "average_price": r.average_price,
                "total_revenue": r.total_revenue,
                "date": r.harvest_date.isoformat() if r.harvest_date else None,
            }
            for r in result.scalars().all()
        ]

    async def _get_market_prices(self, db: AsyncSession) -> list:
        result = await db.execute(
            select(MarketPrice)
            .order_by(MarketPrice.recorded_at.desc())
            .limit(5)
        )
        return [
            {
                "commodity": r.commodity,
                "avg_price": r.avg_price,
                "location": r.location,
                "trend": r.trend,
            }
            for r in result.scalars().all()
        ]
