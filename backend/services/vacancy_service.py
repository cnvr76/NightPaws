from typing import List, Dict, Optional, Union
from models.vacancy_model import Vacancy, VacancyStatus
from schemas.vacancy_schema import VacancyCreate


class VacancyService:
    async def create_vacancy(self, data: VacancyCreate) -> Vacancy:
        vacancy = Vacancy(**data.model_dump())
        await vacancy.save()
        return vacancy
    
    async def get_all_vacancies(self) -> List[Vacancy]:
        return await Vacancy.find(Vacancy.status == VacancyStatus.ACTIVE).to_list()
    
    async def get_vacancy_by_id(self, vacancy_id: str) -> Optional[Vacancy]:
        return await Vacancy.get(vacancy_id)
    

vacancy_service: VacancyService = VacancyService()