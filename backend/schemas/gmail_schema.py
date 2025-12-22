from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from models import ApplicationStatus, SenderInfo


class GmailResponse(BaseModel):
    message_id: str
    thread_id: str
    subject: str
    body: Optional[str]
    sender: SenderInfo
    received_at: datetime


class GmailAnalyzedResponse(GmailResponse):
    status: ApplicationStatus