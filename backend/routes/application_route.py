from fastapi import APIRouter, Depends
from typing import List
from services.application_service import application_service
from schemas.application_schema import ApplicationCreate, ApplicationResponse, ApplicationUpdate
from sqlalchemy.orm import Session
from config.database import get_db
from uuid import UUID
from models.application_model import Application


router = APIRouter()


@router.get("/", response_model=List[ApplicationResponse])
async def get_applications(db: Session = Depends(get_db)):
    return application_service.get_all_applications(db)
    

@router.get("/{user_id}", response_model=List[ApplicationResponse])
async def get_applications_for_user(user_id: UUID, db: Session = Depends(get_db)):
    return application_service.get_users_applications(user_id, db)
    

@router.post("/{user_id}/new", response_model=ApplicationResponse)
async def register_new_application(user_id: UUID, application_data: ApplicationCreate, db: Session = Depends(get_db)):
    new_application: Application = application_service.register_new_application(user_id, application_data, db)
    db.commit()
    return new_application
    

@router.delete("/{appl_id}/delete", status_code=200)
async def delete_application_by_id(appl_id: UUID, db: Session = Depends(get_db)):
    deleted_rows: int = application_service.delete_application(appl_id, db)
    db.commit()
    return {
        "success": deleted_rows > 0,
        "deleted_rows": deleted_rows
    }
    

@router.patch("/{appl_id}/update", response_model=ApplicationResponse)
async def update_application_info(appl_id: UUID, new_application_data: ApplicationUpdate, db: Session = Depends(get_db)):
    updated_application: Application = application_service.update_application(appl_id, new_application_data, db)
    db.commit()
    return updated_application