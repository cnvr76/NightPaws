from fastapi import Depends, APIRouter, Header
from sqlalchemy.orm import Session
from config.database import get_db
from routes.auth_route import get_current_user
from services.gmail_service import gmail_service
from services.parsing_service import parsing_service
from services.application_service import application_service
from models import User
from typing import List, Dict
from dotenv import load_dotenv
import os
from scripts.exceptions import InvalidCRONSecret
from googleapiclient.discovery import Resource
import asyncio
from models import Application
from schemas import GmailResponse


load_dotenv()
CRON_SECRET = os.getenv("CRON_SECRET")


router = APIRouter()


async def verify_cron(x_cron_secret: str = Header(None)) -> None:
    if x_cron_secret != CRON_SECRET:
        raise InvalidCRONSecret()


@router.post("/sync/all-users", status_code=200)
async def sync_all_applications(db: Session = Depends(get_db), _secret: None = Depends(verify_cron)):
    pass


@router.post("/sync/me", status_code=200)
async def sync_my_applications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    pass


@router.get("/test-gmail-search", status_code=200)
async def test_gmail_search(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    applications = application_service.get_active_applications(current_user.id, db)
    
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


# what I had
# from:(hyperia.sk) AND ((Hyperia) AND (python OR developer OR študent)) AND in:inbox

# what I had before & it was sort of working
# from:(hyperia.sk) AND ((Python OR developer OR študent) OR Hyperia) AND in:inbox

# what I have now returned by a func
### (from:hyperia.sk) AND (hyperia OR (python OR developer OR študent)) AND in:inbox  