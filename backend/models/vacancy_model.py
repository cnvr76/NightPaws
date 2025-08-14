from beanie import Document, Indexed
from pydantic import Field, EmailStr
from datetime import datetime, UTC
from typing import List, Dict, Optional, Union, Any
from enum import Enum


class WorkFormat(str, Enum):
    REMOTE = "remote"
    HYBRID = "hybrid"
    OFFICE = "office"


class EmploymentType(str, Enum):
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"


class VacancyStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    DELETED = "deleted"


class Vacancy(Document):
    title: str = Field(...)
    description: str = Field(...)
    position: str = Field(...)
    company_id: str = Field(..., description="Reference to Company")
    location: Dict[str, str] = Field(default={"city": "", "country": ""})
    salary: Optional[Dict[str, Union[str, int]]] = Field(default=None)
    experience_min: int = Field(ge=0, le=50, default=0)
    work_formats: List[WorkFormat] = Field(default_factory=list)
    employment_types: List[EmploymentType] = Field(default_factory=list)
    skills: List[Dict[str, str]] = Field(default_factory=list)
    job_source: Optional[str] = Field(default=None)
    original_link: Optional[str] = Field(default=None)
    status: VacancyStatus = Field(default=VacancyStatus.ACTIVE)
    created_at: datetime = Field(default_factory=datetime.now(UTC))
    updated_at: datetime = Field(default_factory=datetime.now(UTC))

    class Settings:
        name = "vacancies"
        indexes = [
            "company_id",
            "status",
            "created_at",
            [("title", "text"), ("description", "text")]
        ]
        use_state_management = True
