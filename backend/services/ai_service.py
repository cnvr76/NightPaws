from schemas.gmail_schema import GmailAnalyzedResponse, GmailResponse
from models import EmailStatus, Application
from typing import List
from config.logger import Logger
from setfit import SetFitModel
import json
import threading


logger = Logger(__name__).configure()


class AIService:
    def __init__(self) -> None:
        self.model_path = "training_data/my_email_classifier"
        logger.info(f"Loading custom model from {self.model_path}...")
        
        try:
            self.model = SetFitModel.from_pretrained(self.model_path)
            
            with open(f"{self.model_path}/labels_map.json", "r") as f:
                self.id2label = json.load(f)
                
            logger.info("Custom Model loaded!")
        except Exception as e:
            logger.error(f"Failed to load model. You probably need to run train_classifier.py. Error: {e}")
            raise e
        
        self.lock = threading.Lock()

    def analyze(self, application: Application, messages: List[GmailResponse]) -> List[GmailAnalyzedResponse]:
        if not messages:
            return []

        results: List[GmailAnalyzedResponse] = []
        inputs: List[str] = []
        message_map: List[GmailResponse] = []

        for message in messages:
            clean_body = " ".join(message.body.split()) if message.body else ""

            text = f"{message.subject}. {clean_body}"
            inputs.append(text)
            message_map.append(message)

        try:
            with self.lock:
                preds = self.model.predict(inputs)
                # probs = self.model.predict_proba(inputs)

            for i, label_id in enumerate(preds):
                message = message_map[i]
                
                label_str = self.id2label[str(label_id.item())]
                
                try:
                    final_status = EmailStatus(label_str.lower())
                except ValueError:
                    final_status = EmailStatus.OTHER

                logger.info(f"Msg {message.message_id} -> {final_status.value.upper()}")

                if not final_status.is_valid:
                    continue

                results.append(GmailAnalyzedResponse(
                    **message.model_dump(),
                    status=final_status
                ))

        except Exception as e:
            logger.error(f"AI Inference Error: {e}")
            for message in messages:
                results.append(GmailAnalyzedResponse(**message.model_dump(), status=EmailStatus.OTHER))

        return results