from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from schemas import ApplicationUpdate, ApplicationCreate, GmailAnalyzedResponse
from models import User, Application, ApplicationStatus, ChainComponent
from scripts.exceptions import UserDoesntExist, ApplicationAlreadyExists, CustomException
from datetime import datetime
from config.logger import Logger


logger = Logger(__name__).configure()


class ApplicationService:
    def get_all_applications(self, db: Session) -> List[Application]:
        return db.query(Application).all()
    

    def get_users_applications(self, user_id: UUID, db: Session) -> List[Application]:
        return db.query(Application).filter(Application.user_id == user_id).all()
    

    # non rejected for cron updating
    def get_users_active_applications(self, user_id: UUID, db: Session) -> List[Application]:
        return db.query(Application).filter(Application.user_id == user_id, 
                                            Application.current_status != ApplicationStatus.REJECTION.value).all()
    

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


    def add_email_components(self, appl_id: UUID, new_data: Optional[List[ChainComponent]], db: Session) -> Application:
        application: Application = db.query(Application).filter(Application.id == appl_id).first()

        email_ids_map: Dict[str, ChainComponent] = {comp["message_id"]: comp for comp in application.email_chain}        
        if new_data:
            for msg in new_data:
                if isinstance(msg["received_at"], datetime):
                    msg["received_at"] = msg["received_at"].isoformat()
                email_ids_map[msg["message_id"]] = msg

        components: List[ChainComponent] = list(email_ids_map.values())
        components.sort(key=lambda c: c["received_at"], reverse=True)

        current_status: ApplicationStatus = application.current_status
        if components:
            # TODO - if last message is REJECCTION, then it should stay like that and don't change
            # but then there should be good email filtration to remoce IRRELEVANT messsages
            current_status = components[0]["status"]
        
        application.email_chain = components
        application.current_status = current_status

        db.add(application)
        db.flush()
        db.refresh(application)

        return application
    

    def save_emails(self, applications: List[Application], analysed_messages: List[GmailAnalyzedResponse], db: Session) -> List[Application]:
        saved_applications: List[Application] = []
        
        for application, message in zip(applications, analysed_messages):
            if isinstance(message, CustomException):
                logger.error(f"(Custom) Error syncing application {application.id}: {message}")
                raise message
            if isinstance(message, Exception):
                logger.error(f"Error syncing application {application.id}: {message}")
                continue
            if not message:
                saved_applications.append(application)
                continue
            
            try:
                saved_application: Application = self.add_email_components(application.id, message, db)
                saved_applications.append(saved_application)
            except Exception as e:
                logger.error(f"DB error saving application {application.id}: {e}")
                saved_applications.append(application)
        
        return saved_applications
    

    def delete_application(self, appl_id: UUID, db: Session) -> int:
        return db.query(Application).filter(Application.id == appl_id).delete()


application_service: ApplicationService = ApplicationService()