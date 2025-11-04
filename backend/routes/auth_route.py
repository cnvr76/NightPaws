from fastapi import Cookie, Depends, Response, APIRouter
from sqlalchemy.orm import Session
from config.database import get_db
from schemas.user_schema import UserLogin, UserLoginResponse, UserResponse, UserCreate
from models import User
from services.auth_service import auth_service


router = APIRouter()


@router.post("/singup", response_model=UserResponse)
async def signup(signup_data: UserCreate, db: Session = Depends(get_db)):
    new_user: User = auth_service.signup(signup_data, db)
    db.commit()
    return new_user


@router.post("/login", response_model=UserLoginResponse)
async def login(response: Response, login_data: UserLogin, db: Session = Depends(get_db)):
    refresh_token, user_response = auth_service.login(login_data, db)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="strict",
        # secure=True - on deploy via https
    )

    return user_response


@router.post("/refresh", response_model=UserLoginResponse)
async def refresh(refresh_token: str = Cookie(None), db: Session = Depends(get_db)):
    return auth_service.refresh(refresh_token, db)