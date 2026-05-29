from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class DiseaseRecord(Base):
    __tablename__ = "disease_records"

    id = Column(Integer, primary_key=True, index=True)
    field_id = Column(Integer, ForeignKey("fields.id"), nullable=False)
    crop_id = Column(Integer, ForeignKey("crops.id"), nullable=False)
    detected_by = Column(String)
    disease_name = Column(String)
    severity_percentage = Column(Float)
    confidence_score = Column(Float)
    symptoms = Column(Text)
    causes = Column(Text)
    treatment = Column(Text)
    image_path = Column(String)
    detection_method = Column(String)
    is_confirmed = Column(Boolean, default=False)
    extra_data = Column("metadata", JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    field = relationship("Field", backref="disease_records")
    crop = relationship("Crop", backref="disease_records")
