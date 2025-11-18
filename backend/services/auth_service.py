from werkzeug.security import generate_password_hash, check_password_hash
from jose import jwt
from datetime import datetime, UTC, timedelta
from dotenv import load_dotenv
import os
from typing import Dict, Any, Tuple, Optional
from schemas.user_schema import UserCreate, UserLogin, UserLoginResponse
from models.user_model import User
from sqlalchemy.orm import Session
from scripts.exceptions import UserAlreadyExists, InvalidCredentials, RefreshTokenExpired, CredentialsValidationError
from uuid import UUID
from jose import JWTError


load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")) 


class AuthService:
    def signup(self, signup_data: UserCreate, db: Session) -> User:
        db_user_id: Optional[UUID] = db.query(User.id).filter(User.email == signup_data.email).first()
        if db_user_id:
            raise UserAlreadyExists()
        
        hashed_password: str = self._get_password_hash(signup_data.password)
        user_dict = signup_data.model_dump()
        user_dict.pop("password")

        new_user = User(
            **user_dict,
            password_hash=hashed_password
        )

        db.add(new_user)
        db.flush()
        db.refresh(new_user)

        return new_user
    

    def login(self, login_data: UserLogin, db: Session) -> Tuple[str, UserLoginResponse]:
        user = db.query(User).filter(User.email == login_data.email).first()

        if not user or not self._verify_password(login_data.password, user.password_hash):
            raise InvalidCredentials()
        
        token_data = {"sub": user.email}
        access_token: str = auth_service._create_access_token(token_data)
        refresh_token: str = auth_service._create_refresh_token(token_data)

        return (
            refresh_token,
            UserLoginResponse(
                user=user,
                tokens={"access_token": access_token, "token_type": "bearer"}
            ),
        )
    

    def refresh(self, refresh_token: str, db: Session) -> Tuple[User, Dict]:
        if not refresh_token:
            raise RefreshTokenExpired()

        payload = self._validate_token(refresh_token)
        email: str = payload.get("sub")
        if email is None:
            raise CredentialsValidationError()
        
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise CredentialsValidationError()
        
        new_token_data = {"sub": user.email}
        new_access_token: str = auth_service._create_access_token(new_token_data)

        return user, {"access_token": new_access_token, "token_type": "bearer"}
    

    def get_current_user(self, token: str, db: Session) -> User:
        try:
            payload = self._validate_token(token)
            email: str = payload.get("sub")
            if email is None:
                raise CredentialsValidationError()
        except JWTError:
            raise CredentialsValidationError()
        
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise CredentialsValidationError()
        
        return user


    def _get_password_hash(self, password: str) -> str:
        return generate_password_hash(password)
    

    def _verify_password(self, plain_password: str, password_hash: str) -> bool:
        return check_password_hash(password_hash, plain_password)
    

    def _create_access_token(self, data: Dict) -> str:
        to_encode: Dict = data.copy()
        expire: datetime = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt: str = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    
    def _create_refresh_token(self, data: Dict) -> str:
        to_encode: Dict = data.copy()
        expire = datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire})
        encoded_jwt: str = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    

    def _validate_token(self, token: str) -> Dict[str, Any]:
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError:
            raise CredentialsValidationError()


auth_service: AuthService = AuthService()
