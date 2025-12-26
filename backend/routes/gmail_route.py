from fastapi import Depends, APIRouter, Header
from sqlalchemy.orm import Session
from config.database import get_db
from routes.auth_route import get_current_user
from services.gmail_service import gmail_service
from services.parsing_service import parsing_service
from services.application_service import application_service
from models import User
from typing import List
from dotenv import load_dotenv
import os
from scripts.exceptions import InvalidCRONSecret, MissingWorkEmail, CustomException
from googleapiclient.discovery import Resource
import asyncio
from models import Application
from schemas import GmailResponse, ApplicationUpdate, ApplicationResponse
from config.logger import Logger


load_dotenv()
CRON_SECRET = os.getenv("CRON_SECRET")
logger = Logger(__name__).configure()


router = APIRouter()


async def verify_cron(x_cron_secret: str = Header(None)) -> None:
    if x_cron_secret != CRON_SECRET:
        raise InvalidCRONSecret()


@router.post("/sync/all-users", status_code=200)
async def sync_all_applications(db: Session = Depends(get_db), _secret: None = Depends(verify_cron)):
    pass


@router.post("/sync/me", response_model=List[ApplicationResponse])
async def sync_my_applications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.work_email:
        raise MissingWorkEmail()
    
    applications: List[Application] = application_service.get_users_active_applications(current_user.id, db)

    def thread_task(application: Application) -> List[GmailResponse]:
        local_service: Resource = gmail_service.get_resource_service(current_user)
        return parsing_service.process_application(local_service, application)

    tasks = [asyncio.to_thread(thread_task, app) for app in applications]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    saved_applications: List[Application] = []
    for application, result in zip(applications, results):
        if isinstance(result, CustomException):
            logger.error(f"(Custom) Error syncing application {application.id}: {result}")
            raise result
        if isinstance(result, Exception):
            logger.error(f"Error syncing application {application.id}: {result}")
            continue
        if not result:
            saved_applications.append(application)
            continue
        
        try:
            saved_application: Application = application_service.add_email_components(application.id, result, db)
            saved_applications.append(saved_application)
        except Exception as e:
            logger.error(f"DB error saving application {application.id}: {e}")
            saved_applications.append(application)

    db.commit()
    for appl in saved_applications:
        db.refresh(appl)

    return saved_applications



@router.get("/test-gmail-search", status_code=200)
async def test_gmail_search(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    applications = application_service.get_users_active_applications(current_user.id, db)
    
    def thread_task(application: Application) -> List[GmailResponse]:
        local_service: Resource = gmail_service.get_resource_service(current_user)
        return parsing_service.process_application(local_service, application)

    tasks = [asyncio.to_thread(thread_task, app) for app in applications]
    response = await asyncio.gather(*tasks)
    return {
        "gmail": response
    }


@router.get("/execute-query", status_code=200)
async def test_gmail_search(q: str, current_user: User = Depends(get_current_user)):
    service = gmail_service.get_resource_service(current_user)
    return {
        "query": q,
        "gmail": await parsing_service._execute_queries(service, q)
    }