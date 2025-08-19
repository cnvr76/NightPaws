from beanie import Document
from pydantic import Field, EmailStr, BaseModel
from datetime import datetime, UTC, timedelta
from enum import Enum
from typing import Optional, List


class ApplicationStatus(str, Enum):
    SENT = "sent" # Сразу как только заявка отправилась и ожидается какой-либо ответ
    WAITING = "waiting" # Если же пришел ответ, то никаких указаний не было/нужно подождать
    TEST_TASK = "test_task" # Если же дали тестовое задание
    INTERVIEW = "interview" # На интервью позвали (неважно какой раунд, указывается дополнительно)
    OFFER = "offer" # Приняли на работу
    REJECTED = "rejected" # Отказали
    GHOSTED = "ghosted" # Если же с момента последнего изменения статуса нет обновлений долгое время - значит игнор


class EmailSenderType(str, Enum):
    BOT = "bot" # Если это сообщение рассылка/автосгенерированный ответ (мол спасибо за подачу) и прочее
    USER = "user" # Сообщения и ответы(?) пользователя
    HR = "hr" # Ну и если написал работодатель, которого всегда за hr считаем


class ChainComponent(BaseModel):
    ai_status: ApplicationStatus = Field(default=ApplicationStatus.SENT)
    ai_confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)

    sender_type: EmailSenderType = Field(default=EmailSenderType.HR)
    subject: Optional[str] = Field(default=None)
    sender_email: Optional[EmailStr] = Field(default=None)
    response_text: Optional[str] = Field(default=None)

    round_number: int = Field(default=1)
    interview_date: Optional[datetime] = Field(default=None, description="If status is INTERVIEW")
    
    gmail_message_id: Optional[str] = Field(default=None, description="ID of the mail to remove duplicates")
    received_at: Optional[datetime] = Field(default=None)


class Application(Document):
    user_id: str = Field(..., description="Reference to User")
    vacancy_id: str = Field(..., description="Reference to internal Vacancy")

    current_status: ApplicationStatus = Field(default=ApplicationStatus.SENT)

    email_thread_id: Optional[str] = Field(default=None)
    email_chain: List[ChainComponent] = Field(default_factory=list)
    last_email_check: Optional[datetime] = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.now(UTC))

    class Settings:
        name = "applications"
        indexes = [
            "user_id",
            "vacancy_id", 
            "email_thread_id",
            "created_at",
            "last_email_check",
            "current_status",
            [("user_id", 1), ("current_status", 1)]
        ]
        use_state_management = True

    def add_email_to_chain(
        self,
        subject: str,
        sender_email: str,
        response_text: str,
        detected_status: ApplicationStatus = ApplicationStatus.WAITING,
        ai_confidence: float = 0.5,
        sender_type: EmailSenderType = EmailSenderType.HR,
        gmail_message_id: Optional[str] = None
    ) -> None:
        new_component = ChainComponent(
            ai_status=detected_status,
            ai_confidence=ai_confidence,
            sender_type=sender_type,
            subject=subject,
            sender_email=sender_email,
            response_text=response_text,
            round_number=len(self.email_chain) + 1,
            gmail_message_id=gmail_message_id,
            received_at=datetime.now(UTC)
        )
        
        self.email_chain.append(new_component)
        self.current_status = detected_status

    @property
    def days_since_last_response(self) -> Optional[int]:
        if not self.email_chain or len(self.email_chain) == 0:
            return None
        
        last_email: ChainComponent = self.email_chain[-1]
        
        delta: timedelta = datetime.now(UTC) - last_email.received_at
        return delta.days