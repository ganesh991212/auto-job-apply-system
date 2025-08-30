from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import List, Optional
import httpx

from database import get_db, engine
from models import Base, JobApplication, JobPlatform, UserPlatformCredential
from schemas import (
    JobApplicationCreate, JobApplicationResponse, JobMatchRequest,
    JobMatchResponse, PlatformCredentialCreate, MessageResponse
)
from auth_middleware import get_current_user, require_role
from job_platforms import LinkedInHandler, NaukriHandler
from config import settings

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Auto Job Apply - Core Service",
    description="Core job application and management service",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()


@app.post("/jobs/apply", response_model=JobApplicationResponse)
async def apply_to_job(
    job_data: JobApplicationCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Apply to a specific job"""
    user_id = current_user["user_id"]
    user_role = current_user["role"]
    
    # Check daily application limit for candidates
    if user_role == "candidate":
        today = date.today()
        today_applications = db.query(JobApplication).filter(
            JobApplication.user_id == user_id,
            JobApplication.applied_at >= datetime.combine(today, datetime.min.time())
        ).count()
        
        if today_applications >= settings.candidate_daily_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Daily application limit of {settings.candidate_daily_limit} reached"
            )
    
    # Get platform handler
    platform = db.query(JobPlatform).filter(JobPlatform.id == job_data.platform_id).first()
    if not platform:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job platform not found"
        )
    
    # Get user credentials for the platform
    credentials = db.query(UserPlatformCredential).filter(
        UserPlatformCredential.user_id == user_id,
        UserPlatformCredential.platform_id == job_data.platform_id,
        UserPlatformCredential.is_active == True
    ).first()
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No credentials found for {platform.name}"
        )
    
    try:
        # Get platform handler
        handler = _get_platform_handler(platform.name)
        
        # Apply to job
        application_result = await handler.apply_to_job(
            job_data.job_url,
            credentials,
            job_data.cover_letter
        )
        
        # Log the application
        job_application = JobApplication(
            user_id=user_id,
            platform_id=job_data.platform_id,
            company_name=job_data.company_name,
            job_title=job_data.job_title,
            job_description=job_data.job_description,
            job_url=job_data.job_url,
            application_status="applied"
        )
        
        db.add(job_application)
        db.commit()
        db.refresh(job_application)
        
        return JobApplicationResponse.from_orm(job_application)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply to job: {str(e)}"
        )


@app.get("/jobs/history", response_model=List[JobApplicationResponse])
async def get_job_history(
    skip: int = 0,
    limit: int = 50,
    company_filter: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's job application history"""
    user_id = current_user["user_id"]
    
    query = db.query(JobApplication).filter(JobApplication.user_id == user_id)
    
    # Apply filters
    if company_filter:
        query = query.filter(JobApplication.company_name.ilike(f"%{company_filter}%"))
    
    if date_from:
        query = query.filter(JobApplication.applied_at >= datetime.combine(date_from, datetime.min.time()))
    
    if date_to:
        query = query.filter(JobApplication.applied_at <= datetime.combine(date_to, datetime.max.time()))
    
    # Order by most recent first
    query = query.order_by(JobApplication.applied_at.desc())
    
    # Pagination
    applications = query.offset(skip).limit(limit).all()
    
    return [JobApplicationResponse.from_orm(app) for app in applications]


@app.get("/jobs/stats")
async def get_job_stats(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's job application statistics"""
    user_id = current_user["user_id"]
    
    # Total applications
    total_applications = db.query(JobApplication).filter(
        JobApplication.user_id == user_id
    ).count()
    
    # Today's applications
    today = date.today()
    today_applications = db.query(JobApplication).filter(
        JobApplication.user_id == user_id,
        JobApplication.applied_at >= datetime.combine(today, datetime.min.time())
    ).count()
    
    # This month's applications
    month_start = today.replace(day=1)
    month_applications = db.query(JobApplication).filter(
        JobApplication.user_id == user_id,
        JobApplication.applied_at >= datetime.combine(month_start, datetime.min.time())
    ).count()
    
    # Remaining applications for today (for candidates)
    remaining_today = None
    if current_user["role"] == "candidate":
        remaining_today = max(0, settings.candidate_daily_limit - today_applications)
    
    return {
        "total_applications": total_applications,
        "today_applications": today_applications,
        "month_applications": month_applications,
        "remaining_today": remaining_today,
        "daily_limit": settings.candidate_daily_limit if current_user["role"] == "candidate" else None
    }


@app.post("/platforms/credentials", response_model=MessageResponse)
async def save_platform_credentials(
    credentials: PlatformCredentialCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save encrypted platform credentials for user"""
    user_id = current_user["user_id"]
    
    # Check if platform exists
    platform = db.query(JobPlatform).filter(JobPlatform.id == credentials.platform_id).first()
    if not platform:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job platform not found"
        )
    
    # Check if credentials already exist
    existing_creds = db.query(UserPlatformCredential).filter(
        UserPlatformCredential.user_id == user_id,
        UserPlatformCredential.platform_id == credentials.platform_id
    ).first()
    
    if existing_creds:
        # Update existing credentials
        existing_creds.username = _encrypt_data(credentials.username)
        existing_creds.password = _encrypt_data(credentials.password)
        existing_creds.api_key = _encrypt_data(credentials.api_key) if credentials.api_key else None
        existing_creds.is_active = True
    else:
        # Create new credentials
        new_creds = UserPlatformCredential(
            user_id=user_id,
            platform_id=credentials.platform_id,
            username=_encrypt_data(credentials.username),
            password=_encrypt_data(credentials.password),
            api_key=_encrypt_data(credentials.api_key) if credentials.api_key else None
        )
        db.add(new_creds)
    
    db.commit()
    
    return MessageResponse(message="Platform credentials saved successfully")


@app.get("/platforms", response_model=List[dict])
async def get_job_platforms(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available job platforms"""
    platforms = db.query(JobPlatform).filter(JobPlatform.is_active == True).all()
    
    result = []
    for platform in platforms:
        # Check if user has credentials for this platform
        has_credentials = db.query(UserPlatformCredential).filter(
            UserPlatformCredential.user_id == current_user["user_id"],
            UserPlatformCredential.platform_id == platform.id,
            UserPlatformCredential.is_active == True
        ).first() is not None
        
        result.append({
            "id": str(platform.id),
            "name": platform.name,
            "has_credentials": has_credentials
        })
    
    return result


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "core", "timestamp": datetime.utcnow()}


# Admin endpoints
@app.get("/admin/applications", response_model=List[JobApplicationResponse])
async def get_all_applications(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(require_role("super_admin")),
    db: Session = Depends(get_db)
):
    """Get all job applications (Super Admin only)"""
    applications = db.query(JobApplication).order_by(
        JobApplication.applied_at.desc()
    ).offset(skip).limit(limit).all()
    
    return [JobApplicationResponse.from_orm(app) for app in applications]


@app.post("/admin/platforms", response_model=MessageResponse)
async def add_job_platform(
    platform_data: dict,
    current_user: dict = Depends(require_role("super_admin")),
    db: Session = Depends(get_db)
):
    """Add new job platform (Super Admin only)"""
    platform = JobPlatform(
        name=platform_data["name"],
        api_endpoint=platform_data.get("api_endpoint")
    )
    
    db.add(platform)
    db.commit()
    
    return MessageResponse(message="Job platform added successfully")


def _encrypt_data(data: str) -> str:
    """Encrypt sensitive data using the same encryption as auth service"""
    from cryptography.fernet import Fernet
    # This should use the same encryption key as the auth service
    key = settings.encryption_key.encode() if hasattr(settings, 'encryption_key') else Fernet.generate_key()
    fernet = Fernet(key)
    return fernet.encrypt(data.encode()).decode()


def _get_platform_handler(platform_name: str):
    """Get appropriate platform handler"""
    handlers = {
        "LinkedIn": LinkedInHandler(),
        "Naukri": NaukriHandler()
    }
    
    handler = handlers.get(platform_name)
    if not handler:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported platform: {platform_name}"
        )
    
    return handler


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
