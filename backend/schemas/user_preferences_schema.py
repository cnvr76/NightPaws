from pydantic import BaseModel
from typing import List, Optional
from models.vacancy_model import WorkFormat, EmploymentType, SeniorityLevel, Currency
from datetime import datetime


class UserPreferencesCreate(BaseModel):
    prefered_locations: List[str] = []
    prefered_companies: List[str] = []
    prefered_job_sources: List[str] = []

    excluded_companies: List[str] = []
    excluded_job_sources: List[str] = []

    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    prefered_currency: Optional[Currency] = None

    work_formats: List[WorkFormat] = []
    employment_types: List[EmploymentType] = []
    seniority_levels: List[SeniorityLevel] = []


class UserPreferencesUpdate(BaseModel):
    prefered_locations: Optional[List[str]] = None
    prefered_companies: Optional[List[str]] = None
    prefered_job_sources: Optional[List[str]] = None

    excluded_companies: Optional[List[str]] = None
    excluded_job_sources: Optional[List[str]] = None
    
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    prefered_currency: Optional[Currency] = None
    
    work_formats: Optional[List[WorkFormat]] = None
    employment_types: Optional[List[EmploymentType]] = None
    seniority_levels: Optional[List[SeniorityLevel]] = None
    
    gmail_sync_enabled: Optional[bool] = None
    auto_apply_enabled: Optional[bool] = None


class UserPreferencesResponse(BaseModel):
    id: str
    user_id: str
    
    prefered_locations: List[str]
    prefered_companies: List[str]
    prefered_job_sources: List[str]

    excluded_companies: List[str]
    excluded_job_sources: List[str]
    
    min_salary: Optional[int]
    max_salary: Optional[int]
    prefered_currency: Optional[Currency]
    
    work_formats: List[WorkFormat]
    employment_types: List[EmploymentType]
    seniority_levels: List[SeniorityLevel]
    
    gmail_connected: bool
    gmail_sync_enabled: bool
    auto_apply_enabled: bool
    
    updated_at: datetime
    
    model_config = {"from_attributes": True}


