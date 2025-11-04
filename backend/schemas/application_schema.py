from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from models import ApplicationStatus, ChainComponent
from uuid import UUID


class ApplicationCreate(BaseModel):
    job_title: str
    company_name: str
    current_status: ApplicationStatus


class ApplicationUpdate(BaseModel):
    current_status: Optional[ApplicationStatus] = None 


class ApplicationResponse(BaseModel):
    id: UUID
    user_id: UUID
    
    job_title: str
    company_name: str
    current_status: ApplicationStatus
    email_chain: List[ChainComponent]
    
    updated_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}