from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class SpraySchedule(Base):
    __tablename__ = "spray_schedules"

    id = Column(Integer, primary_key=True, index=True)
    field_id = Column(Integer, ForeignKey("fields.id"), nullable=False)
    crop_cycle_id = Column(Integer, ForeignKey("crop_cycles.id"))
    product_name = Column(String)
    active_ingredient = Column(String)
    target_pest = Column(String)
    dosage = Column(Float)
    dilution_rate = Column(Float)
    application_method = Column(String)
    interval_days = Column(Integer)
    next_spray_date = Column(DateTime)
    weather_suitable = Column(Boolean, default=True)
    pre_harvest_interval = Column(Integer)
    resistance_group = Column(String)
    compatibility_notes = Column(Text)
    is_applied = Column(Boolean, default=False)
    applied_date = Column(DateTime)
    extra_data = Column("metadata", JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    field = relationship("Field", backref="spray_schedules")
    crop_cycle = relationship("CropCycle", backref="spray_schedules")
