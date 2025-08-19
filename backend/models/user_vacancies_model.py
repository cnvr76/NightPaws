from beanie import Document
from pydantic import Field
from datetime import datetime, UTC
from typing import Optional, List
from enum import Enum


class InteractionType(str, Enum):
    VIEWED = "viewed" # кликнул на вакансию или провзаимодействовал 
    SAVED = "saved" # сохранил себе на потом вакансию
    DRAFT = "draft" # Что-то выбрал, что-то написал, но все еще чего-то не хватает
    PREPARED = "prepared" # Когда есть и сопроводительное, и резюме прикрепленное
    QUEUED = "queued" # Вакансия поставлена в очередь на автоматическую подачу в фоне
    APPLIED = "applied" # Когда подался на вакансию со всеми данными
    HIDDEN = "hidden" # Когда юзер удалил(скрыл) вакансию и не хочет, чтобы она ему попадалась


class UserVacancy(Document):
    user_id: str = Field(..., description="Reference to User")
    vacancy_id: str = Field(..., description="Reference to Vacancy")
    application_id: Optional[str] = Field(..., description="Reference to Application when APPLIED")
    resume_id: Optional[str] = Field(default=None, description="Reference to Resume if APPLIED/DRAFT/PREPARED")

    ai_match_score: Optional[float] = Field(default=None, description="AI says what are the chances for this vacancy depending on best Resume match (0.0 - 1.0)")
    ai_resume_suggestions: List[str] = Field(default_factory=list, description="AI analyzes chosen resume and lists what can be improved")

    interaction_type: InteractionType = Field(default=InteractionType.VIEWED)
    cover_letter: Optional[str] = Field(default=None)
    
    applied_at: Optional[datetime] = Field(default=None)
    interacted_at: datetime = Field(default_factory=datetime.now(UTC))

    notes: Optional[str] = Field(default=None, description="Just so user can add their custom notes to interacted (SAVED/VIEWED) vacancies")

    class Settings:
        name = "user_vacancies"
        indexes = [
            "user_id",
            "vacancy_id", 
            "interaction_type",
            "ai_match_score",
            "applied_at",
            "interacted_at",
            [("user_id", 1), ("interaction_type", 1)],  # User's saved/applied vacancies
            [("user_id", 1), ("ai_match_score", -1)],   # User's best matches
            [("vacancy_id", 1), ("interaction_type", 1)] # Vacancy popularity tracking
        ]
        use_state_management = True