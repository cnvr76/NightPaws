import dotenv, os
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
import ssl

from models.vacancy_model import Vacancy

dotenv.load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")


class DatabaseConfig:
    def __init__(self):
        self.mongodb_url: str = MONGODB_URL
        self.database_name: str = DATABASE_NAME
        self.client = None
        self.database = None
    
    async def connect(self):
        self.client = AsyncIOMotorClient(
            self.mongodb_url,
        )
        self.database = self.client[self.database_name]

        await init_beanie(
            database=self.database,
            document_models=[Vacancy]
        )
    
    async def disconnect(self):
        if self.client:
            self.client.close()


db_config: DatabaseConfig = DatabaseConfig()