from models import Application
from typing import List, Dict, Optional, Tuple, Set, Optional
from scripts.exceptions import GmailRefreshTokenExpired
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import Resource
from schemas.gmail_schema import GmailAnalyzedResponse, GmailResponse
from services.ai_service import AIService
from models import ChainComponent, Application
import base64
from config.logger import Logger
from services.query_contructor_service import QueryConstructor
from email.utils import parseaddr, parsedate_to_datetime
from bs4 import BeautifulSoup


logger = Logger(__name__).configure()


class ParsingService:
    def __init__(self) -> None:
        self.ai = AIService()
        self.constructor = QueryConstructor()


    def process_application(self, service: Resource, application: Application) -> Optional[List[ChainComponent]]:
        q: Tuple[Optional[str], ...] = self.constructor.construct_queries(application)

        raw_messages: List[Dict] = self._execute_queries(service, *q)
        messages: List[GmailResponse] = [self._parse_message(message) for message in raw_messages]
        analysed_messages: List[GmailAnalyzedResponse] = self.ai.analyze(messages)
        
        if len(analysed_messages) == 0:
            return None
        
        components: List[ChainComponent] = [ChainComponent(**msg.model_dump(exclude={"body"})) for msg in analysed_messages]
        return components
        # return {"vacancy": f"{application.company_name}: {application.job_title}", "messages": analysed_messages}

    
    def _execute_queries(self, service: Resource, *queries: str) -> List[Dict]:
        unique_message_ids: Set[str] = set()
        for q in queries:
            if not q: continue
            results = self._fetch_ids(service, q)
            for message in results:
                unique_message_ids.add(message["id"])

        unique_message_list: List[Dict] = []
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
            return results.get("messages", []) # only message ids
        except RefreshError:
            raise GmailRefreshTokenExpired()
        except Exception as e:
            logger.error(f"Error fetching messages from gmail {q=}: {e}")
            return []
            


    def __get_email_body(self, message: Dict) -> Optional[str]:
        # payload -> body -> data
        # !data => payload -> parts -> body -> data
        # !data => parts -> parts -> body -> data
        # ...

        payload = message.get("payload", {})

        queue = [payload]
        while queue:
            current_part: Dict = queue.pop(0)
            mimetype: str = current_part.get("mimeType")
            html: Optional[str] = None

            if mimetype == "text/plain":
                body_encoded = current_part.get("body", {}).get("data")
                if body_encoded:
                    return self.__decode_body(body_encoded, message["id"])
                
            elif mimetype == "text/html":
                body_encoded = current_part.get("body", {}).get("data")
                if body_encoded:
                    html = self.__decode_body(body_encoded, message["id"])

            if "parts" in current_part:
                queue.extend(current_part["parts"])

        if html:
            soup = BeautifulSoup(html, "html.parser")
            tags_to_delete = soup.find_all(["a", "img"])
            for tag in tags_to_delete:
                tag.decompose()
            clean_text: str = soup.get_text(separator=" ", strip=True)
            return clean_text
        
        logger.info(f"message with id={message.get('id')} doesn't contain a text/plain or html body")
        return None

    
    def __decode_body(self, body_encoded: str, msg_id: str) -> Optional[str]:
        padding = len(body_encoded) % 4
        if padding:
            body_encoded += "=" * (4 - padding)

        try:
            decoded_bytes: bytes = base64.urlsafe_b64decode(body_encoded)
            try:
                return decoded_bytes.decode("utf-8").replace("\r", "")
            except UnicodeDecodeError:
                return decoded_bytes.decode("latin-1").replace("\r", "")
                
        except Exception as e:
            logger.error(f"message with id={msg_id} has critical decoding error: {e}")
            try:
                 return base64.urlsafe_b64decode(body_encoded).decode("utf-8", errors="replace").replace("\r", "")
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
    

parsing_service: ParsingService = ParsingService()