from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional, Dict
from uuid import UUID


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    username: str = Field(..., min_length=3, max_length=50)
    avatar_url: Optional[str] = None
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must contain at least 8 symbols")
        if not any(char.isdigit() for char in value):
            raise ValueError('Password must contain number')
        return value
    

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=1, max_length=50)
    gmail_refresh_token: Optional[str] = None


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    work_email: Optional[EmailStr]
    username: str
    avatar_url: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserLoginResponse(BaseModel):
    user: UserResponse
    message: str = "Login successful"
    tokens: Dict[str, str]
