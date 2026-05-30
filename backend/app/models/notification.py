from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class WhatsAppSession(Base):
    __tablename__ = "whatsapp_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    phone_number = Column(String, unique=True, index=True, nullable=False)
    is_verified = Column(Boolean, default=False)
    verification_code = Column(String)
    provider = Column(String, default="mock")
    provider_session_id = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", backref="whatsapp_sessions")


class NotificationLog(Base):
    __tablename__ = "notification_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    phone_number = Column(String, nullable=False)
    notification_type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    data = Column(JSON)
    status = Column(String, default="sent")
    provider_message_id = Column(String)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime(timezone=True))

    user = relationship("User", backref="notification_logs")


class ReminderPreference(Base):
    __tablename__ = "reminder_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    whatsapp_enabled = Column(Boolean, default=True)
    fertilizer_reminder = Column(Boolean, default=True)
    spray_reminder = Column(Boolean, default=True)
    harvest_reminder = Column(Boolean, default=True)
    disease_risk_alert = Column(Boolean, default=True)
    weather_alert = Column(Boolean, default=False)
    reminder_time_start = Column(String, default="06:00")
    reminder_time_end = Column(String, default="18:00")
    advance_days_fertilizer = Column(Integer, default=1)
    advance_days_spray = Column(Integer, default=1)
    advance_days_harvest = Column(Integer, default=3)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", backref="reminder_preferences")
