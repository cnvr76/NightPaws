from beanie import Document
from pydantic import Field
from datetime import datetime, UTC
from typing import Optional, List
from models.application_model import ApplicationStatus, ChainComponent


class ExternalApplication(Document):
    user_id: str = Field(..., description="Reference to User")

    company_name: str = Field(...)
    job_title: str = Field(...)
    position: str = Field(...)

    current_status: ApplicationStatus = Field(default=ApplicationStatus.WAITING)

    email_thread_id: Optional[str] = Field(default=None)
    email_chain: List[ChainComponent] = Field(default_factory=list)
    last_email_check: Optional[datetime] = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.now(UTC))

    class Settings:
        name = "external_applications"
        indexes = [
            "user_id",
            "company_name",
            "email_thread_id",
            "created_at",
            "current_status",
            "last_email_check",
            [("user_id", 1), ("current_status", 1)]
        ]
        use_state_management = True
