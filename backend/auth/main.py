from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, Any

from database import get_db, engine
from models import Base, User, OAuthProvider
from schemas import (
    UserRegister, UserLogin, EmailOTPRequest, EmailOTPVerify,
    OAuthLoginRequest, TokenRefresh, UserResponse, TokenResponse,
    OTPResponse, MessageResponse, AuditLogCreate
)
from auth_utils import AuthUtils, get_current_user, require_role, get_client_ip
from oauth_handlers import get_oauth_handler
from security import SecurityUtils
from config import settings

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Auto Job Apply - Authentication Service",
    description="Authentication and authorization microservice",
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


@app.post("/register", response_model=TokenResponse)
async def register(
    user_data: UserRegister,
    request: Request,
    db: Session = Depends(get_db)
):
    """Register new user with email and password"""
    # Check if user already exists
    existing_user = AuthUtils.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user = await AuthUtils.create_user(
        db=db,
        email=user_data.email,
        password=user_data.password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone
    )
    
    # Log audit event
    AuthUtils.log_audit(db, AuditLogCreate(
        user_id=str(user.id),
        action="user_register",
        resource="user",
        details={"email": user.email},
        ip_address=get_client_ip(request),
        user_agent=request.headers.get("User-Agent")
    ))
    
    # Generate tokens
    access_token = SecurityUtils.create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role}
    )
    refresh_token = SecurityUtils.create_refresh_token(
        data={"sub": str(user.id), "email": user.email}
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.jwt_access_token_expire_minutes * 60,
        user=UserResponse.from_orm(user)
    )


@app.post("/login", response_model=TokenResponse)
async def login(
    user_credentials: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """Login with email and password"""
    ip_address = get_client_ip(request)
    
    user = await AuthUtils.authenticate_user(
        db=db,
        email=user_credentials.email,
        password=user_credentials.password,
        ip_address=ip_address
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Log audit event
    AuthUtils.log_audit(db, AuditLogCreate(
        user_id=str(user.id),
        action="user_login",
        resource="user",
        details={"method": "email_password"},
        ip_address=ip_address,
        user_agent=request.headers.get("User-Agent")
    ))
    
    # Generate tokens
    access_token = SecurityUtils.create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role}
    )
    refresh_token = SecurityUtils.create_refresh_token(
        data={"sub": str(user.id), "email": user.email}
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.jwt_access_token_expire_minutes * 60,
        user=UserResponse.from_orm(user)
    )


@app.post("/oauth/login", response_model=TokenResponse)
async def oauth_login(
    oauth_data: OAuthLoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Login with OAuth provider (Google, Microsoft, Apple)"""
    try:
        # Get OAuth handler
        oauth_handler = get_oauth_handler(oauth_data.provider.value)
        
        # Exchange code for token
        token_data = await oauth_handler.exchange_code_for_token(
            oauth_data.authorization_code,
            oauth_data.redirect_uri
        )
        
        # Get user info
        user_info = await oauth_handler.get_user_info(token_data["access_token"])
        
        if not user_info.get("email"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not provided by OAuth provider"
            )
        
        # Check if user exists
        user = AuthUtils.get_user_by_email(db, user_info["email"])
        
        if not user:
            # Create new user
            user = await AuthUtils.create_user(
                db=db,
                email=user_info["email"],
                first_name=user_info.get("first_name"),
                last_name=user_info.get("last_name")
            )
        
        # Store/update OAuth provider info
        oauth_provider = db.query(OAuthProvider).filter(
            OAuthProvider.user_id == user.id,
            OAuthProvider.provider == oauth_data.provider.value
        ).first()
        
        if oauth_provider:
            # Update existing
            oauth_provider.access_token = SecurityUtils.encrypt_data(token_data["access_token"])
            oauth_provider.refresh_token = SecurityUtils.encrypt_data(token_data.get("refresh_token", ""))
            oauth_provider.token_expires_at = datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 3600))
        else:
            # Create new
            oauth_provider = OAuthProvider(
                user_id=user.id,
                provider=oauth_data.provider.value,
                provider_user_id=user_info["provider_user_id"],
                access_token=SecurityUtils.encrypt_data(token_data["access_token"]),
                refresh_token=SecurityUtils.encrypt_data(token_data.get("refresh_token", "")),
                token_expires_at=datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 3600))
            )
            db.add(oauth_provider)
        
        db.commit()
        
        # Log audit event
        AuthUtils.log_audit(db, AuditLogCreate(
            user_id=str(user.id),
            action="oauth_login",
            resource="user",
            details={"provider": oauth_data.provider.value},
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("User-Agent")
        ))
        
        # Generate tokens
        access_token = SecurityUtils.create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role}
        )
        refresh_token = SecurityUtils.create_refresh_token(
            data={"sub": str(user.id), "email": user.email}
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.jwt_access_token_expire_minutes * 60,
            user=UserResponse.from_orm(user)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth login failed: {str(e)}"
        )


@app.post("/otp/request", response_model=OTPResponse)
async def request_otp(
    otp_request: EmailOTPRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Request OTP for email login"""
    # Generate OTP
    otp_code = AuthUtils.create_otp(db, otp_request.email)
    
    # Send OTP via email
    email_sent = await AuthUtils.send_otp_email(otp_request.email, otp_code)
    
    if not email_sent:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP email"
        )
    
    # Log audit event
    AuthUtils.log_audit(db, AuditLogCreate(
        action="otp_request",
        resource="otp",
        details={"email": otp_request.email},
        ip_address=get_client_ip(request),
        user_agent=request.headers.get("User-Agent")
    ))
    
    return OTPResponse(
        message="OTP sent to your email",
        expires_in=settings.otp_expire_minutes * 60
    )


