from config.celery_config import celery_app
from config.database import SessionLocal
from models import Application, User, ChainComponent
from services.application_service import application_service
from services.gmail_service import gmail_service
from uuid import UUID
from typing import Dict, List, Any
from sqlalchemy.orm import Session
import asyncio
from config.logger import Logger


logger = Logger(__name__).configure()


@celery_app.task(bind=True, name="sync_user_data_task", max_retries=3)
def sync_user_data_task(self, user_id: str) -> Dict[str, Any]:
    db: Session = SessionLocal()
    try:
        user: User = db.query(User).filter(User.id == UUID(user_id)).first()
        if not user:
            return {"status": "error", "detail": "User not found"}
        
        applications: List[Application] = application_service.get_users_active_applications(user.id, db)
        if not applications:
            return {"status": "error", "detail": "No active applications"}
        
        analysed_messages: List[List[ChainComponent] | Exception | None] = asyncio.run(gmail_service.fetch(applications, user))
        saved_applications: List[Application] = application_service.save_emails(applications, analysed_messages, db)
        db.commit()
        
        return {
            "status": "success",
            "synced_count": len(saved_applications),
            "user_id": user_id
        }
    except Exception as e:
        logger.error(f"Celery task failed for user {user_id}. Error: {e}")
        db.rollback()
        raise self.retry(exc=e, countdown=60)
    finally:
        db.close()