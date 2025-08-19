from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from models.user_vacancies_model import InteractionType
from schemas.vacancy_schema import VacancyBrief
from schemas.resume_schema import ResumeBrief


class UserVacancyCreate(BaseModel):
    vacancy_id: str
    interaction_type: InteractionType


class UserVacancyUpdate(BaseModel):
    application_id: Optional[str] = None
    resume_id: Optional[str] = None
    interaction_type: Optional[InteractionType] = None

    ai_match_score: Optional[float] = None
    cover_letter: Optional[str] = None

    applied_at: Optional[datetime] = None
    interacted_at: Optional[datetime] = None


class UserVacancyResponse(BaseModel):
    id: str
    user_id: str
    vacancy_id: str
    vacancy: Optional[VacancyBrief] = None
    resume_id: Optional[str] = None
    resume: Optional[ResumeBrief] = None

    cover_letter: Optional[str] = None
    ai_match_score: Optional[float] = None
    
    applied_at: Optional[datetime] = None
    interacted_at: datetime

    model_config = {"from_attributes": True}