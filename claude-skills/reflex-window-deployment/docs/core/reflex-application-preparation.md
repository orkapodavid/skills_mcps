# Reflex Application Preparation

## Architecture Context: The Dual-Natured Build Artifact

Reflex is not a standard Python web application; it is a distributed system. Understanding the bifurcation of its build process is critical for diagnosing deployment failures.

### 1. The Frontend (Client-Side)
When you run `reflex export`, the framework compiles the Python UI code into a React application (Next.js). This generates static assets (HTML, JS, CSS) in `.web/_static`.
*   **Implication for IIS:** IIS acts purely as a static file server for these assets. It does not execute Python to serve the UI. This leverages IIS kernel-mode caching.

### 2. The Backend (Server-Side)
The application logic and state management reside in a Python process (FastAPI/Uvicorn).
*   **Implication for IIS:** IIS cannot execute this directly. The backend must run as a separate, persistent Windows Service. IIS acts as a Reverse Proxy, forwarding API requests and WebSockets to this service.

### 3. The State Management Mechanism
Reflex keeps state on the server. The client establishes a WebSocket connection to `/_event`.
*   **Critical Path:** If the WebSocket connection fails, the app loads (static HTML) but is non-interactive.

---

## rxconfig.py Production Configuration

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

## Build Commands for Production

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

## WebSocket Endpoints (Critical for IIS)

| Endpoint | Purpose | Protocol |
|----------|---------|----------|
| `/_event/` | Real-time state sync | WebSocket |
| `/ping` | Health check | HTTP GET |
| `/_upload` | File uploads | HTTP POST |
| `/*` | Frontend routes | HTTP |
