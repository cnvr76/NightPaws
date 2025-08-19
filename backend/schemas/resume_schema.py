from pydantic import BaseModel
from typing import List, Dict, Optional
from models.vacancy_model import SeniorityLevel
from datetime import datetime 


class ResumeCreate(BaseModel):
    content: str
    file_url: str
    original_filename: str
    file_type: str


class ResumeResponse(BaseModel):
    id: str
    user_id: str
    content: str
    file_url: str
    original_filename: str
    file_type: str

    skills: List[Dict[str, str]]
    seniority_level: Optional[SeniorityLevel]
    experience_years: Optional[int]

    created_at: datetime

    model_config = {"from_attributes": True}


class ResumeUpdate(BaseModel):
    content: Optional[str] = None
    skills: Optional[List[Dict[str, str]]] = None
    seniority_level: Optional[SeniorityLevel] = None
    experience_years: Optional[int] = None


class ResumeBrief(BaseModel):
    id: str
    user_id: str
    original_filename: str
    skills: List[Dict[str, str]]
    created_at: datetime

    model_config = {"from_attributes": True}