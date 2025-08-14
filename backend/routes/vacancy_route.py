from fastapi import APIRouter, HTTPException
from typing import List
from schemas.vacancy_schema import VacancyCreate, VacancyResponse
from services.vacancy_service import vacancy_service


router = APIRouter()


@router.get("/", response_model=List[VacancyResponse])
async def get_vacancies():
    return await vacancy_service.get_all_vacancies()