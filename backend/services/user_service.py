from typing import Dict, Any, List
from models.user_model import User
from schemas.user_schema import UserUpdate
from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import UUID


class UserService:
    def update_user_data(self, user_id: UUID, new_user_data: UserUpdate, db: Session) -> User:
        user: User = self.get_user(user_id, db)
        
        update_data: Dict[str, Any] = new_user_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)

        db.add(user)
        db.flush()
        db.refresh(user)

        return user
    

    def get_all_users(self, db: Session) -> List[User]:
        return db.query(User).all()

    
    def delete_user(self, user_id: UUID, db: Session) -> int:
        return db.query(User).filter(User.id == user_id).delete()


    def get_user(self, user_id: UUID, db: Session) -> User:
        return db.query(User).filter(User.id == user_id).first()
    

user_service: UserService = UserService()