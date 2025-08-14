from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from models.vacancy_model import WorkFormat, EmploymentType, VacancyStatus


class VacancyCreate(BaseModel):
    title: str
    description: str
    position: str
    company_id: str
    location: Dict[str, str] = {"city": "", "country": ""}
    salary: Dict[str, Union[str, int]] = None
    experience_min: int = 0
    work_formats: List[WorkFormat] = []
    employment_types: List[EmploymentType] = []
    skills: List[Dict[str, str]] = []
    job_source: Optional[str] = None
    original_link: Optional[str] = None

class VacancyResponse(BaseModel):
    id: str
    title: str
    description: str
    position: str
    company_id: str
    location: Dict[str, str]
    salary: Optional[Dict[str, Union[str, int]]]
    experience_min: int
    work_formats: List[WorkFormat]
    employment_types: List[EmploymentType]
    skills: List[Dict[str, str]]
    job_source: Optional[str]
    original_link: Optional[str]
    status: VacancyStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
