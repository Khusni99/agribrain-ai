from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.notification import WhatsAppSession, NotificationLog, ReminderPreference
from app.schemas.notification import (
    WhatsAppRegisterRequest,
    WhatsAppRegisterResponse,
    WhatsAppWebhookRequest,
    WhatsAppWebhookResponse,
    NotificationLogResponse,
    ReminderPreferenceResponse,
    ReminderPreferenceUpdate,
)
from app.services.whatsapp_provider import get_provider
from app.services.whatsapp_handler import WhatsAppCommandHandler

router = APIRouter()
handler = WhatsAppCommandHandler()


@router.post("/webhook", response_model=WhatsAppWebhookResponse)
async def whatsapp_webhook(payload: WhatsAppWebhookRequest, db: AsyncSession = Depends(get_db)):
    reply = await handler.handle_message(db, payload.From, payload.Body)
    return WhatsAppWebhookResponse(status="ok", reply=reply)


@router.get("/webhook")
async def whatsapp_webhook_verify(request: Request):
    params = dict(request.query_params)
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    verify_token = "agribrain_verify_2024"
    if mode == "subscribe" and token == verify_token:
        return int(challenge)
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/register", response_model=WhatsAppRegisterResponse)
async def register_whatsapp(
    payload: WhatsAppRegisterRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(
        select(WhatsAppSession).where(
            WhatsAppSession.user_id == current_user.id,
            WhatsAppSession.phone_number == payload.phone_number,
        )
    )
    if existing.scalar_one_or_none():
        return WhatsAppRegisterResponse(
            status="exists",
            message="Nomor sudah terdaftar",
            phone_number=payload.phone_number,
            is_verified=True,
        )

    provider = get_provider()
    is_valid = await provider.verify_number(payload.phone_number)
    if not is_valid:
        raise HTTPException(status_code=400, detail="Nomor telepon tidak valid")

    session = WhatsAppSession(
        user_id=current_user.id,
        phone_number=payload.phone_number,
        is_verified=True,
        provider="mock",
    )
    db.add(session)
    await db.commit()

    return WhatsAppRegisterResponse(
        status="registered",
        message="Nomor WhatsApp berhasil didaftarkan",
        phone_number=payload.phone_number,
        is_verified=True,
    )


@router.get("/session")
async def get_whatsapp_session(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(WhatsAppSession).where(WhatsAppSession.user_id == current_user.id)
    )
    session = result.scalar_one_or_none()
    if not session:
        return {"registered": False, "phone_number": None}
    return {
        "registered": True,
        "phone_number": session.phone_number,
        "is_verified": session.is_verified,
        "provider": session.provider,
    }
