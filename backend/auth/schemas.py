from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    CANDIDATE = "candidate"
    SUPER_ADMIN = "super_admin"


class OAuthProvider(str, Enum):
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    APPLE = "apple"


# Request schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class EmailOTPRequest(BaseModel):
    email: EmailStr


class EmailOTPVerify(BaseModel):
    email: EmailStr
    otp_code: str


class OAuthLoginRequest(BaseModel):
    provider: OAuthProvider
    authorization_code: str
    redirect_uri: str


class TokenRefresh(BaseModel):
    refresh_token: str


class PasswordReset(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    email: EmailStr
    reset_code: str
    new_password: str


# Response schemas
class UserResponse(BaseModel):
    id: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    role: UserRole
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class OTPResponse(BaseModel):
    message: str
    expires_in: int


class MessageResponse(BaseModel):
    message: str


class UserProfileResponse(BaseModel):
    id: str
    user_id: str
    current_lpa: Optional[str]
    expected_lpa: Optional[str]
    skills: Optional[List[str]]
    resume_file_path: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Internal schemas
class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None


class AuditLogCreate(BaseModel):
    user_id: Optional[str]
    action: str
    resource: Optional[str]
    details: Optional[dict]
    ip_address: Optional[str]
    user_agent: Optional[str]
