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
from email.utils import parseaddr, parsedate_to_datetime


logger = Logger(__name__).configure()


class ParsingService:
    def __init__(self) -> None:
        self.ai = AIService()
        self.constructor = QueryConstructor()


    async def process_application(self, service: Resource, application: Application): # -> ChainComponent:
        q: Tuple[Optional[str], ...] = self.constructor.construct_queries(application)
        print(q)
        # TODO - everything else
        raw_messages: List[Dict] = await self._execute_queries(service, *q)
        messages: List[GmailResponse] = [self._parse_message(message) for message in raw_messages]
        return messages

    
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


    def __get_email_body(self, message: Dict) -> Optional[str]:
        payload: Dict = message["payload"]
        body_encoded: str = payload.get("body", {}).get("data")
        if not body_encoded:
            logger.info(f"Searching for body in parts for message with id={message['id']}")
            parts: List[Dict] = payload.get("parts", [])
            for part in parts:
                mimetype: str = part.get("mimeType")
                if mimetype == "text/plain":
                    body_encoded = part.get("body", {}).get("data")
                    break
            if not body_encoded:
                logger.info(f"message with id={message["id"]} doesn't contain a body")
                return None
        
        padding = len(body_encoded) % 4
        if padding:
            body_encoded += "=" * (4 - padding)

        try:
            decoded_bytes: bytes = base64.urlsafe_b64decode(body_encoded)
            try:
                return decoded_bytes.decode("utf-8")
            except UnicodeDecodeError:
                return decoded_bytes.decode("latin-1")
                
        except Exception as e:
            logger.error(f"message with id={message['id']} critical decoding error: {e}")
            try:
                 return base64.urlsafe_b64decode(body_encoded).decode("utf-8", errors="replace")
            except:
                 return None
        
    
    def __get_header_info(self, message: Dict) -> Dict[str, str]:
        headers: List[Dict] = message["payload"]["headers"]
        info: Dict[str, str] = {}
        search_headers: Tuple[str, ...] = ("From", "Subject", "Date")
        for header in headers:
            name, value = header["name"], header["value"]
            if name in search_headers:
                info.update({name.lower(): value})
        return info
    

    def _parse_message(self, message: Dict) -> GmailResponse:
        message_id: str = message["id"]
        thread_id: str = message["threadId"]
        body: Optional[str] = self.__get_email_body(message)
        info: Dict[str, str] = self.__get_header_info(message)
        sender, subject, received_at = info["from"], info["subject"], info["date"]
        name, email = parseaddr(sender)
        return GmailResponse(
            message_id=message_id,
            thread_id=thread_id,
            subject=subject,
            body=body,
            sender={"name": name, "email": email},
            received_at=parsedate_to_datetime(received_at)
        )
    

    def _filter_messages(self, messages: List[GmailResponse]) -> List[GmailResponse]:
        pass


    def _ai_analysis(self, message: GmailResponse) -> GmailAnalyzedResponse:
        pass


    def _make_chain_component(self, message: GmailAnalyzedResponse) -> ChainComponent:
        pass
    

parsing_service: ParsingService = ParsingService()