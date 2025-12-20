from models import User, Application
from sqlalchemy.orm import Session
from typing import List, Dict, Optional, Tuple, Set, Coroutine, Optional
from scripts.exceptions import GmailRefreshTokenExpired
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import Resource
from schemas.gmail_schema import GmailAnalyzedResponse, GmailResponse
from services.ai_service import AIService
from models import ChainComponent, Application
from datetime import datetime
import base64
from config.logger import Logger
import asyncio
from services.query_contructor_service import QueryConstructor


logger = Logger(__name__).configure()


class ParsingService:
    def __init__(self) -> None:
        self.ai = AIService()
        self.constructor = QueryConstructor()


    async def process_application(self, service: Resource, application: Application): # -> ChainComponent:
        q: Tuple[Optional[str], ...] = self.constructor.construct_queries(application)
        print(q)
        # TODO - everything else
        return await self._execute_queries(service, *q)

    
    async def _execute_queries(self, service: Resource, *queries: str) -> List[Dict]:
        tasks: List[Coroutine] = []
        for q in queries:
            if not q: continue
            tasks.append((
                asyncio.to_thread(self._fetch_ids, service, q)
            ))

        all_results: List[List[Dict]] = await asyncio.gather(*tasks)

        unique_message_ids: Set[str] = set()
        unique_message_list: List[Dict] = []

        for message_list in all_results:
            for message in message_list:
                msg_id: str = message["id"]
                if msg_id not in unique_message_ids:
                    unique_message_ids.add(msg_id)
        
        for msg_id in unique_message_ids:
            message_data = service.users().messages().get(
                userId="me", 
                id=msg_id,
                format="full"
            ).execute()
            
            unique_message_list.append(message_data)

        unique_message_list.sort(key=lambda x: int(x['internalDate']), reverse=True)
        return unique_message_list
    

    def _fetch_ids(self, service: Resource, q: str) -> List[Dict]:
        results: Dict = {}
        try:
            results = service.users().messages().list(
                userId="me",
                q=q,
                maxResults=10,
            ).execute()
        except RefreshError:
            raise GmailRefreshTokenExpired()
        except Exception as e:
            logger.error(f"Error fetching messages from gmail {q=}: {e}")
        finally:
            return results.get("messages", []) # only message ids


    def _get_email_body(self, message: Dict) -> Optional[str]:
        payload: Dict = message["payload"]
        body_encoded: str = payload.get("body", {}).get("data")
        if not body_encoded:
            logger.info(f"message with id={message["id"]} doesn't contain a body")
            return None
        
        decoded_bytes: bytes = base64.b64decode(body_encoded)
        try:
            decoded_body: str = decoded_bytes.decode("utf-8")
            return decoded_body
        except UnicodeDecodeError as ude:
            logger.error(f"message with id={message['id']} has problem with decoding: {ude}")
            return None


    def _parse_message(self, message: Dict) -> GmailResponse:
        pass


    def _ai_analysis(self, message: GmailResponse) -> GmailAnalyzedResponse:
        pass


    def _make_chain_component(self, message: GmailAnalyzedResponse) -> ChainComponent:
        pass
    

parsing_service: ParsingService = ParsingService()