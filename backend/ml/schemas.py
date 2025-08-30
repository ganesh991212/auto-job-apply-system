from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ResumeMatchRequest(BaseModel):
    resume_text: str
    job_description: str


class ResumeMatchResponse(BaseModel):
    match_score: float
    missing_keywords: List[str]
    common_skills: List[str]
    resume_skills_count: int
    job_skills_count: int


class ResumeEnhanceRequest(BaseModel):
    resume_text: str
    missing_skills: Optional[List[str]] = None
    target_job_title: Optional[str] = None


class ResumeEnhanceResponse(BaseModel):
    suggestions: List[str]
    recommended_skills: List[str]
    current_skills: List[str]


class SkillExtractionResponse(BaseModel):
    extracted_text: str
    skills: List[str]
    skill_count: int


class MessageResponse(BaseModel):
    message: str
