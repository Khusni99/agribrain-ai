from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SAEnum
from sqlalchemy.sql import func
from app.database import Base
import enum


class UserRole(str, enum.Enum):
    FARMER = "farmer"
    AGRONOMIST = "agronomist"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    phone = Column(String)
    role = Column(SAEnum(UserRole), default=UserRole.FARMER)
    is_active = Column(Boolean, default=True)
    language = Column(String, default="id")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<User {self.username}>"
