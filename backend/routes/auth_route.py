from fastapi import Cookie, Depends, HTTPException, status, Response, APIRouter
from sqlalchemy.orm import Session
from config.database import get_db
from schemas.user_schema import UserLogin, UserLoginResponse, UserResponse, UserCreate
from models import User
from services.auth_service import auth_service
from jose import JWTError


router = APIRouter()


@router.post("/singup", response_model=UserResponse)
async def signup(signup_data: UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = db.query(User.id).filter(User.email == signup_data.email).first()
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        
        hashed_password: str = auth_service.get_password_hash(signup_data.password)
        user_dict = signup_data.model_dump()
        user_dict.pop("password")

        new_user = User(
            **user_dict,
            password_hash=hashed_password
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login", response_model=UserLoginResponse)
async def login(response: Response, login_data: UserLogin, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == login_data.email).first()

        if not user or not auth_service.verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        token_data = {"sub": user.email}
        access_token: str = auth_service.create_access_token(token_data)
        refresh_token: str = auth_service.create_refresh_token(token_data)

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            samesite="strict",
            # secure=True - on deploy via https
        )

        return UserLoginResponse(
            user=user,
            tokens={"access_token": access_token, "token_type": "bearer"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh", response_model=UserLoginResponse)
async def refresh(refresh_token: str = Cookie(None), db: Session = Depends(get_db)):
    try:
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token not found"
            )
        
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

        payload = auth_service.validate_refresh_token(refresh_token)
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
        
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise credentials_exception
        
        new_token_data = {"sub": user.email}
        new_access_token: str = auth_service.create_access_token(new_token_data)

        return UserLoginResponse(
            user=user,
            tokens={"access_token": new_access_token, "token_type": "bearer"}
        )

    except JWTError:
        raise credentials_exception 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))