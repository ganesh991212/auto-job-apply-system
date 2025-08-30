from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://postgres:postgres123@localhost:5432/auto_job_apply"
    
    # Auth Service
    auth_service_url: str = "http://auth-service:8000"
    
    # Job Application Limits
    candidate_daily_limit: int = 5
    admin_daily_limit: int = -1  # Unlimited
    
    # LinkedIn API (Mock)
    linkedin_api_base: str = "https://api.linkedin.com/v2"
    linkedin_client_id: Optional[str] = None
    linkedin_client_secret: Optional[str] = None
    
    # Naukri API (Mock)
    naukri_api_base: str = "https://api.naukri.com/v1"
    naukri_api_key: Optional[str] = None
    
    # Selenium WebDriver
    webdriver_headless: bool = True
    webdriver_timeout: int = 30
    
    # Redis for Celery
    redis_url: str = "redis://localhost:6379/0"
    
    # CORS
    cors_origins: list = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    class Config:
        env_file = ".env"


settings = Settings()
