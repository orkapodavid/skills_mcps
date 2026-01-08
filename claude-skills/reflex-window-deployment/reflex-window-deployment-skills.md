# Reflex Windows Deployment Skill Folder

**Bottom Line Up Front:** This production-ready skill folder enables developers to deploy Reflex (Python) full-stack applications on Windows Server 2016/2019/2022 using WinSW or NSSM service wrappers behind IIS reverse proxy with enterprise authentication. The two-phase authentication approach supports air-gapped intranets (Windows Auth/Kerberos) and cloud-connected environments (Microsoft Entra ID/OIDC) with copy-paste configurations, validated templates, and comprehensive troubleshooting guidance.

---

## SKILL.md — Master Overview and Quick Start

### Decision Tree: Choosing Your Deployment Path

```mermaid
flowchart TD
    A[Start: Deploy Reflex on Windows] --> B{Internet Available?}
    B -->|No - Air-Gapped| C[Phase 1: Windows Authentication]
    B -->|Yes - Cloud Connected| D{MFA Required?}
    D -->|Yes| E[Phase 2: Entra ID OIDC]
    D -->|No - Intranet Only| C
    C --> F{Service Wrapper Preference?}
    E --> F
    F -->|XML Config| G[WinSW]
    F -->|CLI/GUI| H[NSSM]
    G --> I[Configure IIS Reverse Proxy]
    H --> I
    I --> J{Multi-App?}
    J -->|Yes - Subdomains| K[app1.corp.com Pattern]
    J -->|Yes - Subpaths| L[corp.com/app1 Pattern]
    J -->|No - Single App| M[Direct Proxy]
    K --> N[Deploy & Validate]
    L --> N
    M --> N
```

### Quick Start Checklist

| Step | Action | Time |
|------|--------|------|
| 1 | Install Python 3.11+ and create venv | 5 min |
| 2 | Install Reflex: `pip install reflex` | 2 min |
| 3 | Build app: `reflex run --env prod` | 3 min |
| 4 | Install WinSW/NSSM service wrapper | 5 min |
| 5 | Configure IIS with ARR + URL Rewrite | 15 min |
| 6 | Enable Windows Auth OR configure Entra ID | 20 min |
| 7 | Validate with deployment checklist | 10 min |

### Architecture Pattern: Reverse Proxy with Service Wrapper

```mermaid
flowchart LR
    subgraph Internet/Intranet
        Client[Browser Client]
    end
    
    subgraph IIS["IIS (Port 443)"]
        SSL[SSL Termination]
        ARR[ARR Proxy]
        Auth[Win Auth / Entra]
    end
    
    subgraph Services["Windows Services"]
        WS1[Reflex App 1<br/>Port 3000]
        WS2[Reflex App 2<br/>Port 3001]
    end
    
    Client -->|HTTPS| SSL
    SSL --> Auth
    Auth --> ARR
    ARR -->|HTTP localhost| WS1
    ARR -->|HTTP localhost| WS2
```

---

## Core Documentation (10 Files)

### 1. reflex-application-preparation.md

#### rxconfig.py Production Configuration

```python
# rxconfig.py - Production configuration for Windows deployment
import reflex as rx
import os

# Environment-aware configuration
ENV = os.getenv("REFLEX_ENV", "production")

config = rx.Config(
    app_name="myapp",
    
    # === Server Configuration ===
    frontend_port=int(os.getenv("FRONTEND_PORT", 3000)),
    backend_port=int(os.getenv("BACKEND_PORT", 8000)),
    backend_host="127.0.0.1",  # Bind to localhost only (IIS proxies)
    
    # === CRITICAL: URLs for reverse proxy ===
    # api_url must be the PUBLIC URL users access
    api_url=os.getenv("API_URL", "https://myapp.corp.com"),
    deploy_url=os.getenv("DEPLOY_URL", "https://myapp.corp.com"),
    
    # === Sub-path deployment (corp.com/myapp) ===
    frontend_path=os.getenv("FRONTEND_PATH", ""),  # Set to "/myapp" for sub-path
    
    # === Database ===
    db_url=os.getenv("DATABASE_URL", "sqlite:///reflex.db"),
    
    # === Production State Management ===
    # Use Redis for multi-worker deployments
    redis_url=os.getenv("REDIS_URL", None),
    
    # === CORS (restrict in production) ===
    cors_allowed_origins=[
        "https://myapp.corp.com",
        "https://*.corp.com",
    ],
    
    # === Environment file ===
    env_file=".env.prod" if ENV == "production" else ".env",
)
```

#### Build Commands for Production

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Set production environment
$env:REFLEX_ENV = "production"
$env:API_URL = "https://myapp.corp.com"

# Option 1: Run both frontend and backend
reflex run --env prod

# Option 2: Run backend only (frontend served separately)
reflex run --env prod --backend-only --backend-port 8000

