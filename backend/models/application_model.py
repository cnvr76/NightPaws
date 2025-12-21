from sqlalchemy.orm import relationship
from sqlalchemy import Column, Text, func, Enum as SQLEnum, ForeignKey, DateTime, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from config.database import Base
from enum import Enum
import uuid
from typing import TypedDict
from datetime import datetime


class ApplicationStatus(str, Enum):
    APPLIED = "pending"
    UPDATES = "updates"
    REJECTION = "rejection"
    INTERVIEW = "interview"
    TEST_TASK = "test_task"
    OFFER = "offer"
    GHOSTED = "ghosted"

    
class SenderInfo(TypedDict):
    name: str
    email: str


class ChainComponent(TypedDict):
    message_id: str
    thread_id: str
    sender: SenderInfo
    subject: str
    status: ApplicationStatus
    received_at: datetime


statuses_enum: SQLEnum = SQLEnum(ApplicationStatus, name="application_status_enum", values_callable=lambda items: [enum.value for enum in items])


class Application(Base):
    __tablename__ = "applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=func.gen_random_uuid())
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    company_name = Column(Text, nullable=False)
    job_title = Column(Text, nullable=False)
    current_status = Column(statuses_enum, nullable=False)
    email_chain = Column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    user = relationship("User", back_populates="applications")

    __table_args__ = (
        UniqueConstraint("user_id", "company_name", "job_title", name="uc_app_user_company_job"),
    )