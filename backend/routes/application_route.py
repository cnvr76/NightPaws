from fastapi import APIRouter, HTTPException
from typing import List
from services.application_service import vacancy_service


router = APIRouter()


@router.get("/", response_model=None)
async def get_applications():
    try:
        pass
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))