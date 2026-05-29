from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func as sa_func
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.farm import Farm, Field
from app.models.crop import Crop, CropCycle
from app.models.fertilizer import FertilizerRecommendation
from app.models.spray import SpraySchedule
from app.models.disease import DiseaseRecord
from app.models.harvest import HarvestRecord
from app.models.cost import ProductionCost
from app.schemas.farm import (
    FarmCreate, FarmUpdate, FarmResponse, FarmDetailResponse,
    FieldCreate, FieldUpdate, FieldResponse,
    CropCycleCreate, CropCycleUpdate, CropCycleResponse,
    FertilizerRecordCreate, FertilizerRecordResponse,
    SprayRecordCreate, SprayRecordResponse,
    DiseaseRecordCreate, DiseaseRecordResponse,
    HarvestRecordCreate, HarvestRecordResponse,
    ActivityResponse, UpcomingTaskResponse,
    CropProgressResponse, DashboardSummaryResponse,
)
from typing import List, Optional
from datetime import datetime, timezone


router = APIRouter()


# ─── Helper ───────────────────────────────────────────────────────

async def _get_user_farm(db: AsyncSession, farm_id: int, user_id: int) -> Farm:
    result = await db.execute(
        select(Farm).where(Farm.id == farm_id, Farm.user_id == user_id)
    )
    farm = result.scalar_one_or_none()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    return farm


async def _get_user_field(db: AsyncSession, field_id: int, user_id: int) -> Field:
    result = await db.execute(
        select(Field).join(Farm).where(Field.id == field_id, Farm.user_id == user_id)
    )
    field = result.scalar_one_or_none()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    return field


# ─── Farm CRUD ────────────────────────────────────────────────────

@router.get("/", response_model=List[FarmDetailResponse])
async def list_farms(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Farm)
        .where(Farm.user_id == user.id)
        .options(selectinload(Farm.fields))
    )
    farms = result.scalars().all()
    return [
        FarmDetailResponse(
            **farm.__dict__,
            fields_count=len(farm.fields),
        )
        for farm in farms
    ]


@router.post("/", response_model=FarmResponse, status_code=201)
async def create_farm(
    data: FarmCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    farm = Farm(**data.model_dump(), user_id=user.id)
    db.add(farm)
    await db.flush()
    await db.refresh(farm)
    return FarmResponse.model_validate(farm)


@router.get("/{farm_id}", response_model=FarmDetailResponse)
async def get_farm(
    farm_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Farm)
        .where(Farm.id == farm_id, Farm.user_id == user.id)
        .options(selectinload(Farm.fields))
    )
    farm = result.scalar_one_or_none()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    return FarmDetailResponse(
        **farm.__dict__,
        fields_count=len(farm.fields),
    )


