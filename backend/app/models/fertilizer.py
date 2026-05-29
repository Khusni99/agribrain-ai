from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class FertilizerRecommendation(Base):
    __tablename__ = "fertilizer_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    field_id = Column(Integer, ForeignKey("fields.id"), nullable=False)
    crop_cycle_id = Column(Integer, ForeignKey("crop_cycles.id"))
    recommendation_type = Column(String)
    fertilizer_name = Column(String)
    fertilizer_type = Column(String)
    dosage_per_plant = Column(Float)
    dosage_per_hectare = Column(Float)
    application_method = Column(String)
    application_interval_days = Column(Integer)
    growth_stage = Column(String)
    reasoning = Column(Text)
    cost_estimate = Column(Float)
    is_organic = Column(Boolean, default=False)
    extra_data = Column("metadata", JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    field = relationship("Field", backref="fertilizer_recommendations")
    crop_cycle = relationship("CropCycle", backref="fertilizer_recommendations")
