from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.farm import Farm, Field
from app.models.crop import CropCycle
from app.schemas.ai import (
    AIAdvisorRequest, AIAdvisorResponse,
    RecommendationRequest, RecommendationListResponse,
    FieldHealthRequest, FieldHealthResponse,
    CropRiskRequest, RiskAssessmentResponse,
)
from app.services.ai_context_builder import AIContextBuilder
from app.services.recommendation_engine import RecommendationEngine
from app.services.crop_health import CropHealthCalculator


router = APIRouter()
context_builder = AIContextBuilder()
recommendation_engine = RecommendationEngine()
health_calculator = CropHealthCalculator()


@router.post("/farm-advisor", response_model=AIAdvisorResponse)
async def farm_advisor(
    data: AIAdvisorRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    context = await context_builder.build_farm_context(db, data.farm_id)
    if not context:
        raise HTTPException(status_code=404, detail="Farm not found")

    if data.field_id:
        field_context = None
        for fc in context.get("fields", []):
            if fc.get("field", {}).get("id") == data.field_id:
                field_context = fc
                break
        if not field_context:
            raise HTTPException(status_code=404, detail="Field not found")
    elif context.get("fields"):
        field_context = context["fields"][0]
    else:
        field_context = {}

    query = data.query or "Berikan saran pertanian untuk lahan saya"

    # Build advice text
    field_info = field_context.get("field", {})
    cycle = field_context.get("active_crop_cycle", {})
    age = field_context.get("crop_age_days", 0)

    if cycle:
        crop_name = cycle.get("crop_name", "Tanaman")
        advice_parts = [
            f"**Analisis Lahan: {field_info.get('name', 'Unknown')}**\n",
            f"Tanaman: {crop_name}",
            f"Umur Tanaman: {age} hari setelah tanam",
            f"Status: {cycle.get('status', 'unknown')}",
        ]

        disease_history = field_context.get("disease_history", [])
        if disease_history:
            advice_parts.append(f"\n**Riwayat Penyakit:** {len(disease_history)} kejadian")
            advice_parts.append(f"Penyakit terakhir: {disease_history[0]['disease_name']}" if disease_history else "")

        weather = field_context.get("weather", {})
        current_weather = weather.get("current", {})
        if current_weather:
            advice_parts.append(f"\n**Kondisi Cuaca:**")
            advice_parts.append(f"Suhu: {current_weather.get('temperature', '-')}°C")
            advice_parts.append(f"Kelembaban: {current_weather.get('humidity', '-')}%")
            advice_parts.append(f"Curah Hujan: {current_weather.get('rainfall', '-')}mm")

        advice_parts.append(f"\n**Saran:**")
        advice_parts.append("1. Pantau perkembangan tanaman setiap hari")
        advice_parts.append("2. Jaga kebersihan lahan dari gulma")
        advice_parts.append("3. Lakukan irigasi sesuai kebutuhan tanaman")
        if age > 0:
            advice_parts.append(f"4. Perhatikan fase pertumbuhan tanaman (hari ke-{age})")
        advice = "\n".join(advice_parts)
    else:
        advice = "**Tidak ada siklus tanam aktif.** Mulai musim tanam baru untuk mendapatkan rekomendasi yang lebih spesifik."

    # Get health, recommendations, risks
    try:
        health = await health_calculator.calculate_field_health(field_context)
    except Exception:
        health = None

    recs = await recommendation_engine.generate_all(field_context)
    risks = await health_calculator.assess_risks(field_context)

    return AIAdvisorResponse(
        advice=advice,
        field_health=health,
        recommendations=recs,
        risks=risks,
    )


@router.post("/recommendations", response_model=RecommendationListResponse)
async def get_recommendations(
    data: RecommendationRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    context = await context_builder.build_farm_context(db, data.farm_id)
    if not context:
        raise HTTPException(status_code=404, detail="Farm not found")

    if data.field_id:
        field_context = None
        for fc in context.get("fields", []):
            if fc.get("field", {}).get("id") == data.field_id:
                field_context = fc
                break
        if not field_context:
            raise HTTPException(status_code=404, detail="Field not found")
    elif context.get("fields"):
        field_context = context["fields"][0]
    else:
        raise HTTPException(status_code=404, detail="No fields found in farm")

    return await recommendation_engine.generate_for_types(field_context, data.types)


@router.get("/field-health/{field_id}", response_model=FieldHealthResponse)
async def get_field_health(
    field_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Field).join(Farm).where(Field.id == field_id, Farm.user_id == user.id)
    )
    field = result.scalar_one_or_none()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")

    context = await context_builder.build_field_context(db, field_id)
    return await health_calculator.calculate_field_health(context)


@router.get("/crop-risk/{crop_cycle_id}", response_model=RiskAssessmentResponse)
async def get_crop_risk(
    crop_cycle_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cycle_result = await db.execute(
        select(CropCycle)
        .join(Field).join(Farm)
        .where(CropCycle.id == crop_cycle_id, Farm.user_id == user.id)
    )
    cycle = cycle_result.scalar_one_or_none()
    if not cycle:
        raise HTTPException(status_code=404, detail="Crop cycle not found")

    context = await context_builder.build_crop_cycle_context(db, crop_cycle_id)
    return await health_calculator.assess_risks(context)
