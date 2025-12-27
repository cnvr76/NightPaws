from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from schemas.user_schema import UserResponse, UserUpdate
from services.user_service import user_service
from config.database import get_db
from uuid import UUID
from models.user_model import User
from routes.auth_route import get_current_user


router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user
    

@router.patch("/me/update", response_model=UserResponse)
async def update_user_info(new_data: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    updated_user: User = user_service.update_user_data(current_user.id, new_data, db)
    db.commit()
    return updated_user


@router.delete("/me/delete", status_code=200)
async def delete_me(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    deleted_rows: int = user_service.delete_user(current_user.id, db)
    db.commit()
    return {
        "success": deleted_rows > 0,
        "deleted_rows": deleted_rows
    }


# ADMIN ROUTES - comment out later when deploying
# (or make get_admin dependency)
@router.get("/", response_model=List[UserResponse])
async def get_users(db: Session = Depends(get_db)):
    return user_service.get_all_users(db)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(user_id: UUID, db: Session = Depends(get_db)):
    return user_service.get_user(user_id, db)
    

@router.delete("/{user_id}/delete", status_code=200)
async def delete_user_by_id(user_id: UUID, db: Session = Depends(get_db)):
    deleted_rows: int = user_service.delete_user(user_id, db)
    db.commit()
    return {
        "success": deleted_rows > 0,
        "deleted_rows": deleted_rows
    }