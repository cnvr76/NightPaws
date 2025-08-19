from beanie import Document
from pydantic import Field, EmailStr
from datetime import datetime, UTC
from typing import Optional
from enum import Enum


class UserStatus(str, Enum):
    BANNED = "banned"
    REGULAR = "regular"
    ADMIN = "admin"


class User(Document):
    email: EmailStr = Field(..., unique=True)
    password_hash: str = Field(..., exclude=True)
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    avatar_url: Optional[str] = Field(default=None)

    status: UserStatus = Field(default=UserStatus.REGULAR)
    last_login: Optional[datetime] = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.now(UTC))
    updated_at: datetime = Field(default_factory=datetime.now(UTC))

    class Settings:
        name = "users"
        indexes = [
            "email",
            "created_at",
            "updated_at",
            "status"
        ]

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()