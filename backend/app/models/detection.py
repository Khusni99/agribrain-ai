from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.database import Base


class DiseaseDetection(Base):
    __tablename__ = "disease_detections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True, index=True)
    image_path = Column(String)
    cloudinary_url = Column(String, nullable=True)
    original_filename = Column(String)
    file_size_bytes = Column(Integer)
    content_type = Column(String)
    disease_name = Column(String, index=True)
    confidence = Column(Float)
    severity = Column(Float)
    bounding_boxes = Column(JSON, default=list)
    recommendations = Column(JSON, default=list)
    prevention = Column(JSON, default=list)
    economic_risk = Column(JSON, default=dict)
    detection_provider = Column(String)
    raw_response = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
