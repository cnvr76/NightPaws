import redis
import dotenv, os


dotenv.load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")
SYNC_TIMEOUT = 5 # minutes

redis_client = redis.from_url(
    REDIS_URL,
    decode_responses=True
)