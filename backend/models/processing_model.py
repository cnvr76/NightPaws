from beanie import Document
from pydantic import Field
from typing import Optional
from enum import Enum
from datetime import datetime, UTC


"""
Данная таблица сделана для того, чтобы за свайпнутыми вакансиями (или когда просто несколько вакансий выбрано на подачу одновременно)
не пропадали из фоновых задач/очереди при ошибках с ней или при обновлении/закрытии вкладки.

Процесс авто подачи точно будет занимать приличное кол-во времени и не все будет проходить удачно, поэтому за вакансиями и их 
статусами нужно следить и, при надобности, сообщать об этом пользователю.

Будет работать в основном с Тиндер-подачей и вакансиями из UserVacancies
"""


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskType(str, Enum):
    EXTRACTING_INFO = "extracting_info"
    AI_ANALYZING = "ai_analyzing"
    GENERATING_EMBEDDING = "generating_embedding"
    MATCHING = "matching"


class EntityType(str, Enum):
    VACANCY = "vacancy"
    RESUME = "resume"


class ProcessingQueue(Document):
    entity_type: EntityType = Field(...)
    entity_id: str = Field(...)
    user_id: Optional[str] = Field(default=None, description="If None -> data is auto-processing")

    status: ProcessingStatus = Field(default=ProcessingStatus.PENDING)
    task_type: TaskType = Field(...)
    priority: int = Field(default=1, ge=1, le=5)
    attempts: int = Field(default=0, description="Retry counter")
    max_attempts: int = Field(default=3)

    error_message: Optional[str] = Field(default=None)
    started_at: Optional[datetime] = Field(default=None)
    ended_at: Optional[datetime] = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.now(UTC))

    class Settings:
        name = "processings"
        indexes = [
            "status",
            "priority", 
            "created_at",
            "entity_type",
            "user_id",
            [("status", 1), ("priority", 1), ("created_at", 1)]  # Processing order
        ]