@app.post("/otp/verify", response_model=TokenResponse)
async def verify_otp(
    otp_verify: EmailOTPVerify,
    request: Request,
    db: Session = Depends(get_db)
):
    """Verify OTP and login user"""
    # Verify OTP
    if not AuthUtils.verify_otp(db, otp_verify.email, otp_verify.otp_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )

    # Get or create user
    user = AuthUtils.get_user_by_email(db, otp_verify.email)
    if not user:
        # Create new user for OTP login
        user = await AuthUtils.create_user(
            db=db,
            email=otp_verify.email
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )

    # Log audit event
    AuthUtils.log_audit(db, AuditLogCreate(
        user_id=str(user.id),
        action="otp_login",
        resource="user",
        details={"email": user.email},
        ip_address=get_client_ip(request),
        user_agent=request.headers.get("User-Agent")
    ))

    # Generate tokens
    access_token = SecurityUtils.create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role}
    )
    refresh_token = SecurityUtils.create_refresh_token(
        data={"sub": str(user.id), "email": user.email}
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.jwt_access_token_expire_minutes * 60,
        user=UserResponse.from_orm(user)
    )


@app.post("/token/refresh", response_model=TokenResponse)
async def refresh_token(
    token_data: TokenRefresh,
    request: Request,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    payload = SecurityUtils.verify_token(token_data.refresh_token, "refresh")

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    user_id = payload.get("sub")
    user = AuthUtils.get_user_by_id(db, user_id)

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or deactivated"
        )

    # Generate new tokens
    access_token = SecurityUtils.create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role}
    )
    new_refresh_token = SecurityUtils.create_refresh_token(
        data={"sub": str(user.id), "email": user.email}
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.jwt_access_token_expire_minutes * 60,
        user=UserResponse.from_orm(user)
    )


@app.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse.from_orm(current_user)


@app.post("/logout", response_model=MessageResponse)
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout user (invalidate tokens - client-side implementation)"""
    # Log audit event
    AuthUtils.log_audit(db, AuditLogCreate(
        user_id=str(current_user.id),
        action="user_logout",
        resource="user",
        details={"email": current_user.email},
        ip_address=get_client_ip(request),
        user_agent=request.headers.get("User-Agent")
    ))

    return MessageResponse(message="Successfully logged out")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "auth", "timestamp": datetime.utcnow()}


# Admin endpoints
@app.get("/admin/users", response_model=list[UserResponse])
async def get_all_users(
    current_user: User = Depends(require_role("super_admin")),
    db: Session = Depends(get_db)
):
    """Get all users (Super Admin only)"""
    users = db.query(User).all()
    return [UserResponse.from_orm(user) for user in users]


@app.put("/admin/users/{user_id}/status")
async def update_user_status(
    user_id: str,
    is_active: bool,
    current_user: User = Depends(require_role("super_admin")),
    db: Session = Depends(get_db)
):
    """Activate/deactivate user (Super Admin only)"""
    user = AuthUtils.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_active = is_active
    db.commit()

    return MessageResponse(
        message=f"User {'activated' if is_active else 'deactivated'} successfully"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