@router.put("/{farm_id}", response_model=FarmResponse)
async def update_farm(
    farm_id: int,
    data: FarmUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    farm = await _get_user_farm(db, farm_id, user.id)
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(farm, key, value)
    await db.flush()
    await db.refresh(farm)
    return FarmResponse.model_validate(farm)


@router.delete("/{farm_id}", status_code=204)
async def delete_farm(
    farm_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    farm = await _get_user_farm(db, farm_id, user.id)
    await db.delete(farm)


# ─── Field CRUD ───────────────────────────────────────────────────

@router.get("/{farm_id}/fields", response_model=List[FieldResponse])
async def list_fields(
    farm_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_user_farm(db, farm_id, user.id)
    result = await db.execute(
        select(Field).where(Field.farm_id == farm_id)
    )
    return [FieldResponse.model_validate(f) for f in result.scalars().all()]


@router.post("/{farm_id}/fields", response_model=FieldResponse, status_code=201)
async def create_field(
    farm_id: int,
    data: FieldCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_user_farm(db, farm_id, user.id)
    field_data = data.model_dump(exclude={"farm_id"})
    field = Field(**field_data, farm_id=farm_id)
    db.add(field)
    await db.flush()
    await db.refresh(field)
    return FieldResponse.model_validate(field)


@router.get("/fields/{field_id}", response_model=FieldResponse)
async def get_field(
    field_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    field = await _get_user_field(db, field_id, user.id)
    return FieldResponse.model_validate(field)


@router.put("/fields/{field_id}", response_model=FieldResponse)
async def update_field(
    field_id: int,
    data: FieldUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    field = await _get_user_field(db, field_id, user.id)
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(field, key, value)
    await db.flush()
    await db.refresh(field)
    return FieldResponse.model_validate(field)


@router.delete("/fields/{field_id}", status_code=204)
async def delete_field(
    field_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    field = await _get_user_field(db, field_id, user.id)
    await db.delete(field)


# ─── Crop Cycle CRUD ──────────────────────────────────────────────

@router.get("/crop-cycles", response_model=List[CropCycleResponse])
async def list_crop_cycles(
    field_id: Optional[int] = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(CropCycle)
        .join(Field)
        .join(Farm)
        .where(Farm.user_id == user.id)
    )
    if field_id:
        query = query.where(CropCycle.field_id == field_id)
    result = await db.execute(query)
    return [CropCycleResponse.model_validate(c) for c in result.scalars().all()]


@router.post("/{farm_id}/crop-cycles", response_model=CropCycleResponse, status_code=201)
async def create_crop_cycle(
    farm_id: int,
    data: CropCycleCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_user_farm(db, farm_id, user.id)
    cycle = CropCycle(**data.model_dump())
    db.add(cycle)
    await db.flush()
    await db.refresh(cycle)
    return CropCycleResponse.model_validate(cycle)


@router.get("/crop-cycles/{cycle_id}", response_model=CropCycleResponse)
async def get_crop_cycle(
    cycle_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CropCycle)
        .join(Field).join(Farm)
        .where(CropCycle.id == cycle_id, Farm.user_id == user.id)
    )
    cycle = result.scalar_one_or_none()
    if not cycle:
        raise HTTPException(status_code=404, detail="Crop cycle not found")
    return CropCycleResponse.model_validate(cycle)


@router.put("/crop-cycles/{cycle_id}", response_model=CropCycleResponse)
async def update_crop_cycle(
    cycle_id: int,
    data: CropCycleUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CropCycle)
        .join(Field).join(Farm)
        .where(CropCycle.id == cycle_id, Farm.user_id == user.id)
    )
    cycle = result.scalar_one_or_none()
    if not cycle:
        raise HTTPException(status_code=404, detail="Crop cycle not found")
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(cycle, key, value)
    await db.flush()
    await db.refresh(cycle)
    return CropCycleResponse.model_validate(cycle)


@router.delete("/crop-cycles/{cycle_id}", status_code=204)
async def delete_crop_cycle(
    cycle_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CropCycle)
        .join(Field).join(Farm)
        .where(CropCycle.id == cycle_id, Farm.user_id == user.id)
    )
    cycle = result.scalar_one_or_none()
    if not cycle:
        raise HTTPException(status_code=404, detail="Crop cycle not found")
    await db.delete(cycle)


# ─── Fertilizer Records ───────────────────────────────────────────

@router.post("/fertilizer-records", response_model=FertilizerRecordResponse, status_code=201)
async def create_fertilizer_record(
    data: FertilizerRecordCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_user_field(db, data.field_id, user.id)
    record = FertilizerRecommendation(**data.model_dump())
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return FertilizerRecordResponse.model_validate(record)


@router.get("/fertilizer-records", response_model=List[FertilizerRecordResponse])
async def list_fertilizer_records(
    field_id: Optional[int] = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(FertilizerRecommendation)
        .join(Field).join(Farm)
        .where(Farm.user_id == user.id)
    )
    if field_id:
        query = query.where(FertilizerRecommendation.field_id == field_id)
    result = await db.execute(query)
    return [FertilizerRecordResponse.model_validate(r) for r in result.scalars().all()]


@router.get("/fertilizer-records/{record_id}", response_model=FertilizerRecordResponse)
async def get_fertilizer_record(
    record_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(FertilizerRecommendation)
        .join(Field).join(Farm)
        .where(FertilizerRecommendation.id == record_id, Farm.user_id == user.id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Fertilizer record not found")
    return FertilizerRecordResponse.model_validate(record)


# ─── Spray Records ────────────────────────────────────────────────

@router.post("/spray-records", response_model=SprayRecordResponse, status_code=201)
async def create_spray_record(
    data: SprayRecordCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_user_field(db, data.field_id, user.id)
    record = SpraySchedule(**data.model_dump())
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return SprayRecordResponse.model_validate(record)


@router.get("/spray-records", response_model=List[SprayRecordResponse])
async def list_spray_records(
    field_id: Optional[int] = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(SpraySchedule)
        .join(Field).join(Farm)
        .where(Farm.user_id == user.id)
    )
    if field_id:
        query = query.where(SpraySchedule.field_id == field_id)
    result = await db.execute(query)
    return [SprayRecordResponse.model_validate(r) for r in result.scalars().all()]


@router.get("/spray-records/{record_id}", response_model=SprayRecordResponse)
async def get_spray_record(
    record_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SpraySchedule)
        .join(Field).join(Farm)
        .where(SpraySchedule.id == record_id, Farm.user_id == user.id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Spray record not found")
    return SprayRecordResponse.model_validate(record)


# ─── Disease Records ──────────────────────────────────────────────

@router.post("/disease-records", response_model=DiseaseRecordResponse, status_code=201)
async def create_disease_record(
    data: DiseaseRecordCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_user_field(db, data.field_id, user.id)
    record = DiseaseRecord(**data.model_dump())
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return DiseaseRecordResponse.model_validate(record)


@router.get("/disease-records", response_model=List[DiseaseRecordResponse])
async def list_disease_records(
    field_id: Optional[int] = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(DiseaseRecord)
        .join(Field).join(Farm)
        .where(Farm.user_id == user.id)
    )
    if field_id:
        query = query.where(DiseaseRecord.field_id == field_id)
    result = await db.execute(query)
    return [DiseaseRecordResponse.model_validate(r) for r in result.scalars().all()]


@router.get("/disease-records/{record_id}", response_model=DiseaseRecordResponse)
async def get_disease_record(
    record_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(DiseaseRecord)
        .join(Field).join(Farm)
        .where(DiseaseRecord.id == record_id, Farm.user_id == user.id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Disease record not found")
    return DiseaseRecordResponse.model_validate(record)


# ─── Harvest Records ──────────────────────────────────────────────

@router.post("/harvest-records", response_model=HarvestRecordResponse, status_code=201)
async def create_harvest_record(
    data: HarvestRecordCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_user_field(db, data.field_id, user.id)
    record = HarvestRecord(**data.model_dump())
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return HarvestRecordResponse.model_validate(record)


@router.get("/harvest-records", response_model=List[HarvestRecordResponse])
async def list_harvest_records(
    field_id: Optional[int] = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(HarvestRecord)
        .join(Field).join(Farm)
        .where(Farm.user_id == user.id)
    )
    if field_id:
        query = query.where(HarvestRecord.field_id == field_id)
    result = await db.execute(query)
    return [HarvestRecordResponse.model_validate(r) for r in result.scalars().all()]


@router.get("/harvest-records/{record_id}", response_model=HarvestRecordResponse)
async def get_harvest_record(
    record_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(HarvestRecord)
        .join(Field).join(Farm)
        .where(HarvestRecord.id == record_id, Farm.user_id == user.id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Harvest record not found")
    return HarvestRecordResponse.model_validate(record)


# ─── Dashboard / Aggregate Endpoints ──────────────────────────────

@router.get("/{farm_id}/dashboard", response_model=DashboardSummaryResponse)
async def farm_dashboard(
    farm_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    farm = await _get_user_farm(db, farm_id, user.id)

    # Fields count
    fields_result = await db.execute(
        select(sa_func.count(Field.id)).where(Field.farm_id == farm_id)
    )
    total_fields = fields_result.scalar() or 0

    # Active crop cycles
    cycles_result = await db.execute(
        select(sa_func.count(CropCycle.id))
        .join(Field)
        .where(Field.farm_id == farm_id, CropCycle.status == "active")
    )
    active_cycles = cycles_result.scalar() or 0

    # Total harvest
    harvest_result = await db.execute(
        select(sa_func.coalesce(sa_func.sum(HarvestRecord.quantity_kg), 0))
        .join(Field)
        .where(Field.farm_id == farm_id)
    )
    total_harvest = float(harvest_result.scalar() or 0)

    # Recent activities (timeline)
    activities = []
    now = datetime.now(timezone.utc)

    # Recent harvests
    harvest_q = await db.execute(
        select(HarvestRecord)
        .join(Field)
        .where(Field.farm_id == farm_id)
        .options(selectinload(HarvestRecord.field))
        .order_by(HarvestRecord.created_at.desc())
        .limit(5)
    )
    for h in harvest_q.scalars().all():
        activities.append(ActivityResponse(
            id=h.id, activity_type="panen",
            description=f"Panen {h.quantity_kg or 0:.0f} kg dari {h.field.name}",
            field_name=h.field.name,
            timestamp=h.created_at or now,
        ))

    # Recent disease records
    disease_q = await db.execute(
        select(DiseaseRecord)
        .join(Field)
        .where(Field.farm_id == farm_id)
        .options(selectinload(DiseaseRecord.field))
        .order_by(DiseaseRecord.created_at.desc())
        .limit(5)
    )
    for d in disease_q.scalars().all():
        activities.append(ActivityResponse(
            id=d.id, activity_type="penyakit",
            description=f"Hama penyakit {d.disease_name} terdeteksi di {d.field.name}",
            field_name=d.field.name,
            timestamp=d.created_at or now,
        ))

    # Recent spray
    spray_q = await db.execute(
        select(SpraySchedule)
        .join(Field)
        .where(Field.farm_id == farm_id)
        .options(selectinload(SpraySchedule.field))
        .order_by(SpraySchedule.created_at.desc())
        .limit(5)
    )
    for s in spray_q.scalars().all():
        activities.append(ActivityResponse(
            id=s.id, activity_type="semprot",
            description=f"Penyemprotan {s.product_name} di {s.field.name}",
            field_name=s.field.name,
            timestamp=s.created_at or now,
        ))

    activities.sort(key=lambda a: a.timestamp, reverse=True)
    activities = activities[:10]

    # Upcoming tasks (reminders)
    upcoming = []
    cycles_q = await db.execute(
        select(CropCycle)
        .join(Field)
        .where(Field.farm_id == farm_id, CropCycle.status == "active")
        .options(selectinload(CropCycle.field), selectinload(CropCycle.crop))
    )
    for cc in cycles_q.scalars().all():
        if cc.expected_harvest_date:
            days_remaining = (cc.expected_harvest_date.date() - now.date()).days
            if 0 <= days_remaining <= 30:
                upcoming.append(UpcomingTaskResponse(
                    id=cc.id, task_type="panen",
                    title=f"Panen {cc.crop.name}",
                    description=f"Jadwal panen untuk {cc.field.name}",
                    field_name=cc.field.name,
                    due_date=cc.expected_harvest_date,
                    days_remaining=days_remaining,
                    priority="high" if days_remaining <= 7 else "medium",
                ))

    upcoming.sort(key=lambda t: t.days_remaining)
    upcoming = upcoming[:10]

    # Crop progress
    crop_progress = []
    progress_q = await db.execute(
        select(CropCycle)
        .join(Field)
        .where(Field.farm_id == farm_id, CropCycle.status == "active")
        .options(selectinload(CropCycle.field), selectinload(CropCycle.crop))
    )
    for cc in progress_q.scalars().all():
        days_elapsed = (now.date() - cc.start_date.date()).days
        total_days = (
            (cc.expected_harvest_date.date() - cc.start_date.date()).days
            if cc.expected_harvest_date else 90
        )
        total_days = max(total_days, 1)
        pct = min(100.0, max(0.0, (days_elapsed / total_days) * 100))
        crop_progress.append(CropProgressResponse(
            cycle_id=cc.id,
            crop_name=cc.crop.name if cc.crop else "Unknown",
            field_name=cc.field.name,
            start_date=cc.start_date,
            expected_harvest_date=cc.expected_harvest_date,
            days_elapsed=max(0, days_elapsed),
            total_days=total_days,
            progress_percentage=round(pct, 1),
            status=cc.status,
        ))

    return DashboardSummaryResponse(
        total_farms=1,
        total_fields=total_fields,
        active_crop_cycles=active_cycles,
        total_harvest_kg=total_harvest,
        upcoming_tasks=upcoming,
        recent_activities=activities,
        crop_progress=crop_progress,
    )


@router.get("/{farm_id}/timeline", response_model=List[ActivityResponse])
async def farm_timeline(
    farm_id: int,
    limit: int = 20,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_user_farm(db, farm_id, user.id)
    now = datetime.now(timezone.utc)
    activities = []

    harvest_q = await db.execute(
        select(HarvestRecord)
        .join(Field)
        .where(Field.farm_id == farm_id)
        .options(selectinload(HarvestRecord.field))
        .order_by(HarvestRecord.created_at.desc())
        .limit(limit)
    )
    for h in harvest_q.scalars().all():
        activities.append(ActivityResponse(
            id=h.id, activity_type="panen",
            description=f"Panen {h.quantity_kg or 0:.0f} kg di {h.field.name}",
            field_name=h.field.name,
            timestamp=h.created_at or now,
        ))

    disease_q = await db.execute(
        select(DiseaseRecord)
        .join(Field)
        .where(Field.farm_id == farm_id)
        .options(selectinload(DiseaseRecord.field))
        .order_by(DiseaseRecord.created_at.desc())
        .limit(limit)
    )
    for d in disease_q.scalars().all():
        activities.append(ActivityResponse(
            id=d.id, activity_type="penyakit",
            description=f"Penyakit {d.disease_name} di {d.field.name}",
            field_name=d.field.name,
            timestamp=d.created_at or now,
        ))

    spray_q = await db.execute(
        select(SpraySchedule)
        .join(Field)
        .where(Field.farm_id == farm_id)
        .options(selectinload(SpraySchedule.field))
        .order_by(SpraySchedule.created_at.desc())
        .limit(limit)
    )
    for s in spray_q.scalars().all():
        activities.append(ActivityResponse(
            id=s.id, activity_type="semprot",
            description=f"Semprot {s.product_name} di {s.field.name}",
            field_name=s.field.name,
            timestamp=s.created_at or now,
        ))

    fert_q = await db.execute(
        select(FertilizerRecommendation)
        .join(Field)
        .where(Field.farm_id == farm_id)
        .options(selectinload(FertilizerRecommendation.field))
        .order_by(FertilizerRecommendation.created_at.desc())
        .limit(limit)
    )
    for f in fert_q.scalars().all():
        activities.append(ActivityResponse(
            id=f.id, activity_type="pupuk",
            description=f"Pemupukan {f.fertilizer_name} di {f.field.name}",
            field_name=f.field.name,
            timestamp=f.created_at or now,
        ))

    activities.sort(key=lambda a: a.timestamp, reverse=True)
    return activities[:limit]


@router.get("/{farm_id}/reminders", response_model=List[UpcomingTaskResponse])
async def farm_reminders(
    farm_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_user_farm(db, farm_id, user.id)
    now_dt = datetime.now(timezone.utc)
    upcoming = []

    cycles_q = await db.execute(
        select(CropCycle)
        .join(Field)
        .where(Field.farm_id == farm_id, CropCycle.status == "active")
        .options(selectinload(CropCycle.field), selectinload(CropCycle.crop))
    )
    for cc in cycles_q.scalars().all():
        if cc.expected_harvest_date:
            days = (cc.expected_harvest_date.date() - now_dt.date()).days
            if 0 <= days <= 30:
                upcoming.append(UpcomingTaskResponse(
                    id=cc.id, task_type="panen",
                    title=f"Panen {cc.crop.name}",
                    description=f"Jadwal panen {cc.field.name}",
                    field_name=cc.field.name,
                    due_date=cc.expected_harvest_date,
                    days_remaining=days,
                    priority="high" if days <= 7 else "medium",
                ))

    spray_q = await db.execute(
        select(SpraySchedule)
        .join(Field)
        .where(Field.farm_id == farm_id, SpraySchedule.is_applied == False)
        .options(selectinload(SpraySchedule.field))
    )
    for s in spray_q.scalars().all():
        if s.next_spray_date:
            days = (s.next_spray_date.date() - now_dt.date()).days
            if -1 <= days <= 30:
                upcoming.append(UpcomingTaskResponse(
                    id=s.id, task_type="semprot",
                    title=f"Semprot {s.product_name}",
                    description=f"Penyemprotan {s.target_pest or ''} di {s.field.name}",
                    field_name=s.field.name,
                    due_date=s.next_spray_date,
                    days_remaining=max(0, days),
                    priority="high" if days <= 3 else "medium",
                ))

    cycles_q2 = await db.execute(
        select(CropCycle)
        .join(Field)
        .where(Field.farm_id == farm_id, CropCycle.status == "active")
        .options(selectinload(CropCycle.field), selectinload(CropCycle.crop))
    )
    for cc in cycles_q2.scalars().all():
        days = (now_dt.date() - cc.start_date.date()).days
        for fert_days, label in [(14, "Pupuk dasar"), (30, "Pupuk susulan I"), (45, "Pupuk susulan II"), (60, "Pupuk tambahan")]:
            remaining = fert_days - days
            if 0 <= remaining <= 7:
                upcoming.append(UpcomingTaskResponse(
                    id=cc.id * 1000 + fert_days, task_type="pupuk",
                    title=f"{label} {cc.crop.name}",
                    description=cc.field.name,
                    field_name=cc.field.name,
                    due_date=cc.start_date,
                    days_remaining=remaining,
                    priority="medium",
                ))

    upcoming.sort(key=lambda t: t.days_remaining)
    return upcoming[:20]


@router.get("/crop-cycles/{cycle_id}/progress", response_model=CropProgressResponse)
async def crop_cycle_progress(
    cycle_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CropCycle)
        .join(Field).join(Farm)
        .where(CropCycle.id == cycle_id, Farm.user_id == user.id)
        .options(selectinload(CropCycle.field), selectinload(CropCycle.crop))
    )
    cc = result.scalar_one_or_none()
    if not cc:
        raise HTTPException(status_code=404, detail="Crop cycle not found")

    now_dt = datetime.now(timezone.utc)
    days_elapsed = (now_dt.date() - cc.start_date.date()).days
    total_days = (
        (cc.expected_harvest_date.date() - cc.start_date.date()).days
        if cc.expected_harvest_date else 90
    )
    total_days = max(total_days, 1)
    pct = min(100.0, max(0.0, (days_elapsed / total_days) * 100))

    return CropProgressResponse(
        cycle_id=cc.id,
        crop_name=cc.crop.name if cc.crop else "Unknown",
        field_name=cc.field.name,
        start_date=cc.start_date,
        expected_harvest_date=cc.expected_harvest_date,
        days_elapsed=max(0, days_elapsed),
        total_days=total_days,
        progress_percentage=round(pct, 1),
        status=cc.status,
    )
