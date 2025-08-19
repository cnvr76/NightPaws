from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Optional, Union
from models.vacancy_model import WorkFormat, EmploymentType, VacancyStatus, SeniorityLevel, Salary
from schemas.company_schema import CompanyResponse


class VacancyCreate(BaseModel):
    title: str
    description: str
    position: str
    company_id: str
    location: Dict[str, str] = {"city": "", "country": ""}
    salary: Optional[Salary] = None
    experience_years: int = 0
    work_formats: List[WorkFormat] = []
    employment_types: List[EmploymentType] = []
    skills: List[Dict[str, str]] = []
    job_source: Optional[str] = None
    original_link: Optional[str] = None


class VacancyUpdate(BaseModel):
    summary: Optional[str] = None
    salary: Optional[Salary] = None
    experience_years: Optional[int] = None
    work_formats: Optional[List[WorkFormat]] = None
    employment_types: Optional[List[EmploymentType]] = None
    skills: Optional[List[Dict[str, str]]] = None
    seniority_levels: Optional[List[SeniorityLevel]] = None
    status: Optional[VacancyStatus] = None
    updated_at: Optional[datetime] = None


class VacancyResponse(BaseModel):
    id: str
    title: str
    description: str
    summary: Optional[str]
    position: str
    company_id: str
    company: CompanyResponse
    location: Dict[str, str]
    salary: Optional[Salary]
    experience_years: int
    work_formats: List[WorkFormat]
    employment_types: List[EmploymentType]
    skills: List[Dict[str, str]]
    seniority_levels: List[SeniorityLevel]
    job_source: Optional[str]
    original_link: Optional[str]
    status: VacancyStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class VacancyBrief(BaseModel):
    id: str
    title: str
    position: str
    summary: Optional[str]
    company_id: str
    company: CompanyResponse
    salary: Optional[Salary]
    work_formats: List[WorkFormat]
    employment_types: List[EmploymentType]
    seniority_levels: List[SeniorityLevel]
    original_link: Optional[str]
    
    model_config = {"from_attributes": True}
