from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://postgres:postgres123@localhost:5432/auto_job_apply"
    
    # JWT Settings
    jwt_secret_key: str = "your-super-secret-jwt-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    
    # Encryption
    encryption_key: str = "your-32-byte-encryption-key-here"
    
    # OAuth Settings
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    microsoft_client_id: Optional[str] = None
    microsoft_client_secret: Optional[str] = None
    apple_client_id: Optional[str] = None
    apple_client_secret: Optional[str] = None
    
    # Email/OTP Settings
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    
    # Security
    bcrypt_rounds: int = 12
    otp_expire_minutes: int = 10
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 30
    
    # CORS
    cors_origins: list = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    class Config:
        env_file = ".env"


settings = Settings()
