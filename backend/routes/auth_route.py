from fastapi import Cookie, Depends, Response, APIRouter
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from config.database import get_db
from schemas.user_schema import UserLogin, UserLoginResponse, UserResponse, UserCreate, UserUpdate
from models import User
from services.auth_service import auth_service
from services.gmail_service import gmail_service
from services.user_service import user_service
from uuid import UUID
from scripts.exceptions import UserDoesntExist
from config.gmail import bearer_scheme
import os
from dotenv import load_dotenv


load_dotenv()
router = APIRouter()
FRONTEND_URL = os.getenv("FRONTEND_URL")


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: Session = Depends(get_db)) -> User:
    token: str = credentials.credentials
    return auth_service.get_current_user(token, db)


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
    user, tokens = auth_service.refresh(refresh_token, db)
    return UserLoginResponse(
        user=user,
        tokens=tokens
    )


@router.get("/google/login")
async def google_login(current_user: User = Depends(get_current_user)):
    user_id_state: str = str(current_user.id)
    auth_url = gmail_service.get_google_auth_url(user_id_state)
    return {"authorization_url": auth_url}


@router.get("/google/callback")
async def google_callback(code: str, state: str, db: Session = Depends(get_db)):
    user_id_from_state: UUID = UUID(state)
    user_to_update: User = user_service.get_user(user_id_from_state, db)
    if not user_to_update:
        raise UserDoesntExist()
    
    gmail_service.process_google_callback(code, user_to_update, db)
    db.commit()

    return RedirectResponse(url=f"{FRONTEND_URL}/settings?gmail=success")