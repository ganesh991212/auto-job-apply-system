import httpx
from typing import Dict, Any, Optional
from fastapi import HTTPException, status
from authlib.integrations.requests_client import OAuth2Session
from config import settings
from security import SecurityUtils


class OAuthHandler:
    """Base OAuth handler class"""
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from OAuth provider"""
        raise NotImplementedError
    
    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        raise NotImplementedError


class GoogleOAuthHandler(OAuthHandler):
    """Google OAuth2 handler"""
    
    def __init__(self):
        super().__init__(settings.google_client_id, settings.google_client_secret)
        self.token_url = "https://oauth2.googleapis.com/token"
        self.user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    
    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchange Google authorization code for access token"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": redirect_uri,
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange code for token"
                )
            
            return response.json()
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get Google user information"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.user_info_url,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to get user info from Google"
                )
            
            user_data = response.json()
            return {
                "email": user_data.get("email"),
                "first_name": user_data.get("given_name"),
                "last_name": user_data.get("family_name"),
                "provider_user_id": user_data.get("id"),
                "picture": user_data.get("picture")
            }


class MicrosoftOAuthHandler(OAuthHandler):
    """Microsoft OAuth2 handler"""
    
    def __init__(self):
        super().__init__(settings.microsoft_client_id, settings.microsoft_client_secret)
        self.token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
        self.user_info_url = "https://graph.microsoft.com/v1.0/me"
    
    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchange Microsoft authorization code for access token"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": redirect_uri,
                    "scope": "User.Read"
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange code for token"
                )
            
            return response.json()
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get Microsoft user information"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.user_info_url,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to get user info from Microsoft"
                )
            
            user_data = response.json()
            return {
                "email": user_data.get("mail") or user_data.get("userPrincipalName"),
                "first_name": user_data.get("givenName"),
                "last_name": user_data.get("surname"),
                "provider_user_id": user_data.get("id")
            }


class AppleOAuthHandler(OAuthHandler):
    """Apple OAuth2 handler (simplified implementation)"""
    
    def __init__(self):
        super().__init__(settings.apple_client_id, settings.apple_client_secret)
        self.token_url = "https://appleid.apple.com/auth/token"
    
    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchange Apple authorization code for access token"""
        # Apple OAuth requires JWT client assertion - simplified for demo
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": redirect_uri,
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange code for token"
                )
            
            return response.json()
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get Apple user information (limited due to Apple's privacy model)"""
        # Apple provides limited user info, typically just email
        # In real implementation, user info comes with the initial token response
        return {
            "email": None,  # Would be provided in the token response
            "first_name": None,
            "last_name": None,
            "provider_user_id": None
        }


def get_oauth_handler(provider: str) -> OAuthHandler:
    """Get OAuth handler for specific provider"""
    handlers = {
        "google": GoogleOAuthHandler,
        "microsoft": MicrosoftOAuthHandler,
        "apple": AppleOAuthHandler
    }
    
    handler_class = handlers.get(provider)
    if not handler_class:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported OAuth provider: {provider}"
        )
    
    return handler_class()
