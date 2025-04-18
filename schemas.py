from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr
from sqlalchemy import Enum


class ContactCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: str
    birthday: Optional[date] = None
    additional_info: Optional[str] = None


class ContactResponse(ContactCreate):
    id: int

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    username: EmailStr
    password: str


class UserRole(str, Enum):
    user = "user"
    admin = "admin"


class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    role: UserRole

    class Config:
        orm_mode = True


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
