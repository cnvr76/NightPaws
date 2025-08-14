from werkzeug.security import generate_password_hash, check_password_hash
from typing import List, Optional, Dict, Any
from models.user_model import User, UserStatus
from schemas.user_schema import UserCreate, UserLogin, UserUpdate
from datetime import datetime, UTC


class UserService:
    async def create_user(self, data: UserCreate) -> User:
        existing_user: Optional[User] = await User.find_one(User.email == data.email)
        if existing_user:
            raise ValueError("User with this email already exists")
        
        user_dict: Dict[str, Any] = data.model_dump()
        user_dict["password_hash"] = generate_password_hash(user_dict.pop("password"))

        new_user = User(**user_dict)
        await new_user.save()
        return new_user
    
    async def authenticate_user(self, login_data: UserLogin) -> Optional[User]:
        user: Optional[User] = await User.find_one(User.email == login_data.email)
        if not user:
            return None
        if not check_password_hash(user.password_hash, login_data.password):
            return None
        
        user.last_login = datetime.now(UTC)
        await user.save()
        return user
    
    async def get_all_users(self) -> List[User]:
        return await User.all().to_list()
    
    async def ban_user(self, user_id: str) -> bool:
        user: Optional[User] = await User.find_one(User.id == user_id)
        if not user:
            return False
        
        user.status = UserStatus.BANNED
        await user.save()
        return True

    async def delete_user(self, user_id: str) -> bool:
        user: Optional[User] = await User.find_one(User.id == user_id)
        if not user:
            return False

        await user.delete()
        return True
    

user_service: UserService = UserService()