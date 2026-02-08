from celery import Celery
import os, dotenv


dotenv.load_dotenv()
REDIS_URL = os.getenv("REDIS_URL")

celery_app = Celery(
    "nightpaws_worker",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    include=["services.tasks_service"],
    
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True
)