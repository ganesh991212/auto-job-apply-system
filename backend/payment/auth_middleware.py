import httpx
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer
from typing import Dict, Any
from config import settings

security = HTTPBearer()


async def get_current_user(credentials = Depends(security)) -> Dict[str, Any]:
    """Get current user from auth service"""
    token = credentials.credentials
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.auth_service_url}/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                user_data = response.json()
                return {
                    "user_id": user_data["id"],
                    "email": user_data["email"],
                    "role": user_data["role"],
                    "is_active": user_data["is_active"]
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication token"
                )
                
        except httpx.RequestError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service unavailable"
            )


def require_role(required_role: str):
    """Require specific user role"""
    async def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        if current_user["role"] != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker
