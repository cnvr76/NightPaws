from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime, UTC


class Company(Document):
    name: str = Field(...)
    logo_url: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.now(UTC))

    class Settings:
        name = "companies"
        indexes = [
            "name"
        ]