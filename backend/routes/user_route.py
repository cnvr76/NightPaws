from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from schemas.user_schema import UserResponse, UserUpdate
from services.user_service import user_service
from config.database import get_db
from uuid import UUID
from models.user_model import User


router = APIRouter()


@router.get("/", response_model=List[UserResponse])
async def get_users(db: Session = Depends(get_db)):
    try:
        return user_service.get_all_users(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(user_id: UUID, db: Session = Depends(get_db)):
    try:
        return user_service.get_user(user_id, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.patch("/{user_id}/update", response_model=UserResponse)
async def update_user_info(user_id: UUID, new_data: UserUpdate, db: Session = Depends(get_db)):
    try:
        updated_user: User = user_service.update_user_data(user_id, new_data, db)
        db.commit()
        return updated_user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    

@router.delete("/{user_id}/delete", status_code=200)
async def delete_user_by_id(user_id: UUID, db: Session = Depends(get_db)):
    try:
        deleted_rows: int = user_service.delete_user(user_id, db)
        db.commit()
        return {
            "success": deleted_rows > 0,
            "deleted_rows": deleted_rows
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))