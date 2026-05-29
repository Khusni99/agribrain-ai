from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Crop(Base):
    __tablename__ = "crops"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    variety = Column(String)
    category = Column(String)
    growing_days = Column(Integer)
    optimal_temp_min = Column(Float)
    optimal_temp_max = Column(Float)
    optimal_ph_min = Column(Float)
    optimal_ph_max = Column(Float)
    water_requirement_mm = Column(Float)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CropCycle(Base):
    __tablename__ = "crop_cycles"

    id = Column(Integer, primary_key=True, index=True)
    field_id = Column(Integer, ForeignKey("fields.id"), nullable=False)
    crop_id = Column(Integer, ForeignKey("crops.id"), nullable=False)
    start_date = Column(DateTime, nullable=False)
    expected_harvest_date = Column(DateTime)
    actual_harvest_date = Column(DateTime)
    plant_count = Column(Integer)
    spacing_meters = Column(Float)
    status = Column(String, default="active")
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    field = relationship("Field", backref="crop_cycles")
    crop = relationship("Crop", backref="crop_cycles")
