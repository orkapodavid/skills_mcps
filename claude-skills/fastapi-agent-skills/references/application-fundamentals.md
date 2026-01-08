# FastAPI Application Fundamentals

This guide covers project initialization, dependency injection, middleware, and lifecycle management.

## Project Initialization

Establish a production-ready FastAPI project skeleton with consistent structure, typed configuration, and developer tooling.

### Directory Layout
Add a layered layout to organize code:
```
app/
  api/            # routers, DTOs
  core/           # config, logging, middleware
  models/         # pydantic/ORM models
  services/       # business logic
  main.py         # app factory
```

### Basic Setup
Initialize the project structure and install dependencies:
```bash
# Create and activate environment
python -m venv .venv && source .venv/bin/activate
pip install fastapi uvicorn[standard] pydantic ruff mypy pytest coverage pre-commit
```

## Dependency Injection

Use FastAPI's dependency system to provide resources (DB sessions, settings, auth contexts) with explicit lifetimes.

### Basic Dependency
Declare callables with `Depends(...)` to inject resources into routes:
```python
from fastapi import Depends, FastAPI
from pydantic import BaseModel

class Settings(BaseModel):
    app_name: str = "DI Demo"

def get_settings() -> Settings:
    return Settings()

app = FastAPI()

@app.get("/info")
def info(settings: Settings = Depends(get_settings)) -> dict:
    return {"name": settings.app_name}
```

### Async Database Dependency
Inject an asynchronous database session using yield:
```python
from sqlalchemy.ext.asyncio import AsyncSession

async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

@app.get("/items")
async def list_items(db: AsyncSession = Depends(get_db)) -> list[dict]:
    return []
```

## Middleware Configuration

Configure built-in and custom middleware to handle concerns such as CORS, logging, and security headers.

### CORS Setup
Add `CORSMiddleware` to handle cross-origin requests:
```python
from starlette.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
```

### Custom Middleware
Implement `BaseHTTPMiddleware` for custom processing (e.g., request timing):
```python
import time
from starlette.middleware.base import BaseHTTPMiddleware

class RequestTimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        response.headers["X-Process-Time"] = str(time.perf_counter() - start)
        return response

app.add_middleware(RequestTimingMiddleware)
```

## Lifecycle Management

Initialize and dispose resources predictably using lifespan handlers.

### Lifespan Handler
Use an `asynccontextmanager` to encapsulate startup and shutdown logic:
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize engines, caches, or warming
    yield
    # Shutdown: Flush logs and close connections
```

## Critical Considerations
- Keep dependencies minimal at bootstrap.
- Prefer explicit dependency injection over global mutable state.
- Ensure shutdown logic always executes to prevent resource leaks.
- Maintain consistent Python versions (e.g., 3.10+).

## Integration with LLM Agents
- Provide explicit file paths and module names.
- Favor small composable modules.
- Document startup commands clearly.
- Describe dependency contracts (input/output types) explicitly.
