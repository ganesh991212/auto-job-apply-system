from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://postgres:postgres123@localhost:5432/auto_job_apply"
    
    # ML Models
    spacy_model: str = "en_core_web_sm"
    transformers_model: str = "gpt2"
    sentence_transformer_model: str = "all-MiniLM-L6-v2"
    
    # Processing limits
    max_text_length: int = 10000
    max_file_size_mb: int = 5
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    class Config:
        env_file = ".env"


settings = Settings()
