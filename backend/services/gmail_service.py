from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build, Resource
from google.auth.transport.requests import AuthorizedSession
from config.gmail import google_config, SCOPES, REDIRECT_URI, fernet_cipher
from models import Application, User, ChainComponent
from scripts.exceptions import GmailRefreshTokenMissing, UnableToDecryptGmailRefreshToken
from services.parsing_service import parsing_service
import asyncio
from config.logger import Logger


logger = Logger(__name__).configure()


class GmailService:
    def __init__(self) -> None:
        self.fetch_batch_size: int = 3
        
        
    def __create_flow(self, state: Optional[str] = None) -> Flow:
        return Flow.from_client_config(
            client_config=google_config,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI,
            state=state
        )


    async def fetch(self, applications: List[Application], current_user: User) ->  List[List[ChainComponent] | Exception | None]:
        semaphore = asyncio.Semaphore(self.fetch_batch_size)
        
        def thread_task(application: Application) -> Optional[List[ChainComponent]]:
            local_service: Resource = self.get_resource_service(current_user)
            return parsing_service.process_application(local_service, application)
        
        async def safe_task(application: Application) -> Optional[List[ChainComponent]]:
            async with semaphore:
                return await asyncio.to_thread(thread_task, application)

        tasks = [safe_task(app) for app in applications]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        return results

    
    def get_google_auth_url(self, state: str) -> str:
        auth_url, _ = self.__create_flow(state).authorization_url(
            access_type="offline",
            prompt="consent",
            include_granted_scopes="true"
        )
        return auth_url
    

    def _decrypt_token(self, encrypted_token: str) -> str:
        return fernet_cipher.decrypt(encrypted_token.encode()).decode()
    

    def _encrypt_token(self, token: str) -> str:
        return fernet_cipher.encrypt(token.encode()).decode()
    

    def process_google_callback(self, auth_code: str, user: User, db: Session) -> None:
        flow: Flow = self.__create_flow()
        try:
            flow.fetch_token(code=auth_code)
        except Exception as e:
            logger.error(f"Error fetching token: {e}")
            raise e
        
        refresh_token: Optional[str] = flow.credentials.refresh_token
        if not refresh_token:
            # refresh_token not accepted, maybe its was already given
            return
        
        session: AuthorizedSession = flow.authorized_session()
        profile_info: Dict[str, Any] = session.get("https://www.googleapis.com/userinfo/v2/me").json()
        connected_email: Optional[str] = profile_info.get("email")
        if connected_email:
            user.work_email = connected_email
        
        user.gmail_refresh_token = self._encrypt_token(refresh_token)
        db.add(user)
        db.flush()

    
    def get_resource_service(self, user: User) -> Resource:
        encrypted_token: Optional[str] = user.gmail_refresh_token
        if not encrypted_token:
            raise GmailRefreshTokenMissing()
        
        try:
            refresh_token: str = self._decrypt_token(encrypted_token)
        except Exception:
            raise UnableToDecryptGmailRefreshToken()
        
        client_config: Dict[str, str] = google_config["web"]
        creds = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri=client_config['token_uri'],
            client_id=client_config['client_id'],
            client_secret=client_config['client_secret'],
            scopes=SCOPES
        )

        return build("gmail", "v1", credentials=creds, static_discovery=False)


gmail_service: GmailService = GmailService()