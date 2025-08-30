from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Integer, DECIMAL, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


class JobPlatform(Base):
    __tablename__ = "job_platforms"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    api_endpoint = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    credentials = relationship("UserPlatformCredential", back_populates="platform")
    applications = relationship("JobApplication", back_populates="platform")


class UserPlatformCredential(Base):
    __tablename__ = "user_platform_credentials"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)  # Foreign key to auth service
    platform_id = Column(UUID(as_uuid=True), ForeignKey("job_platforms.id", ondelete="CASCADE"))
    username = Column(String(255))  # Encrypted
    password = Column(String(255))  # Encrypted
    api_key = Column(Text)  # Encrypted
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    platform = relationship("JobPlatform", back_populates="credentials")


class JobApplication(Base):
    __tablename__ = "job_applications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)  # Foreign key to auth service
    platform_id = Column(UUID(as_uuid=True), ForeignKey("job_platforms.id"))
    company_name = Column(String(255), nullable=False)
    job_title = Column(String(255), nullable=False)
    job_description = Column(Text)
    job_url = Column(String(500))
    application_status = Column(String(50), default='applied')
    cover_letter = Column(Text)
    applied_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    platform = relationship("JobPlatform", back_populates="applications")


class JobMatch(Base):
    __tablename__ = "job_matches"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    job_title = Column(String(255), nullable=False)
    job_description = Column(Text)
    company_name = Column(String(255))
    job_url = Column(String(500))
    match_score = Column(DECIMAL(5,2))  # 0.00 to 100.00
    missing_keywords = Column(ARRAY(String))
    suggested_skills = Column(ARRAY(String))
    platform_id = Column(UUID(as_uuid=True), ForeignKey("job_platforms.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    platform = relationship("JobPlatform")


class AutoApplySettings(Base):
    __tablename__ = "auto_apply_settings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), unique=True, nullable=False)
    is_enabled = Column(Boolean, default=False)
    job_titles = Column(ARRAY(String))  # Target job titles
    min_salary = Column(DECIMAL(10,2))
    max_salary = Column(DECIMAL(10,2))
    preferred_locations = Column(ARRAY(String))
    excluded_companies = Column(ARRAY(String))
    min_match_score = Column(DECIMAL(5,2), default=70.0)  # Minimum match score to auto-apply
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
