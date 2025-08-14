from fastapi import APIRouter, HTTPException
from typing import List
from schemas.user_schema import UserCreate, UserLoginResponse, UserResponse, UserUpdate, UserLogin
from services.user_service import user_service


router = APIRouter()


@router.get("/", response_model=List[UserResponse])
async def get_users():
    return await user_service.get_all_users()