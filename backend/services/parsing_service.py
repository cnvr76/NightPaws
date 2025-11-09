from models import User, Application
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from scripts.exceptions import UnableToDecryptGmailRefreshToken, GmailRefreshTokenMissing
from googleapiclient.discovery import Resource


class ParsingService:
    def execute_query(self, service: Resource, q: str):
        results = service.users().messages().list(
            userId="me",
            q=q,
            maxResults=5
        ).execute()

        message_ids: List[Dict] = results.get("messages", [])
        if not message_ids:
            return []
        
        detailed_messages: List[Dict] = []
        
        for msg_id_data in message_ids:
            msg_id = msg_id_data['id']
            
            # Робимо запит на 'get', але просимо тільки 'metadata'
            # Це дасть нам 'snippet' і 'headers' (де є 'From', 'Date')
            message_data = service.users().messages().get(
                userId="me", 
                id=msg_id,
                format="metadata"
            ).execute()
            
            # Тепер message_data - це повний об'єкт листа
            # (без тіла, але нам і не треба)
            detailed_messages.append(message_data)
        
        # TODO - extract needed info from messages
        return detailed_messages
    

    def wide_filter(self, messages: List[Dict]) -> List[Dict]:
        pass


    def narrow_filter(self, messages: List[Dict]) -> List[Dict]:
        pass


parsing_service: ParsingService = ParsingService()