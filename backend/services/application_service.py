from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.exc import IntegrityError
from schemas import ApplicationUpdate, ApplicationCreate, ApplicationMessageUpdate
from models import User, Application, ApplicationStatus, ChainComponent
from scripts.exceptions import UserDoesntExist, ApplicationAlreadyExists, CustomException
from datetime import datetime
from config.logger import Logger


logger = Logger(__name__).configure()


class ApplicationService:
    def get_all_applications(self, db: Session) -> List[Application]:
        return db.query(Application).all()
    

    def get_application_by_id(self, user_id: UUID, appl_id: UUID, db: Session) -> Application:
        return db.query(Application).filter(
            Application.user_id == user_id, 
            Application.id == appl_id
        ).first()
    

    def get_users_applications(self, user_id: UUID, db: Session) -> List[Application]:
        return db.query(Application).filter(Application.user_id == user_id).all()
    

    # non rejected for cron updating
    def get_users_active_applications(self, user_id: UUID, db: Session) -> List[Application]:
        skip_statuses: List[str] = [
            status.value
            for status in ApplicationStatus
            if not status.is_syncable
        ]
        
        return db.query(Application).filter(
            Application.user_id == user_id, Application.current_status.notin_(skip_statuses)
        ).all()
    

    def register_new_application(self, user_id: UUID, data: ApplicationCreate, db: Session) -> Application:
        processed_company: str = " ".join(data.company_name.split())
        processed_title: str = " ".join(data.job_title.split())
        try:
            new_application = Application(
                user_id=user_id,
                company_name=processed_company,
                job_title=processed_title,
                current_status=data.current_status,
                applied_at=data.apply_date,
                email_chain=[]
            )
            db.add(new_application)
            db.flush()
            db.refresh(new_application)
            return new_application
        except IntegrityError:
            raise ApplicationAlreadyExists(f"Application {processed_title} from {processed_company} already registered under your name.")
        except Exception as e:
            logger.error(f"Error while registering new application {processed_title} from {processed_company}: {e}")
            raise e
        
        
    def __set_new_appl_data(self, application: Application, data: ApplicationMessageUpdate | ApplicationUpdate) -> Application:
        update_data: Dict[str, Any] = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(application, key, value)
    

    def update_application(self, appl_id: UUID, user_id: UUID, new_data: ApplicationUpdate, db: Session) -> Application:
        application: Application = self.get_application_by_id(user_id, appl_id, db)
        self.__set_new_appl_data(application, new_data)

        db.add(application)
        db.flush()
        db.refresh(application)

        return application
    
    
    def update_message(self, appl_id: UUID, user_id: UUID, message_id: str, new_data: ApplicationMessageUpdate, db: Session) -> Application:
        application: Application = self.get_application_by_id(user_id, appl_id, db)
        
        components: List[ChainComponent] = application.email_chain
        is_modified: bool = False
        
        for comp in components:
            if comp["message_id"] == message_id:
                if status := new_data.message_status:
                    comp["status"] = status
                    is_modified = True
                break
            
        if is_modified:
            components.sort(key=lambda c: c["received_at"], reverse=True)
            application.email_chain = list(components)
            flag_modified(application, "email_chain")
            
            latest_email: ChainComponent = components[0]
            if latest_email["message_id"] == message_id:
                application.current_status = latest_email["status"]
            
            db.add(application)
            db.flush()
            db.refresh(application)
        
        return application
    

    def delete_email(self, appl_id: UUID, message_id: str, user_id: UUID, db: Session) -> Application:
        application: Application = self.get_application_by_id(user_id, appl_id, db)
        
        updated_emails: List[ChainComponent] = [
            message for message in application.email_chain
            if message["message_id"] != message_id
        ]

        if not updated_emails:
            application.current_status = ApplicationStatus.APPLIED
        else:
            updated_emails.sort(key=lambda c: c["received_at"], reverse=True)
            application.current_status = updated_emails[0]["status"]

        application.email_chain = updated_emails
        
        db.add(application)
        db.flush()
        db.refresh(application)

        return application
            

    def add_email_components(self, application: Application, new_data: List[ChainComponent], db: Session) -> Application:
        email_ids_map: Dict[str, ChainComponent] = {comp["message_id"]: comp for comp in application.email_chain}       
        has_new_messages: bool = False
        
        for msg in new_data:
            if msg not in email_ids_map:
                has_new_messages = True
                
                # converting string dates of existing email components to datetime objects
                if isinstance(msg["received_at"], datetime):
                    msg["received_at"] = msg["received_at"].isoformat()
                email_ids_map[msg["message_id"]] = msg

        components: List[ChainComponent] = list(email_ids_map.values())
        components.sort(key=lambda c: c["received_at"], reverse=True)

        if has_new_messages and components:
            # TODO - if last message is REJECCTION, then it should stay like that and don't change
            # but then there should be good email filtration to remove IRRELEVANT messsages
            application.current_status = components[0]["status"]
        
        application.email_chain = components

        db.add(application)
        db.flush()
        db.refresh(application)

        return application
    

    def save_emails(self, applications: List[Application], analysed_messages: List[List[ChainComponent] | Exception | None], db: Session) -> List[Application]:
        saved_applications: List[Application] = []
        
        for application, messages in zip(applications, analysed_messages):
            appl_id: UUID = application.id
            if isinstance(messages, CustomException):
                logger.error(f"(Custom) Error syncing application {appl_id}: {messages}")
                raise messages
            if isinstance(messages, Exception):
                logger.error(f"Error syncing application {appl_id}: {messages}")
                continue
            if not messages:
                saved_applications.append(application)
                continue
            
            try:
                saved_application: Application = self.add_email_components(application, messages, db)
                saved_applications.append(saved_application)
            except Exception as e:
                logger.error(f"DB error saving application {appl_id}: {e}")
                saved_applications.append(application)
        
        return saved_applications
    

    def delete_application(self, appl_id: UUID, user_id: UUID, db: Session) -> int:
        return db.query(Application).filter(
            Application.id == appl_id, 
            Application.user_id == user_id
        ).delete()


application_service: ApplicationService = ApplicationService()