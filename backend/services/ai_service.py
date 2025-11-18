from schemas.gmail_schema import GmailAnalyzedResponse, GmailResponse
from models import ApplicationStatus


class AIService:
    def __init__(self) -> None:
        pass


    def analyze(self, message: GmailResponse) -> GmailAnalyzedResponse:
        pass


    def _define_status(self, context: str) -> ApplicationStatus:
        pass