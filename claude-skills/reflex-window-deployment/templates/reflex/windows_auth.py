# middleware/windows_auth.py
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class WindowsAuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract Windows-authenticated user from X-Remote-User header.
    Only trust this header when running behind IIS with Windows Auth enabled.
    """
    
    def __init__(self, app, trusted_proxies: list = None):
        super().__init__(app)
        self.trusted_proxies = trusted_proxies or ["127.0.0.1", "::1"]
    
    async def dispatch(self, request: Request, call_next):
        # Only trust header from known proxy IPs
        client_ip = request.client.host if request.client else None
        
        if client_ip in self.trusted_proxies:
            # Extract authenticated user
            remote_user = request.headers.get("X-Remote-User", "")
            
            if remote_user:
                # Parse DOMAIN\username format
                if "\\" in remote_user:
                    domain, username = remote_user.split("\\", 1)
                elif "@" in remote_user:
                    username, domain = remote_user.split("@", 1)
                else:
                    username = remote_user
                    domain = ""
                
                # Store in request state for access in route handlers
                request.state.auth_user = username
                request.state.auth_domain = domain
                request.state.auth_full = remote_user
        
        return await call_next(request)

# Usage in Reflex app
# In your main app file:
# app.add_middleware(WindowsAuthMiddleware, trusted_proxies=["127.0.0.1"])
