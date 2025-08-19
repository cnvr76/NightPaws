from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CompanyCreate(BaseModel):
    name: str
    logo_url: Optional[str] = None

    model_config = {"from_attributes": True}


class CompanyResponse(BaseModel):
    id: str
    name: str
    logo_url: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}