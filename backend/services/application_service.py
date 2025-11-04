from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from schemas.application_schema import ApplicationUpdate, ApplicationCreate
from models.application_model import Application
from models.user_model import User
from scripts.exceptions import UserDoesntExist, ApplicationAlreadyExists


class ApplicationService:
    def get_all_applications(self, db: Session) -> List[Application]:
        return db.query(Application).all()
    

    def get_users_applications(self, user_id: UUID, db: Session) -> List[Application]:
        return db.query(Application).filter(Application.user_id == user_id).all()
    

    def register_new_application(self, user_id: UUID, data: ApplicationCreate, db: Session) -> Application:
        existing_user: Optional[UUID] = db.query(User.id).filter(User.id == user_id).first()
        if not existing_user:
            raise UserDoesntExist
        db_application_id: Optional[UUID] = db.query(Application.id).filter(Application.job_title == data.job_title,
                                                                      Application.company_name == data.company_name,
                                                                      Application.user_id == user_id).first()
        
        if db_application_id:
            raise ApplicationAlreadyExists(f"Application {data.job_title} from {data.company_name} already registered under your name.")

        new_application = Application(
            user_id=user_id,
            company_name=data.company_name,
            job_title=data.job_title,
            current_status=data.current_status,
            email_chain=[]
        )
        db.add(new_application)
        db.flush()
        db.refresh(new_application)

        return new_application


    def update_application(self, appl_id: UUID, new_data: ApplicationUpdate, db: Session) -> Application:
        application: Application = db.query(Application).filter(Application.id == appl_id).first()

        update_data: Dict[str, Any] = new_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(application, key, value)

        db.add(application)
        db.flush()
        db.refresh(application)

        return application
    

    def delete_application(self, appl_id: UUID, db: Session) -> int:
        return db.query(Application).filter(Application.id == appl_id).delete()


application_service: ApplicationService = ApplicationService()