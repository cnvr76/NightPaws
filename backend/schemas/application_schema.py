from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from models.application_model import ApplicationStatus, ChainComponent


class ApplicationCreate(BaseModel):
    job_title: str
    company_name: str
    current_status: ApplicationStatus


class ApplicationUpdate(BaseModel):
    current_status: Optional[ApplicationStatus] = None 


class ApplicationResponse(BaseModel):
    id: str
    user_id: str
    
    job_title: str
    company_name: str
    current_status: ApplicationStatus
    email_chain: List[ChainComponent]
    
    updated_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}