from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.notification import NotificationLog, ReminderPreference
from app.schemas.notification import (
    NotificationLogResponse,
    ReminderPreferenceResponse,
    ReminderPreferenceUpdate,
)
from datetime import datetime, timezone

router = APIRouter()


@router.get("/", response_model=list[NotificationLogResponse])
async def get_notifications(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(NotificationLog)
        .where(NotificationLog.user_id == current_user.id)
        .order_by(NotificationLog.sent_at.desc())
        .limit(limit)
    )
    logs = result.scalars().all()
    return logs


@router.get("/unread")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(NotificationLog)
        .where(
            NotificationLog.user_id == current_user.id,
            NotificationLog.read_at.is_(None),
        )
    )
    unread = len(result.scalars().all())
    return {"unread_count": unread}


@router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(NotificationLog).where(
            NotificationLog.id == notification_id,
            NotificationLog.user_id == current_user.id,
        )
    )
    log = result.scalar_one_or_none()
    if not log:
        raise HTTPException(status_code=404, detail="Notification not found")
    log.read_at = datetime.now(timezone.utc)
    await db.commit()
    return {"status": "read"}


@router.get("/preferences", response_model=ReminderPreferenceResponse)
async def get_reminder_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ReminderPreference).where(ReminderPreference.user_id == current_user.id)
    )
    pref = result.scalar_one_or_none()
    if not pref:
        pref = ReminderPreference(user_id=current_user.id)
        db.add(pref)
        await db.commit()
        await db.refresh(pref)
    return pref


@router.put("/preferences", response_model=ReminderPreferenceResponse)
async def update_reminder_preferences(
    payload: ReminderPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ReminderPreference).where(ReminderPreference.user_id == current_user.id)
    )
    pref = result.scalar_one_or_none()
    if not pref:
        pref = ReminderPreference(user_id=current_user.id)
        db.add(pref)

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(pref, key, value)

    await db.commit()
    await db.refresh(pref)
    return pref
