from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class WhatsAppRegisterRequest(BaseModel):
    phone_number: str = Field(..., description="Phone number with country code, e.g. +6281234567890")


class WhatsAppRegisterResponse(BaseModel):
    status: str
    message: str
    phone_number: str
    is_verified: bool


class WhatsAppWebhookRequest(BaseModel):
    From: str = Field(..., description="Sender phone number")
    Body: str = Field(..., description="Message body")
    MessageSid: Optional[str] = None


class WhatsAppWebhookResponse(BaseModel):
    status: str
    reply: str


class NotificationLogResponse(BaseModel):
    id: int
    notification_type: str
    title: str
    message: str
    status: str
    sent_at: datetime

    model_config = {"from_attributes": True}


class ReminderPreferenceResponse(BaseModel):
    whatsapp_enabled: bool
    fertilizer_reminder: bool
    spray_reminder: bool
    harvest_reminder: bool
    disease_risk_alert: bool
    weather_alert: bool
    reminder_time_start: str
    reminder_time_end: str
    advance_days_fertilizer: int
    advance_days_spray: int
    advance_days_harvest: int

    model_config = {"from_attributes": True}


class ReminderPreferenceUpdate(BaseModel):
    whatsapp_enabled: Optional[bool] = None
    fertilizer_reminder: Optional[bool] = None
    spray_reminder: Optional[bool] = None
    harvest_reminder: Optional[bool] = None
    disease_risk_alert: Optional[bool] = None
    weather_alert: Optional[bool] = None
    reminder_time_start: Optional[str] = None
    reminder_time_end: Optional[str] = None
    advance_days_fertilizer: Optional[int] = None
    advance_days_spray: Optional[int] = None
    advance_days_harvest: Optional[int] = None
