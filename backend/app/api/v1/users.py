from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_profile(user: User = Depends(get_current_user)):
    return UserResponse.model_validate(user)


@router.put("/me", response_model=UserResponse)
async def update_profile(
    data: UserUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    for key, value in data.model_dump(exclude_unset=True).items():
        if hasattr(user, key) and key not in ("id", "hashed_password", "role"):
            setattr(user, key, value)
    await db.flush()
    return UserResponse.model_validate(user)
