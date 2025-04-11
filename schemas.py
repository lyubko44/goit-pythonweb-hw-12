from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr


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

class UserResponse(BaseModel):
    id: int
    username: EmailStr

    class Config:
        orm_mode = True