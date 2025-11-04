from werkzeug.security import generate_password_hash, check_password_hash
from jose import jwt
from datetime import datetime, UTC, timedelta
from dotenv import load_dotenv
import os
from typing import Dict, Any


load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")) 


class UserAlreadyExists(Exception):
    def __init__(self):
        self.message = ""
        super().__init__(self.message)

# so info can't be added for non-existing user (not signed-up one)
class UserDoesntExist(Exception):
    def __init__(self):
        self.message: str = "User needs to be signed-up to before creating data for him"
        super().__init__(self.message)


class AuthService:
    def get_password_hash(self, password: str) -> str:
        return generate_password_hash(password)
    

    def verify_password(self, plain_password: str, password_hash: str) -> bool:
        return check_password_hash(password_hash, plain_password)
    

    def create_access_token(self, data: Dict) -> str:
        to_encode: Dict = data.copy()
        expire: datetime = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt: str = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    
    def create_refresh_token(self, data: Dict) -> str:
        to_encode: Dict = data.copy()
        expire = datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire})
        encoded_jwt: str = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    

    def validate_refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        return jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])


auth_service: AuthService = AuthService()
