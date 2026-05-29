from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None
    phone: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: str
    is_active: bool
    language: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    language: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
