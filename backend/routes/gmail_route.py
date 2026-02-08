from fastapi import Depends, APIRouter, Header
from sqlalchemy.orm import Session
from config.database import get_db
from routes.auth_route import get_current_user
from services.gmail_service import gmail_service
from services.parsing_service import parsing_service
from services.application_service import application_service
from services.tasks_service import sync_user_data_task
from models import User, ChainComponent
from typing import List
from dotenv import load_dotenv
import os
from scripts.exceptions import InvalidCRONSecret, MissingWorkEmail, CustomException, TooManySyncRequests
from models import Application
from schemas import ApplicationUpdate, ApplicationResponse, GmailAnalyzedResponse
from config.logger import Logger
from config.celery_config import celery_app
from config.redis_config import redis_client, SYNC_TIMEOUT
from uuid import UUID
from celery.result import AsyncResult


load_dotenv()
CRON_SECRET = os.getenv("CRON_SECRET")
logger = Logger(__name__).configure()


router = APIRouter()


async def verify_cron(x_cron_secret: str = Header(None)) -> None:
    if x_cron_secret != CRON_SECRET:
        raise InvalidCRONSecret()


@router.get("/sync/status/{task_id}")
async def get_task_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    result = {
        "task_id": task_id,
        "status": task_result.status,
        "result": None
    }
    
    if task_result.ready():
        if task_result.successful():
            result["result"] = task_result.result
        else:
            result["status"] = "FAILURE"
            result["error"] = str(task_result.result)
            
    return result


@router.post("/sync/me", status_code=202)
async def sync_my_applications(current_user: User = Depends(get_current_user)):
    if not current_user.work_email:
        raise MissingWorkEmail()
    
    lock_key: str = f"sync_lock:{current_user.id}"
    
    if redis_client.exists(lock_key):
        ttl = redis_client.ttl(lock_key)
        minutes, seconds = divmod(ttl, 60)
        raise TooManySyncRequests(f"{minutes} minutes and {seconds} seconds")

    redis_client.setex(lock_key, SYNC_TIMEOUT * 60, "true")
    
    task = sync_user_data_task.delay(str(current_user.id))
    
    return {
        "task_id": task.id,
        "status": "queued",
        "message": "Synchronization started in background"
    }


@router.get("/test-gmail-search", status_code=200)
async def test_gmail_search(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    applications = application_service.get_users_applications(current_user.id, db)
    
    return {
        "messages": await gmail_service.fetch(applications, current_user)
    }


# FIXME - when 0 emails -> breaks with 500
@router.get("/sync/me/{appl_id}", response_model=ApplicationResponse)
async def sync_specific_application(appl_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    application: Application = application_service.get_application_by_id(current_user.id, appl_id, db)
    analysed_messages:  List[List[ChainComponent] | Exception | None] = await gmail_service.fetch([application], current_user)
    saved_application: Application = application_service.save_emails([application], analysed_messages, db)[0]

    db.commit()
    db.refresh(saved_application)

    return saved_application


@router.get("/execute-query", status_code=200)
async def execute_query(q: str, current_user: User = Depends(get_current_user)):
    service = gmail_service.get_resource_service(current_user)
    return {
        "query": q,
        "gmail": parsing_service._execute_queries(service, q)
    }