from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.database import db_config

from routes.vacancy_route import router as vacancy_router


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
app.include_router(vacancy_router, prefix="/vacancies", tags=["vacancies"])

@app.on_event("startup")
async def startup():
    await db_config.connect()
    print("Connecting to MongoDB")

@app.on_event("shutdown")
async def shutdown():
    await db_config.disconnect()
    print("Disconnecting from MongoDB")
