from beanie import Document
from pydantic import Field, BaseModel
from datetime import datetime, UTC
from typing import List, Dict, Optional, Union
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


class SeniorityLevel(str, Enum):
    ENTRY_LEVEL = "entry-level"
    JUNIOR = "junior"
    MIDDLE = "middle"
    SENIOR = "senior"
    UNKNOWN = "unknown"


class VacancyStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    HIDDEN = "deleted"


class VacancyQuality(str, Enum):
    RAW = "raw"
    PROCESSED = "processed"
    SCAM = "scam"


class Currency(str, Enum):
    USD = "usd"
    EUR = "eur"
    UAH = "uah"
    
class Salary(BaseModel):
    min_salary: Optional[int] = Field(default=None)
    max_salary: Optional[int] = Field(default=None)
    currency: Optional[Currency] = Field(default=None)


class Vacancy(Document):
    title: str = Field(...)
    description: str = Field(...)
    position: str = Field(...)
    company_id: str = Field(..., description="Reference to Company")

    location: Dict[str, str] = Field(default={"city": "", "country": ""})
    salary: Salary = Field(default=None)

    # AI extracted
    summary: Optional[str] = Field(default=None)
    experience_years: int = Field(ge=0, le=50, default=0)
    work_formats: List[WorkFormat] = Field(default_factory=list)
    employment_types: List[EmploymentType] = Field(default_factory=list)
    skills: List[Dict[str, str]] = Field(default_factory=list)
    seniority_levels: List[SeniorityLevel] = Field(default_factory=list)
    status: VacancyStatus = Field(default=VacancyStatus.ACTIVE)
    content_embedding: List[float] = Field(default_factory=list, description="Vector array for matching")
    processing_quality: VacancyQuality = Field(default=VacancyQuality.RAW, description="Analyze on demand or in batches")
    
    job_source: Optional[str] = Field(default=None)
    original_link: Optional[str] = Field(default=None)
    
    interaction_count: int = Field(default=0)
    application_count: int = Field(default=0)
    is_popular: bool = Field(default=False, description="Will depend on interaction count")

    created_at: datetime = Field(default_factory=datetime.now(UTC))
    updated_at: datetime = Field(default_factory=datetime.now(UTC))

    class Settings:
        name = "vacancies"
        indexes = [
            "company_id",
            "status",
            "processing_quality", # Find unprocessed vacancies
            "job_source",
            "created_at",
            "is_popular",
            "interaction_count",
            "application_count",
            [("title", "text"), ("description", "text")], # Text search
            [("company_id", 1), ("interaction_count", -1)], # Popular jobs by company
            [("status", 1), ("created_at", -1)], # Recent active jobs
            [("seniority_levels", 1), ("work_formats", 1)]
        ]
        use_state_management = True
