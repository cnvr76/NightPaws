from beanie import Document
from pydantic import Field
from datetime import datetime, UTC
from typing import Optional, List
from models.vacancy_model import WorkFormat, EmploymentType, SeniorityLevel, Currency


class UserPreferences(Document):
    user_id: str = Field(...)

    prefered_locations: List[str] = Field(default_factory=list)
    prefered_companies: List[str] = Field(default_factory=list)
    prefered_job_sources: List[str] = Field(default_factory=list)
    
    excluded_companies: List[str] = Field(default_factory=list)
    excluded_job_sources: List[str] = Field(default_factory=list)

    min_salary: Optional[int] = Field(default=None)
    max_salary: Optional[int] = Field(default=None)
    prefered_currency: Optional[Currency] = Field(default=None)

    work_formats: List[WorkFormat] = Field(default_factory=list)
    employment_types: List[EmploymentType] = Field(default_factory=list)
    seniority_levels: List[SeniorityLevel] = Field(default_factory=list)

    gmail_connected: bool = Field(default=False)
    gmail_sync_enabled: bool = Field(default=True)
    auto_apply_enabled: bool = Field(default=False, description="Won't be working for now in MVP")

    updated_at: datetime = Field(default_factory=datetime.now(UTC))

    class Settings:
        name = "user_preferences"
        indexes = [
            "user_id",
            "gmail_connected",
        ]
    
