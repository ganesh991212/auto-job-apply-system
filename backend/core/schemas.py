from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# Request schemas
class JobApplicationCreate(BaseModel):
    platform_id: str
    company_name: str
    job_title: str
    job_description: Optional[str] = None
    job_url: str
    cover_letter: Optional[str] = None


class PlatformCredentialCreate(BaseModel):
    platform_id: str
    username: str
    password: str
    api_key: Optional[str] = None


class JobMatchRequest(BaseModel):
    job_title: str
    job_description: str
    company_name: Optional[str] = None
    job_url: Optional[str] = None


class AutoApplySettingsCreate(BaseModel):
    is_enabled: bool
    job_titles: List[str]
    min_salary: Optional[Decimal] = None
    max_salary: Optional[Decimal] = None
    preferred_locations: Optional[List[str]] = None
    excluded_companies: Optional[List[str]] = None
    min_match_score: Optional[Decimal] = 70.0


# Response schemas
class JobApplicationResponse(BaseModel):
    id: str
    user_id: str
    platform_id: Optional[str]
    company_name: str
    job_title: str
    job_description: Optional[str]
    job_url: Optional[str]
    application_status: str
    applied_at: datetime
    
    class Config:
        from_attributes = True


class JobPlatformResponse(BaseModel):
    id: str
    name: str
    is_active: bool
    has_credentials: bool = False
    
    class Config:
        from_attributes = True


class JobMatchResponse(BaseModel):
    id: str
    user_id: str
    job_title: str
    job_description: Optional[str]
    company_name: Optional[str]
    job_url: Optional[str]
    match_score: Optional[Decimal]
    missing_keywords: Optional[List[str]]
    suggested_skills: Optional[List[str]]
    platform_id: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class JobStatsResponse(BaseModel):
    total_applications: int
    today_applications: int
    month_applications: int
    remaining_today: Optional[int]
    daily_limit: Optional[int]


class AutoApplySettingsResponse(BaseModel):
    id: str
    user_id: str
    is_enabled: bool
    job_titles: Optional[List[str]]
    min_salary: Optional[Decimal]
    max_salary: Optional[Decimal]
    preferred_locations: Optional[List[str]]
    excluded_companies: Optional[List[str]]
    min_match_score: Optional[Decimal]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    message: str


class JobSearchResult(BaseModel):
    title: str
    company: str
    location: Optional[str]
    salary: Optional[str]
    description: str
    url: str
    posted_date: Optional[datetime]
    match_score: Optional[float]
