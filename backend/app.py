from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.application_route import router as application_router
from routes.user_route import router as user_router
from routes.auth_route import router as auth_router


app = FastAPI(
    title="NightPaws",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Cache-Control", "Pragma"]
)

app.include_router(application_router, prefix="/applications", tags=["applications"])
app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
