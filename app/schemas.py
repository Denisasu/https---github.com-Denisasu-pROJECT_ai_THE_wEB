from datetime import datetime
from pydantic import BaseModel,EmailStr
from typing import Optional
from fastapi import UploadFile


class Application(BaseModel):
    id: int
    photo: bytes
    email: str
    longitude: float
    latitude: float
    description: str
    status: str  # Добавлено поле
    created_at: datetime  # Добавлено поле

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

    # Метод для форматирования даты
    def dict(self, **kwargs):
        result = super().dict(**kwargs)
        if isinstance(result['created_at'], datetime):
            result['created_at'] = result['created_at'].isoformat()  
        return result    

class ApplicationCreate(BaseModel):
    photo: bytes
    email: str
    longitude: float
    latitude: float
    description: str

class UpdateStatus(BaseModel):
    status: str

class Message(BaseModel):
    id: int
    phone_number: str
    name: str
    message: str

    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    phone_number: str
    name: str
    message: str

class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None  # Добавлено поле для имени
    last_name: Optional[str] = None   # Добавлено поле для фамилии
    city: Optional[str] = None
    photo_url: Optional[str] = None 

class UserCreate(UserBase):
    password: str  # Поле для пароля

class User(UserBase):
    id: int

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    city: Optional[str] = None
    email: Optional[EmailStr] = None
    photo_url: Optional[UploadFile]


class EmailVerificationCreate(BaseModel):
    email: EmailStr
    code: str

class EmailVerificationCheck(BaseModel):
    email: EmailStr
    code: str
    new_password: str