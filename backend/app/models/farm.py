from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Farm(Base):
    __tablename__ = "farms"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    location = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    altitude = Column(Float)
    area_hectare = Column(Float)
    soil_type = Column(String)
    soil_ph = Column(Float)
    soil_ec = Column(Float)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", backref="farms")
    fields = relationship("Field", back_populates="farm", cascade="all, delete-orphan")


class Field(Base):
    __tablename__ = "fields"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)
    name = Column(String, nullable=False)
    area_hectare = Column(Float)
    crop_type = Column(String)
    planting_date = Column(DateTime)
    status = Column(String, default="active")
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    farm = relationship("Farm", back_populates="fields")
