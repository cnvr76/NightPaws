from pydantic import BaseModel
from typing import Optional


class LocationCreate(BaseModel):
    city: str
    country: Optional[str] = None


class LocationUpdate(BaseModel):
    country: Optional[str] = None


class LocationResponse(BaseModel):
    id: str
    city: str
    country: Optional[str]

    model_config = {"from_attributes": True}