# Option 3: Export static frontend for CDN/static hosting
reflex export --frontend-only --no-zip
# Output: .web/_static/
```

#### WebSocket Endpoints (Critical for IIS)

| Endpoint | Purpose | Protocol |
|----------|---------|----------|
| `/_event/` | Real-time state sync | WebSocket |
| `/ping` | Health check | HTTP GET |
| `/_upload` | File uploads | HTTP POST |
| `/*` | Frontend routes | HTTP |

---

### 2. windows-service-management.md

#### WinSW Configuration (winsw.xml)

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- 
  WinSW Configuration for Reflex Application
  Place alongside WinSW.exe (renamed to match app name)
  Download: https://github.com/winsw/winsw/releases/download/v2.12.0/WinSW.NET461.exe
-->
<service>
  <!-- === Service Identity === -->
  <id>ReflexApp</id>
  <name>Reflex Application Service</name>
  <description>Reflex full-stack Python application running on Uvicorn</description>
  
  <!-- === Executable Configuration === -->
  <executable>%BASE%\.venv\Scripts\python.exe</executable>
  <arguments>-m reflex run --env prod --backend-only --backend-port 8000</arguments>
  <workingdirectory>%BASE%</workingdirectory>
  
  <!-- === Environment Variables === -->
  <env name="REFLEX_ENV" value="production"/>
  <env name="API_URL" value="https://myapp.corp.com"/>
  <env name="DATABASE_URL" value="postgresql://user:pass@dbserver/myapp"/>
  <env name="PYTHONUNBUFFERED" value="1"/>
  
  <!-- === Logging with Rotation === -->
  <logpath>%BASE%\logs</logpath>
  <log mode="roll-by-size">
    <sizeThreshold>10240</sizeThreshold>  <!-- 10MB -->
    <keepFiles>10</keepFiles>
  </log>
  
  <!-- === Service Startup === -->
  <startmode>Automatic</startmode>
  <delayedAutoStart>true</delayedAutoStart>
  
  <!-- === Dependencies (wait for network) === -->
  <depend>Tcpip</depend>
  <depend>Dnscache</depend>
  
  <!-- === Recovery on Failure === -->
  <onfailure action="restart" delay="10 sec"/>
  <onfailure action="restart" delay="30 sec"/>
  <onfailure action="restart" delay="60 sec"/>
  <resetfailure>1 hour</resetfailure>
  
  <!-- === Graceful Shutdown === -->
  <stoptimeout>30 sec</stoptimeout>
  <stopparentprocessfirst>true</stopparentprocessfirst>
  
  <!-- === Security (run as service account) === -->
  <serviceaccount>
    <user>NetworkService</user>
  </serviceaccount>
</service>
```

#### WinSW Installation Commands

```powershell
# Rename WinSW executable to match your app
Rename-Item WinSW.NET461.exe ReflexApp.exe

# Install service
.\ReflexApp.exe install

# Start service
.\ReflexApp.exe start

# Check status
.\ReflexApp.exe status

# View logs
Get-Content .\logs\ReflexApp.out.log -Tail 50 -Wait
```

#### NSSM Installation Script (install-service.ps1)

```powershell
# install-reflex-service.ps1
# NSSM-based service installation for Reflex applications

param(
    [Parameter(Mandatory=$true)]
    [string]$ServiceName,
    
    [Parameter(Mandatory=$true)]
    [string]$AppPath,
    
    [int]$Port = 8000,
    [string]$ApiUrl = "https://myapp.corp.com"
)

$ErrorActionPreference = "Stop"

# Paths
$VenvPython = Join-Path $AppPath ".venv\Scripts\python.exe"
$LogDir = Join-Path $AppPath "logs"
$NssmPath = "nssm.exe"  # Assumes in PATH

# Validate
if (-not (Test-Path $VenvPython)) {
    throw "Virtual environment not found at $VenvPython"
}

# Create log directory
New-Item -ItemType Directory -Path $LogDir -Force | Out-Null

Write-Host "Installing service: $ServiceName" -ForegroundColor Cyan

# Install service
& $NssmPath install $ServiceName $VenvPython "-m" "reflex" "run" "--env" "prod" "--backend-only" "--backend-port" "$Port"

# Application settings
& $NssmPath set $ServiceName AppDirectory $AppPath
& $NssmPath set $ServiceName DisplayName "Reflex App - $ServiceName"
& $NssmPath set $ServiceName Description "Reflex Python application on port $Port"

# Environment variables
& $NssmPath set $ServiceName AppEnvironmentExtra `
    "REFLEX_ENV=production" `
    "API_URL=$ApiUrl" `
    "BACKEND_PORT=$Port" `
    "PYTHONUNBUFFERED=1"

# Logging with rotation
& $NssmPath set $ServiceName AppStdout "$LogDir\stdout.log"
& $NssmPath set $ServiceName AppStderr "$LogDir\stderr.log"
& $NssmPath set $ServiceName AppStdoutCreationDisposition 4
& $NssmPath set $ServiceName AppStderrCreationDisposition 4
& $NssmPath set $ServiceName AppRotateFiles 1
& $NssmPath set $ServiceName AppRotateOnline 1
& $NssmPath set $ServiceName AppRotateBytes 10485760  # 10MB

# Restart behavior
& $NssmPath set $ServiceName AppExit Default Restart
& $NssmPath set $ServiceName AppRestartDelay 5000

# Graceful shutdown (Python needs time)
& $NssmPath set $ServiceName AppStopMethodConsole 15000
& $NssmPath set $ServiceName AppStopMethodWindow 15000
& $NssmPath set $ServiceName AppStopMethodThreads 15000

# Auto-start
& $NssmPath set $ServiceName Start SERVICE_AUTO_START

# Windows-level recovery
sc.exe failure $ServiceName reset= 86400 actions= restart/60000/restart/60000/restart/60000

Write-Host "Service installed successfully!" -ForegroundColor Green
Write-Host "Start with: nssm start $ServiceName" -ForegroundColor Yellow
```

---

### 3. iis-reverse-proxy-setup.md

#### Prerequisites Installation

```powershell
# Install IIS features (run as Administrator)
Install-WindowsFeature -Name Web-Server, Web-WebSockets, Web-Windows-Auth -IncludeManagementTools

# Install URL Rewrite (online)
# Download: https://download.microsoft.com/download/1/2/8/128E2E22-C1B9-44A4-BE2A-5859ED1D4592/rewrite_amd64_en-US.msi
msiexec /i rewrite_amd64_en-US.msi /qn

# Install ARR 3.0 (online)
# Download: https://go.microsoft.com/fwlink/?LinkID=615136
.\requestRouter_amd64.msi /quiet

# Enable proxy at server level
C:\Windows\System32\inetsrv\appcmd.exe set config -section:system.webServer/proxy /enabled:true /commit:apphost

# CRITICAL: Set timeout for WebSocket connections (5 minutes)
C:\Windows\System32\inetsrv\appcmd.exe set config -section:system.webServer/proxy /timeout:"00:05:00" /commit:apphost

# Disable response buffering for WebSocket
C:\Windows\System32\inetsrv\appcmd.exe set config -section:system.webServer/proxy /responseBufferLimit:0 /commit:apphost

# Preserve host header
C:\Windows\System32\inetsrv\appcmd.exe set config -section:system.webServer/proxy /preserveHostHeader:true /commit:apphost
```

#### web.config — Single App with WebSocket Support

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!--
  IIS web.config for Reflex reverse proxy
  Place in IIS site root (e.g., C:\inetpub\myapp\web.config)
-->
<configuration>
  <system.webServer>
    <!-- Enable WebSocket protocol (CRITICAL for Reflex) -->
    <webSocket enabled="true" />
    
    <!-- URL Rewrite Rules -->
    <rewrite>
      <!-- Whitelist server variables for header injection -->
      <allowedServerVariables>
        <add name="HTTP_X_FORWARDED_FOR" />
        <add name="HTTP_X_FORWARDED_PROTO" />
        <add name="HTTP_X_ORIGINAL_URL" />
      </allowedServerVariables>
      
      <rules>
        <!-- Force HTTPS -->
        <rule name="HTTPS Redirect" stopProcessing="true">
          <match url="(.*)" />
          <conditions>
            <add input="{HTTPS}" pattern="^OFF$" />
          </conditions>
          <action type="Redirect" url="https://{HTTP_HOST}/{R:1}" redirectType="Permanent" />
        </rule>
        
        <!-- Proxy all requests to Reflex backend -->
        <rule name="Reflex Proxy" stopProcessing="true">
          <match url="(.*)" />
          <serverVariables>
            <set name="HTTP_X_FORWARDED_PROTO" value="{REQUEST_SCHEME}" />
            <set name="HTTP_X_FORWARDED_FOR" value="{REMOTE_ADDR}" />
          </serverVariables>
          <action type="Rewrite" url="http://127.0.0.1:3000/{R:1}" />
        </rule>
      </rules>
    </rewrite>
    
    <!-- Error handling -->
    <httpErrors existingResponse="PassThrough" />
  </system.webServer>
</configuration>
```

---

### 4. windows-authentication-phase1.md

#### IIS Windows Authentication Setup

```powershell
# Install Windows Authentication feature
Install-WindowsFeature Web-Windows-Auth

# Enable Windows Auth, disable Anonymous (via appcmd)
$siteName = "MyReflexApp"
C:\Windows\System32\inetsrv\appcmd.exe set config "$siteName" /section:anonymousAuthentication /enabled:false
C:\Windows\System32\inetsrv\appcmd.exe set config "$siteName" /section:windowsAuthentication /enabled:true
```

#### web.config — Windows Authentication with Header Injection

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!--
  IIS web.config for Reflex with Windows Authentication (Phase 1)
  Passes authenticated username to backend via X-Remote-User header
-->
<configuration>
  <system.webServer>
    <webSocket enabled="true" />
    
    <!-- Windows Authentication -->
    <security>
      <authentication>
        <anonymousAuthentication enabled="false" />
        <windowsAuthentication enabled="true" useKernelMode="true">
          <providers>
            <clear />
            <add value="Negotiate" />
            <add value="NTLM" />
          </providers>
        </windowsAuthentication>
      </authentication>
    </security>
    
    <rewrite>
      <!-- CRITICAL: Whitelist variables for distributed rules -->
      <allowedServerVariables>
        <add name="HTTP_X_REMOTE_USER" />
        <add name="HTTP_X_FORWARDED_FOR" />
        <add name="HTTP_X_FORWARDED_PROTO" />
      </allowedServerVariables>
      
      <rules>
        <!-- HTTPS Redirect -->
        <rule name="HTTPS Redirect" stopProcessing="true">
          <match url="(.*)" />
          <conditions>
            <add input="{HTTPS}" pattern="^OFF$" />
          </conditions>
          <action type="Redirect" url="https://{HTTP_HOST}/{R:1}" />
        </rule>
        
        <!-- Inject authenticated user into header -->
        <rule name="Reflex Proxy with Auth" stopProcessing="true">
          <match url="(.*)" />
          <conditions>
            <add input="{LOGON_USER}" pattern=".+" />
          </conditions>
          <serverVariables>
            <!-- DOMAIN\username or username@domain.com -->
            <set name="HTTP_X_REMOTE_USER" value="{LOGON_USER}" />
            <set name="HTTP_X_FORWARDED_PROTO" value="{REQUEST_SCHEME}" />
            <set name="HTTP_X_FORWARDED_FOR" value="{REMOTE_ADDR}" />
          </serverVariables>
          <action type="Rewrite" url="http://127.0.0.1:3000/{R:1}" />
        </rule>
      </rules>
    </rewrite>
    
    <httpErrors existingResponse="PassThrough" />
  </system.webServer>
</configuration>
```

#### Python Middleware for Reading X-Remote-User

```python
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
```

#### SPN Configuration for Kerberos

```powershell
# Register SPNs for the IIS service account
# Replace DOMAIN\svc_iis with your service account

# For hostname access
setspn -S HTTP/myapp DOMAIN\svc_iis
setspn -S HTTP/myapp.corp.com DOMAIN\svc_iis

# Verify SPNs
setspn -L DOMAIN\svc_iis

# Check for duplicates (CRITICAL - duplicates break Kerberos)
setspn -X
```

#### Troubleshooting 401 Loops Decision Tree

```mermaid
flowchart TD
    A[401 Authentication Error] --> B{Check IIS Log sc-substatus}
    B -->|401.1| C[Credentials rejected]
    B -->|401.2| D[Configuration issue]
    B -->|401.5| E[ISAPI/CGI issue]
    
    C --> C1{User account valid?}
    C1 -->|No| C2[Reset password / unlock account]
    C1 -->|Yes| C3{SPN configured?}
    C3 -->|No| C4[Run: setspn -S HTTP/hostname account]
    C3 -->|Yes| C5{Duplicate SPN?}
    C5 -->|Yes| C6[Remove duplicate with setspn -D]
    C5 -->|No| C7[Check Kerberos ticket: klist]
    
    D --> D1{Windows Auth enabled?}
    D1 -->|No| D2[Enable in IIS Manager]
    D1 -->|Yes| D3{Anonymous disabled?}
    D3 -->|No| D4[Disable Anonymous Auth]
    D3 -->|Yes| D5[Check authorization rules]
    
    C7 --> C8{Ticket present?}
    C8 -->|No| C9[Purge and retry: klist purge]
    C8 -->|Yes| C10[Check time sync with DC < 5 min]
```

---

### 5. ms-entra-authentication-phase2.md

#### Entra ID App Registration Checklist

| Step | Action | Value |
|------|--------|-------|
| 1 | App Name | `Reflex-MyApp-Prod` |
| 2 | Supported Accounts | Single tenant (your org only) |
| 3 | Redirect URI | `https://myapp.corp.com/oauth2/callback` |
| 4 | Client Secret | Generate and save securely |
| 5 | API Permissions | `User.Read`, `openid`, `profile`, `email` |
| 6 | Token Config | Add `groups` claim if needed |

#### OAuth2 Authorization Code Flow with PKCE

```mermaid
sequenceDiagram
    participant U as User Browser
    participant R as Reflex App
    participant E as Entra ID
    
    U->>R: Access /protected
    R->>R: Generate state + PKCE (code_verifier, code_challenge)
    R->>U: Redirect to Entra /authorize
    U->>E: Login request with code_challenge
    E->>U: Show login page
    U->>E: Enter credentials + MFA
    E->>U: Redirect to /oauth2/callback?code=xxx&state=xxx
    U->>R: Callback with auth code
    R->>R: Validate state (CSRF protection)
    R->>E: POST /token with code + code_verifier
    E->>R: Access token + ID token + Refresh token
    R->>R: Validate JWT signature via JWKS
    R->>U: Set session cookie, return protected content
```

#### FastAPI Entra ID Middleware

```python
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
```

---

### 6. multi-app-deployment-strategy.md

#### Port Allocation Strategy

| Application | Backend Port | Frontend Port | Service Name |
|-------------|--------------|---------------|--------------|
| App 1 | 8001 | 3001 | ReflexApp1 |
| App 2 | 8002 | 3002 | ReflexApp2 |
| App 3 | 8003 | 3003 | ReflexApp3 |

#### Sub-Domain Pattern (app1.corp.com)

```xml
<!-- web.config for sub-domain routing -->
<configuration>
  <system.webServer>
    <webSocket enabled="true" />
    <rewrite>
      <rules>
        <!-- Route app1.corp.com to port 3001 -->
        <rule name="App1 Subdomain" stopProcessing="true">
          <match url="(.*)" />
          <conditions>
            <add input="{HTTP_HOST}" pattern="^app1\.corp\.com$" />
          </conditions>
          <action type="Rewrite" url="http://127.0.0.1:3001/{R:1}" />
        </rule>
        
        <!-- Route app2.corp.com to port 3002 -->
        <rule name="App2 Subdomain" stopProcessing="true">
          <match url="(.*)" />
          <conditions>
            <add input="{HTTP_HOST}" pattern="^app2\.corp\.com$" />
          </conditions>
          <action type="Rewrite" url="http://127.0.0.1:3002/{R:1}" />
        </rule>
      </rules>
    </rewrite>
  </system.webServer>
</configuration>
```

#### Sub-Path Pattern (corp.com/app1)

```xml
<!-- web.config for sub-path routing -->
<configuration>
  <system.webServer>
    <webSocket enabled="true" />
    <rewrite>
      <rules>
        <!-- Route /app1/* to port 3001 -->
        <rule name="App1 Path" stopProcessing="true">
          <match url="^app1/(.*)" />
          <action type="Rewrite" url="http://127.0.0.1:3001/{R:1}" />
        </rule>
        
        <!-- Route /app2/* to port 3002 -->
        <rule name="App2 Path" stopProcessing="true">
          <match url="^app2/(.*)" />
          <action type="Rewrite" url="http://127.0.0.1:3002/{R:1}" />
        </rule>
      </rules>
    </rewrite>
  </system.webServer>
</configuration>
```

**CRITICAL:** When using sub-path pattern, set `frontend_path` in rxconfig.py:
```python
config = rx.Config(
    app_name="app1",
    frontend_path="/app1",
    api_url="https://corp.com/app1",
)
```

---

### 7. air-gapped-deployment-guide.md

#### Phase 1: Prepare on Connected Machine

```powershell
# prepare-offline-deployment.ps1
# Run on machine with internet access

param(
    [string]$OutputPath = "C:\OfflineDeployment",
    [string]$PythonVersion = "3.11.6"
)

# Create output structure
$dirs = @("wheelhouse", "installers", "tools", "iis-modules")
foreach ($dir in $dirs) {
    New-Item -ItemType Directory -Path "$OutputPath\$dir" -Force | Out-Null
}

# 1. Download embedded Python
$pythonUrl = "https://www.python.org/ftp/python/$PythonVersion/python-$PythonVersion-embed-amd64.zip"
Invoke-WebRequest -Uri $pythonUrl -OutFile "$OutputPath\installers\python-$PythonVersion-embed-amd64.zip"

# 2. Download get-pip.py
Invoke-WebRequest -Uri "https://bootstrap.pypa.io/get-pip.py" -OutFile "$OutputPath\installers\get-pip.py"

# 3. Download WinSW
$winswUrl = "https://github.com/winsw/winsw/releases/download/v2.12.0/WinSW.NET461.exe"
Invoke-WebRequest -Uri $winswUrl -OutFile "$OutputPath\tools\WinSW.exe"

# 4. Download NSSM
Invoke-WebRequest -Uri "https://nssm.cc/release/nssm-2.24.zip" -OutFile "$OutputPath\tools\nssm-2.24.zip"

# 5. Download IIS modules
$modules = @{
    "rewrite_amd64_en-US.msi" = "https://download.microsoft.com/download/1/2/8/128E2E22-C1B9-44A4-BE2A-5859ED1D4592/rewrite_amd64_en-US.msi"
    "requestRouter_amd64.msi" = "https://go.microsoft.com/fwlink/?LinkID=615136"
}
foreach ($module in $modules.GetEnumerator()) {
    Invoke-WebRequest -Uri $module.Value -OutFile "$OutputPath\iis-modules\$($module.Key)"
}

# 6. Download Python packages
Write-Host "Downloading Python packages..." -ForegroundColor Cyan

# Create temp venv to generate requirements
python -m venv "$OutputPath\temp_venv"
& "$OutputPath\temp_venv\Scripts\pip.exe" install reflex uvicorn msal pyjwt[crypto] httpx

# Export requirements
& "$OutputPath\temp_venv\Scripts\pip.exe" freeze > "$OutputPath\wheelhouse\requirements.txt"

# Download wheels for Windows x64
& "$OutputPath\temp_venv\Scripts\pip.exe" download `
    --only-binary=:all: `
    --platform win_amd64 `
    --python-version 311 `
    -d "$OutputPath\wheelhouse" `
    -r "$OutputPath\wheelhouse\requirements.txt"

# Also download pip, setuptools, wheel for bootstrap
& "$OutputPath\temp_venv\Scripts\pip.exe" download pip setuptools wheel virtualenv -d "$OutputPath\wheelhouse"

# Cleanup temp venv
Remove-Item -Recurse -Force "$OutputPath\temp_venv"

# 7. Generate checksums
Get-ChildItem -Path $OutputPath -Recurse -File | ForEach-Object {
    $hash = Get-FileHash $_.FullName -Algorithm SHA256
    "$($hash.Hash)  $($_.FullName.Replace($OutputPath, '.'))"
} | Out-File "$OutputPath\checksums.sha256"

Write-Host "`nOffline deployment package ready at: $OutputPath" -ForegroundColor Green
Write-Host "Transfer this folder to the air-gapped server" -ForegroundColor Yellow
```

#### Phase 2: Deploy on Air-Gapped Server

```powershell
# deploy-offline.ps1
# Run on air-gapped Windows Server

param(
    [Parameter(Mandatory=$true)]
    [string]$SourcePath,  # Path to transferred offline package
    
    [string]$InstallPath = "C:\ReflexApp",
    [string]$ServiceName = "ReflexApp"
)

$ErrorActionPreference = "Stop"

Write-Host "=== Air-Gapped Reflex Deployment ===" -ForegroundColor Cyan

# 1. Verify checksums
Write-Host "`n[1/6] Verifying file integrity..." -ForegroundColor Yellow
$checksumFile = Join-Path $SourcePath "checksums.sha256"
# (Verification logic here - see full script)

# 2. Extract Python
Write-Host "`n[2/6] Setting up Python..." -ForegroundColor Yellow
$pythonZip = Get-ChildItem "$SourcePath\installers\python-*-embed-amd64.zip" | Select-Object -First 1
Expand-Archive $pythonZip.FullName -DestinationPath "$InstallPath\python" -Force

# Configure embedded Python
$pthFile = Get-ChildItem "$InstallPath\python\python*._pth" | Select-Object -First 1
$pthContent = @"
python311.zip
.
.\Scripts
.\Lib\site-packages
import site
"@
Set-Content -Path $pthFile.FullName -Value $pthContent

# 3. Install pip
Write-Host "`n[3/6] Installing pip..." -ForegroundColor Yellow
$pythonExe = "$InstallPath\python\python.exe"
$wheelhouse = "$SourcePath\wheelhouse"

& $pythonExe "$SourcePath\installers\get-pip.py" --no-index --find-links=$wheelhouse

# 4. Create virtual environment and install packages
Write-Host "`n[4/6] Installing application packages..." -ForegroundColor Yellow
& $pythonExe -m pip install --no-index --find-links=$wheelhouse virtualenv
& $pythonExe -m virtualenv "$InstallPath\venv"
& "$InstallPath\venv\Scripts\pip.exe" install --no-index --find-links=$wheelhouse -r "$wheelhouse\requirements.txt"

# 5. Install IIS modules
Write-Host "`n[5/6] Installing IIS modules..." -ForegroundColor Yellow
net stop WAS /y 2>$null
Start-Process msiexec.exe -ArgumentList "/i `"$SourcePath\iis-modules\rewrite_amd64_en-US.msi`" /qn /norestart" -Wait
Start-Process msiexec.exe -ArgumentList "/i `"$SourcePath\iis-modules\requestRouter_amd64.msi`" /qn /norestart" -Wait
net start WAS
net start W3SVC

# 6. Install Windows service
Write-Host "`n[6/6] Installing Windows service..." -ForegroundColor Yellow
Expand-Archive "$SourcePath\tools\nssm-2.24.zip" -DestinationPath "$InstallPath\tools" -Force
$nssm = "$InstallPath\tools\nssm-2.24\win64\nssm.exe"

& $nssm install $ServiceName "$InstallPath\venv\Scripts\python.exe"
& $nssm set $ServiceName AppParameters "-m reflex run --env prod"
& $nssm set $ServiceName AppDirectory $InstallPath
# (Additional NSSM configuration...)

Write-Host "`n=== Deployment Complete ===" -ForegroundColor Green
```

---

### 8. deployment-checklist.md

#### Pre-Deployment Checklist

- [ ] **Python 3.11+** installed or embedded Python prepared
- [ ] **Virtual environment** created with all dependencies
- [ ] **rxconfig.py** configured with production URLs
- [ ] **Environment variables** documented and set
- [ ] **Database** migrations completed
- [ ] **Firewall rules** allow IIS ports (80, 443)

#### IIS Configuration Checklist

- [ ] **WebSocket Protocol** feature installed
- [ ] **URL Rewrite Module 2.1** installed
- [ ] **Application Request Routing 3.0** installed
- [ ] **Proxy enabled** at server level
- [ ] **Timeout set to 300+ seconds** for WebSocket
- [ ] **responseBufferLimit set to 0** for streaming
- [ ] **SSL certificate** bound to site

#### Authentication Checklist (Phase 1: Windows Auth)

- [ ] **Windows Authentication** feature installed
- [ ] **Anonymous Authentication** disabled
- [ ] **SPNs registered** (setspn -X shows no duplicates)
- [ ] **HTTP_X_REMOTE_USER** in allowedServerVariables
- [ ] **Backend validates** X-Remote-User header
- [ ] **Test with domain user** - verify LOGON_USER populated

#### Authentication Checklist (Phase 2: Entra ID)

- [ ] **App Registration** completed in Entra admin center
- [ ] **Redirect URIs** configured for all environments
- [ ] **Client secret** generated and stored securely
- [ ] **API permissions** granted admin consent
- [ ] **Session middleware** configured with secure cookies
- [ ] **PKCE enabled** in OAuth flow
- [ ] **Test login flow** end-to-end

#### Service Wrapper Checklist

- [ ] **WinSW/NSSM** executable in place
- [ ] **Configuration file** validated (XML syntax)
- [ ] **Log directory** created with write permissions
- [ ] **Environment variables** set in service config
- [ ] **Service installed** and running
- [ ] **Auto-start** enabled
- [ ] **Recovery actions** configured

#### Go/No-Go Validation

```powershell
# Quick validation script
$checks = @()

# Check service running
$service = Get-Service -Name "ReflexApp" -ErrorAction SilentlyContinue
$checks += @{Name="Service Running"; Pass=$service.Status -eq "Running"}

# Check port listening
$listener = Get-NetTCPConnection -LocalPort 3000 -State Listen -ErrorAction SilentlyContinue
$checks += @{Name="Port 3000 Listening"; Pass=$listener -ne $null}

# Check IIS site
$site = Get-Website -Name "MyReflexApp" -ErrorAction SilentlyContinue
$checks += @{Name="IIS Site Running"; Pass=$site.State -eq "Started"}

# Check SSL binding
$binding = Get-WebBinding -Name "MyReflexApp" -Protocol https
$checks += @{Name="HTTPS Binding"; Pass=$binding -ne $null}

# Check WebSocket endpoint
try {
    $ws = Invoke-WebRequest -Uri "https://localhost/_event/" -UseBasicParsing -TimeoutSec 5
    $checks += @{Name="WebSocket Endpoint"; Pass=$true}
} catch {
    $checks += @{Name="WebSocket Endpoint"; Pass=$false}
}

# Output results
$checks | ForEach-Object {
    $status = if ($_.Pass) {"✓"} else {"✗"}
    $color = if ($_.Pass) {"Green"} else {"Red"}
    Write-Host "$status $($_.Name)" -ForegroundColor $color
}
```

---

### 9-10. configuration-templates.md

See the complete templates in sections above. Key templates included:
- **WinSW XML** with log rotation and environment variables
- **NSSM PowerShell** installation script
- **IIS web.config** for reverse proxy (3 variants)
- **rxconfig.py** for production deployment
- **Python middleware** for Windows Auth and Entra ID

---

## Advanced Documentation (6 Files)

### 11. troubleshooting-guide.md

#### 502 Error Resolution

| Error Code | Win32 Status | Cause | Solution |
|------------|--------------|-------|----------|
| 502.3 | 12002 | Timeout | Increase proxy timeout to 300+ sec |
| 502.3 | 12030 | Connection aborted | Check backend is running |
| 502.4 | 0 | No server available | Verify backend port and firewall |

```powershell
# Diagnose 502 errors
# Check IIS logs for win32 status
Get-Content C:\inetpub\logs\LogFiles\W3SVC1\*.log -Tail 20 | Select-String "502"

# Increase timeout
appcmd.exe set config -section:system.webServer/proxy /timeout:"00:05:00" /commit:apphost
```

#### WebSocket Connection Failures

```powershell
# Verify WebSocket feature enabled
Get-WindowsFeature Web-WebSockets

# Check ARR WebSocket support
appcmd.exe list config -section:system.webServer/proxy

# Test WebSocket endpoint directly
# Should return 101 Switching Protocols
curl -v -H "Upgrade: websocket" -H "Connection: Upgrade" http://localhost:3000/_event/
```

#### Authentication Debugging

```powershell
# Check Kerberos tickets
klist

# Purge and refresh tickets
klist purge

# Verify SPN
setspn -L DOMAIN\svc_account

# Check for SPN duplicates
setspn -X

# Enable Kerberos logging
# HKLM\SYSTEM\CurrentControlSet\Control\Lsa\Kerberos\Parameters
# LogLevel = 1
```

---

### 12. security-hardening.md

#### Least Privilege Principles

```powershell
# Create dedicated service account
$password = ConvertTo-SecureString "ComplexP@ssw0rd!" -AsPlainText -Force
New-LocalUser -Name "svc_reflex" -Password $password -Description "Reflex App Service Account"

# Grant minimum required permissions
$acl = Get-Acl "C:\ReflexApp"
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    "svc_reflex", "ReadAndExecute,Write", "ContainerInherit,ObjectInherit", "None", "Allow"
)
$acl.AddAccessRule($rule)
Set-Acl "C:\ReflexApp" $acl

# Logs directory - write access
$logsAcl = Get-Acl "C:\ReflexApp\logs"
$logsRule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    "svc_reflex", "Modify", "ContainerInherit,ObjectInherit", "None", "Allow"
)
$logsAcl.AddAccessRule($logsRule)
Set-Acl "C:\ReflexApp\logs" $logsAcl
```

#### Cookie Security Configuration

```python
# Always use these settings in production
SESSION_CONFIG = {
    "secret_key": os.getenv("SESSION_SECRET"),  # 32+ char random string
    "session_cookie": "__Host-session",  # __Host- prefix enforces security
    "max_age": 3600,
    "same_site": "lax",
    "https_only": True,  # MANDATORY for production
    "httponly": True,    # Prevents XSS access
}
```

---

### 13-16. Additional Documentation

*Maintenance operations, migration guides, authentication comparison, and testing validation documentation follow similar detailed patterns covering:*

- **Log rotation** schedules and retention policies
- **Certificate renewal** automation with Task Scheduler
- **Migration path** from Windows Auth to Entra ID
- **Load testing** with locust or k6
- **Authentication verification** scripts

---

## LLM Usage Instructions

### Claude Desktop (MCP Filesystem)

```json
// claude_desktop_config.json
{
  "mcpServers": {
    "reflex-skill": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-filesystem", "/path/to/reflex-windows-deployment-skill"]
    }
  }
}
```

**Usage prompt:**
> "Using the reflex-windows-deployment-skill folder, help me deploy a Reflex app on Windows Server 2022 with Windows Authentication. Start with the SKILL.md overview."

### Cursor / VS Code

Create `.cursorrules` in project root:

```markdown
# Reflex Windows Deployment Context

When helping with Reflex deployment on Windows:
1. Reference docs in `reflex-windows-deployment-skill/` folder
2. Use WinSW for XML-based service configuration
3. Use NSSM for CLI-based service management
4. Always enable WebSocket support in IIS
5. Set proxy timeout to 300+ seconds for Reflex
6. Phase 1 = Windows Auth, Phase 2 = Entra ID
```

### Cline

Add to `.ai-context/instructions.md`:

```markdown
## Reflex Windows Deployment Skill

This project uses the reflex-windows-deployment-skill folder for Windows Server deployment guidance.

Key files:
- SKILL.md: Start here for decision tree
- docs/core/: 10 essential documentation files
- templates/: Copy-paste configurations
- examples/: Complete deployment scenarios
```

---

## Folder Structure Reference

```
reflex-windows-deployment-skill/
├── SKILL.md                           # Master overview, decision tree
├── docs/
│   ├── core/
│   │   ├── reflex-application-preparation.md
│   │   ├── windows-service-management.md
│   │   ├── iis-reverse-proxy-setup.md
│   │   ├── windows-authentication-phase1.md
│   │   ├── ms-entra-authentication-phase2.md
│   │   ├── multi-app-deployment-strategy.md
│   │   ├── air-gapped-deployment-guide.md
│   │   ├── deployment-checklist.md
│   │   └── configuration-templates.md
│   └── advanced/
│       ├── troubleshooting-guide.md
│       ├── security-hardening.md
│       ├── maintenance-operations.md
│       ├── migration-and-scaling.md
│       ├── authentication-comparison.md
│       └── testing-and-validation.md
├── templates/
│   ├── winsw/
│   │   └── winsw.xml
│   ├── nssm/
│   │   └── install-service.ps1
│   ├── iis/
│   │   ├── web.config.basic
│   │   ├── web.config.winauth
│   │   └── web.config.entra
│   ├── reflex/
│   │   └── rxconfig.py
│   └── deployment/
│       ├── prepare-offline.ps1
│       └── deploy-offline.ps1
├── examples/
│   ├── single-app-windows-auth/
│   ├── multi-app-entra-auth/
│   └── air-gapped-deployment/
└── diagrams/
    ├── architecture-overview.mmd
    ├── oauth2-pkce-flow.mmd
    ├── iis-request-routing.mmd
    ├── windows-auth-flow.mmd
    └── deployment-decision-tree.mmd
```

---

## Authentication Comparison Matrix

| Feature | Phase 1: Windows Auth | Phase 2: Entra ID |
|---------|----------------------|-------------------|
| **Use Case** | Intranet, Air-gapped | Internet-facing, SaaS |
| **Connectivity** | Offline (DC only) | Online (Azure required) |
| **Implementation** | Low (IIS config) | Medium (code changes) |
| **MFA** | Desktop login dependent | Native support |
| **SSO** | Automatic (domain-joined) | Configured per app |
| **User Source** | Active Directory | Entra ID (synced or cloud) |
| **Session Duration** | Kerberos ticket (~10h) | Configurable (1h default) |
| **Logout** | Close browser | Explicit + Entra logout |
| **Group Claims** | Via AD query | In JWT token |
| **Best For** | Corporate intranets | Modern cloud apps |

This comprehensive skill folder provides everything needed to deploy Reflex applications on Windows Server with enterprise-grade reliability, security, and authentication options.