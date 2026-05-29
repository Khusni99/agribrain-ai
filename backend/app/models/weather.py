from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


class WeatherData(Base):
    __tablename__ = "weather_data"

    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    temperature = Column(Float)
    humidity = Column(Float)
    rainfall_mm = Column(Float)
    wind_speed = Column(Float)
    solar_radiation = Column(Float)
    pressure = Column(Float)
    condition = Column(String)
    forecast = Column(JSON)
    disease_risk_score = Column(Float)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())
