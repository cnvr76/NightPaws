from typing import TypedDict
from pydantic import BaseModel
from datetime import datetime
from models import ApplicationStatus, SenderInfo


class GmailResponse(BaseModel):
    message_id: str
    thread_id: str
    subject: str
    body: str
    sender: SenderInfo
    received_at: datetime


class GmailAnalyzedResponse(GmailResponse):
    status: ApplicationStatus