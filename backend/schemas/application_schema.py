from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from models.application_model import ApplicationStatus, ChainComponent
from schemas.vacancy_schema import VacancyBrief


class ApplicationCreate(BaseModel):
    user_id: str
    vacancy_id: str


class ApplicationUpdate(BaseModel):
    current_status: Optional[ApplicationStatus] = None 

    email_thread_id: Optional[str] = None
    email_chain: Optional[ChainComponent] = None
    last_email_check: Optional[datetime] = None


class ApplicationResponse(BaseModel):
    id: str
    user_id: str
    vacancy_id: str
    vacancy: Optional[VacancyBrief]

    current_status: ApplicationStatus
    email_thread_id: Optional[str]
    email_chain: List[ChainComponent]
    last_email_check: Optional[datetime]

    created_at: datetime

    model_config = {"from_attributes": True}