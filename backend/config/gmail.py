import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from fastapi.security import OAuth2PasswordBearer, HTTPBearer


load_dotenv()


ENCRYPTION_KEY = os.getenv("FERNET_KEY")
fernet_cipher = Fernet(ENCRYPTION_KEY.encode())

CLIENT_SECRET = os.getenv("CLIENT_SECRET")
CLIENT_ID = os.getenv("CLIENT_ID")
REDIRECT_URI = os.getenv("REDIRECT_URI")
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

AUTH_URI = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URI = "https://oauth2.googleapis.com/token"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
bearer_scheme = HTTPBearer()

google_config = {
    "web": {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "auth_uri": AUTH_URI,
        "token_uri": TOKEN_URI,
        "redirect_uri": [REDIRECT_URI]
    }
}