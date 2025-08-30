from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
from authlib.integrations.requests_client import OAuth2Session
import asyncpg
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from models import User, OAuthProvider, LoginAttempt, OTPCode, AuditLog
from schemas import TokenData, AuditLogCreate
from security import SecurityUtils
from config import settings
from database import get_db

security = HTTPBearer()


class AuthUtils:
    @staticmethod
    async def create_user(db: Session, email: str, password: Optional[str] = None, 
                         first_name: Optional[str] = None, last_name: Optional[str] = None,
                         phone: Optional[str] = None, role: str = "candidate") -> User:
        """Create a new user"""
        password_hash = SecurityUtils.hash_password(password) if password else None
        
        user = User(
            email=email,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            role=role
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    async def authenticate_user(db: Session, email: str, password: str, 
                               ip_address: str) -> Optional[User]:
        """Authenticate user with email and password"""
        # Check for too many failed attempts
        recent_attempts = db.query(LoginAttempt).filter(
            LoginAttempt.email == email,
            LoginAttempt.success == False,
            LoginAttempt.created_at > datetime.utcnow() - timedelta(minutes=settings.lockout_duration_minutes)
        ).count()
        
        if recent_attempts >= settings.max_login_attempts:
            # Log the attempt
            AuthUtils.log_login_attempt(db, email, ip_address, False, "Account locked due to too many failed attempts")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Account temporarily locked due to too many failed login attempts"
            )
        
        user = AuthUtils.get_user_by_email(db, email)
        if not user or not user.password_hash:
            AuthUtils.log_login_attempt(db, email, ip_address, False, "User not found or no password set")
            return None
        
        if not SecurityUtils.verify_password(password, user.password_hash):
            AuthUtils.log_login_attempt(db, email, ip_address, False, "Invalid password")
            return None
        
        if not user.is_active:
            AuthUtils.log_login_attempt(db, email, ip_address, False, "Account deactivated")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated"
            )
        
        # Successful login
        AuthUtils.log_login_attempt(db, email, ip_address, True, "Successful login")
        return user
    
    @staticmethod
    def log_login_attempt(db: Session, email: str, ip_address: str, 
                         success: bool, failure_reason: Optional[str] = None):
        """Log login attempt"""
        attempt = LoginAttempt(
            email=email,
            ip_address=ip_address,
            success=success,
            failure_reason=failure_reason
        )
        db.add(attempt)
        db.commit()
    
    @staticmethod
    async def send_otp_email(email: str, otp_code: str) -> bool:
        """Send OTP via email"""
        try:
            msg = MimeMultipart()
            msg['From'] = settings.smtp_username
            msg['To'] = email
            msg['Subject'] = "Auto Job Apply - Login OTP"
            
            body = f"""
            Your OTP for Auto Job Apply login is: {otp_code}
            
            This code will expire in {settings.otp_expire_minutes} minutes.
            
            If you didn't request this code, please ignore this email.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(settings.smtp_server, settings.smtp_port)
            server.starttls()
            server.login(settings.smtp_username, settings.smtp_password)
            text = msg.as_string()
            server.sendmail(settings.smtp_username, email, text)
            server.quit()
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
    
    @staticmethod
    def create_otp(db: Session, email: str) -> str:
        """Create and store OTP for email"""
        # Invalidate existing OTPs for this email
        db.query(OTPCode).filter(OTPCode.email == email).update({"used": True})
        
        otp_code = SecurityUtils.generate_otp()
        expires_at = datetime.utcnow() + timedelta(minutes=settings.otp_expire_minutes)
        
        otp = OTPCode(
            email=email,
            code=otp_code,
            expires_at=expires_at
        )
        
        db.add(otp)
        db.commit()
        return otp_code
    
    @staticmethod
    def verify_otp(db: Session, email: str, otp_code: str) -> bool:
        """Verify OTP code"""
        otp = db.query(OTPCode).filter(
            OTPCode.email == email,
            OTPCode.code == otp_code,
            OTPCode.used == False,
            OTPCode.expires_at > datetime.utcnow()
        ).first()
        
        if otp:
            otp.used = True
            db.commit()
            return True
        return False
    
    @staticmethod
    def log_audit(db: Session, audit_data: AuditLogCreate):
        """Log audit event"""
        audit_log = AuditLog(**audit_data.dict())
        db.add(audit_log)
        db.commit()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security),
                          db: Session = Depends(get_db)) -> User:
    """Get current authenticated user from JWT token"""
    token = credentials.credentials
    payload = SecurityUtils.verify_token(token, "access")
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = AuthUtils.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
    
    return user


def require_role(required_role: str):
    """Decorator to require specific role"""
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker


def get_client_ip(request: Request) -> str:
    """Get client IP address from request"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"
