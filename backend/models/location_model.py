from beanie import Document
from pydantic import Field
from typing import Optional


class Location(Document):
    city: str = Field(...)
    country: Optional[str] = Field(default=None, description="Not every job specify country tbh")
    
    class Settings:
        name = "locations"
        indexes = [
            "city",
            [("country", 1), ("city", 1)]
        ]