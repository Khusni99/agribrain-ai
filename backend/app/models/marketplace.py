from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Boolean, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class ProductStatus(str, enum.Enum):
    AVAILABLE = "available"
    SOLD = "sold"
    RESERVED = "reserved"


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    category = Column(String)
    quantity_kg = Column(Float)
    price_per_kg = Column(Float)
    quality_grade = Column(String)
    location = Column(String)
    description = Column(Text)
    image_path = Column(String)
    status = Column(SAEnum(ProductStatus), default=ProductStatus.AVAILABLE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="products")


class MarketPrice(Base):
    __tablename__ = "market_prices"

    id = Column(Integer, primary_key=True, index=True)
    commodity = Column(String, nullable=False)
    location = Column(String)
    min_price = Column(Float)
    max_price = Column(Float)
    avg_price = Column(Float)
    trend = Column(String)
    source = Column(String)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
