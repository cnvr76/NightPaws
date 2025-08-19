from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from models.application_model import ApplicationStatus, ChainComponent


class ExternalApplicationCreate(BaseModel):
    user_id: str
    company_name: str
    job_title: str
    position: str


class ExternalApplicationUpdate(BaseModel):
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    position: Optional[str] = None
    
    current_status: Optional[ApplicationStatus] = None

    email_thread_id: Optional[str] = None
    email_chain: Optional[List[ChainComponent]] = None
    last_email_check: Optional[datetime] = None


class ExternalApplicationResponse(BaseModel):
    id: str
    user_id: str

    company_name: str
    job_title: str
    position: str

    current_status: ApplicationStatus

    email_thread_id: Optional[str]
    email_chain: List[ChainComponent]
    last_email_check: Optional[datetime]

    created_at: datetime

    model_config = {"from_attributes": True}
