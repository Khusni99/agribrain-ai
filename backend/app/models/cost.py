from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class ProductionCost(Base):
    __tablename__ = "production_costs"

    id = Column(Integer, primary_key=True, index=True)
    field_id = Column(Integer, ForeignKey("fields.id"), nullable=False)
    crop_cycle_id = Column(Integer, ForeignKey("crop_cycles.id"))
    cost_category = Column(String, nullable=False)
    item_name = Column(String, nullable=False)
    quantity = Column(Float)
    unit = Column(String)
    unit_price = Column(Float)
    total_cost = Column(Float)
    notes = Column(Text)
    extra_data = Column("metadata", JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    field = relationship("Field", backref="production_costs")
    crop_cycle = relationship("CropCycle", backref="production_costs")
