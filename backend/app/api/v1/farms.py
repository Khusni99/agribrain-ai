from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.farm import Farm, Field
from app.schemas.farm import FarmCreate, FarmResponse, FieldCreate, FieldResponse
from typing import List

router = APIRouter()


@router.get("/", response_model=List[FarmResponse])
async def list_farms(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Farm).where(Farm.user_id == user.id))
    farms = result.scalars().all()
    return [FarmResponse.model_validate(f) for f in farms]


@router.post("/", response_model=FarmResponse, status_code=201)
async def create_farm(
    data: FarmCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    farm = Farm(**data.model_dump(), user_id=user.id)
    db.add(farm)
    await db.flush()
    return FarmResponse.model_validate(farm)


@router.get("/{farm_id}", response_model=FarmResponse)
async def get_farm(
    farm_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Farm).where(Farm.id == farm_id, Farm.user_id == user.id)
    )
    farm = result.scalar_one_or_none()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    return FarmResponse.model_validate(farm)


@router.post("/{farm_id}/fields", response_model=FieldResponse, status_code=201)
async def create_field(
    farm_id: int,
    data: FieldCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    farm_result = await db.execute(
        select(Farm).where(Farm.id == farm_id, Farm.user_id == user.id)
    )
    if not farm_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Farm not found")

    field = Field(**data.model_dump(), farm_id=farm_id)
    db.add(field)
    await db.flush()
    return FieldResponse.model_validate(field)
