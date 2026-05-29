from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class HarvestRecord(Base):
    __tablename__ = "harvest_records"

    id = Column(Integer, primary_key=True, index=True)
    field_id = Column(Integer, ForeignKey("fields.id"), nullable=False)
    crop_cycle_id = Column(Integer, ForeignKey("crop_cycles.id"))
    harvest_date = Column(DateTime, nullable=False)
    quantity_kg = Column(Float)
    marketable_kg = Column(Float)
    reject_kg = Column(Float)
    yield_per_hectare = Column(Float)
    average_price = Column(Float)
    total_revenue = Column(Float)
    quality_grade = Column(String)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    field = relationship("Field", backref="harvest_records")
    crop_cycle = relationship("CropCycle", backref="harvest_records")
