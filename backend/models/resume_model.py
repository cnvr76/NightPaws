from beanie import Document
from pydantic import Field
from datetime import datetime, UTC
from typing import Optional, List, Dict, Any
from models.vacancy_model import SeniorityLevel


class Resume(Document):
    user_id: str = Field(..., description="Reference to User")
    content: str = Field(..., description="Full resume text")
    file_url: str = Field(...)
    original_filename: str = Field(...)
    file_type: str = Field(..., description="e.x.: pdf")

    content_embedding: List[float] = Field(default_factory=list, description="Vector array for matching with vacancies")
    ai_resume_score: Optional[float] = Field(default=None, description="AI tells from 0.0 to 1.0 how successful your resume will be")
    skills: List[Dict[str, Any]] = Field(default_factory=list)
    seniority_level: Optional[SeniorityLevel] = Field(default=SeniorityLevel.UNKNOWN)
    experience_years: int = Field(ge=0, le=50, default=0)

    created_at: datetime = Field(default_factory=datetime.now(UTC))

    class Settings:
        name = "resumes"
        indexes = [
            "user_id"
        ]

    