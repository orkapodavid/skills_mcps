# auth/entra_oidc.py
"""
Microsoft Entra ID (Azure AD) OIDC Authentication for FastAPI/Reflex
Requires: pip install msal pyjwt[crypto] httpx
"""

import os
import secrets
import hashlib
import base64
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

import jwt
import msal
from jwt import PyJWKClient
from fastapi import HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware

class EntraOIDCConfig:
    """Configuration for Entra ID OIDC."""
    
    def __init__(self):
        self.client_id = os.getenv("ENTRA_CLIENT_ID")
        self.client_secret = os.getenv("ENTRA_CLIENT_SECRET")
        self.tenant_id = os.getenv("ENTRA_TENANT_ID")
        self.redirect_uri = os.getenv("ENTRA_REDIRECT_URI", "https://myapp.corp.com/oauth2/callback")
        
        if not all([self.client_id, self.client_secret, self.tenant_id]):
            raise ValueError("Missing Entra ID configuration. Set ENTRA_CLIENT_ID, ENTRA_CLIENT_SECRET, ENTRA_TENANT_ID")
        
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.issuer = f"https://login.microsoftonline.com/{self.tenant_id}/v2.0"
        self.jwks_url = f"https://login.microsoftonline.com/{self.tenant_id}/discovery/v2.0/keys"
        self.scopes = ["User.Read", "openid", "profile", "email"]


class EntraOIDCHandler:
    """Handles Entra ID OAuth2/OIDC authentication."""
    
    def __init__(self, config: EntraOIDCConfig):
        self.config = config
        self.jwks_client = PyJWKClient(config.jwks_url)
        self.msal_app = msal.ConfidentialClientApplication(
            client_id=config.client_id,
            client_credential=config.client_secret,
            authority=config.authority,
        )
    
    def generate_pkce(self) -> tuple[str, str]:
        """Generate PKCE code_verifier and code_challenge."""
        code_verifier = secrets.token_urlsafe(32)
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode().rstrip("=")
        return code_verifier, code_challenge
    
    def initiate_login(self, request: Request) -> RedirectResponse:
        """Start OAuth2 login flow."""
        state = secrets.token_urlsafe(32)
        code_verifier, code_challenge = self.generate_pkce()
        
        # Store in session
        request.session["oauth_state"] = state
        request.session["code_verifier"] = code_verifier
        request.session["return_to"] = str(request.url)
        
        # Build authorization URL
        flow = self.msal_app.initiate_auth_code_flow(
            scopes=self.config.scopes,
            redirect_uri=self.config.redirect_uri,
            state=state,
        )
        request.session["auth_flow"] = flow
        
        return RedirectResponse(url=flow["auth_uri"])
    
    async def handle_callback(self, request: Request) -> Dict[str, Any]:
        """Handle OAuth2 callback and exchange code for tokens."""
        # Validate state (CSRF protection)
        state = request.query_params.get("state")
        stored_state = request.session.get("oauth_state")
        
        if not state or state != stored_state:
            raise HTTPException(status_code=400, detail="Invalid state parameter")
        
        # Get auth flow from session
        flow = request.session.get("auth_flow")
        if not flow:
            raise HTTPException(status_code=400, detail="No auth flow in session")
        
        # Exchange code for tokens
        result = self.msal_app.acquire_token_by_auth_code_flow(
            flow, dict(request.query_params)
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=400,
                detail=result.get("error_description", "Authentication failed")
            )
        
        # Validate ID token
        id_token = result.get("id_token")
        claims = self.validate_token(id_token)
        
        # Store user info in session
        request.session["user"] = {
            "id": claims.get("oid"),
            "name": claims.get("name"),
            "email": claims.get("preferred_username"),
            "groups": claims.get("groups", []),
        }
        request.session["access_token"] = result.get("access_token")
        
        # Cleanup
        for key in ["oauth_state", "code_verifier", "auth_flow"]:
            request.session.pop(key, None)
        
        return request.session["user"]
    
    def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate JWT token using JWKS."""
        try:
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)
            claims = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=self.config.client_id,
                issuer=self.config.issuer,
            )
            return claims
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
    
    def logout(self, request: Request) -> RedirectResponse:
        """Handle logout."""
        request.session.clear()
        logout_url = (
            f"https://login.microsoftonline.com/{self.config.tenant_id}/oauth2/v2.0/logout"
            f"?post_logout_redirect_uri={self.config.redirect_uri.rsplit('/', 1)[0]}"
        )
        return RedirectResponse(url=logout_url)


# Session cookie security settings
SESSION_CONFIG = {
    "secret_key": os.getenv("SESSION_SECRET", secrets.token_urlsafe(32)),
    "session_cookie": "session",
    "max_age": 3600,  # 1 hour
    "same_site": "lax",  # Required for OAuth redirects
    "https_only": True,  # ALWAYS True in production
}
