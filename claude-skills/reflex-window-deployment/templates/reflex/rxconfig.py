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
