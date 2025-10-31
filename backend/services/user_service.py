from werkzeug.security import generate_password_hash, check_password_hash
from typing import List, Optional, Dict, Any
from models.user_model import User
from schemas.user_schema import UserCreate, UserLogin, UserUpdate
from datetime import datetime, UTC


class UserService:
    pass
    

user_service: UserService = UserService()