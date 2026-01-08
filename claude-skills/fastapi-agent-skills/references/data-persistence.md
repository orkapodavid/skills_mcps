# Data Persistence

This guide covers SQLAlchemy/SQLModel integration, asynchronous database operations, and connection pooling.

## SQLAlchemy Integration

Integrate SQLAlchemy with FastAPI to manage relational data using typed models and session Dependencies.

### Model Definition
Separate ORM models from your Pydantic DTOs for cleaner architecture:
```python
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
```

### Database Dependency
Provide database sessions to routes via `Depends`:
```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from fastapi import Depends

engine = create_async_engine("postgresql+asyncpg://user:pass@host/db")
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

@app.get("/users")
async def read_users(session: AsyncSession = Depends(get_session)):
    # use session here
    return []
```

## Async Database Operations

Use asynchronous drivers and engine configurations to ensure non-blocking I/O.

### Async CRUD
Always `await` your database operations to prevent blocking the event loop:
```python
from sqlalchemy import select

async def list_users(session: AsyncSession):
    result = await session.execute(select(User))
    return result.scalars().all()
```

## Connection Pooling

Configure the engine's pool settings to handle traffic bursts and maintain performance.

### Engine Configuration
Set `pool_size`, `max_overflow`, and timeouts:
```python
engine = create_async_engine(
    "postgresql+asyncpg://...",
    pool_size=10,
    max_overflow=20,
    pool_recycle=1800,
    pool_timeout=30,
)
```

### Resource Cleanup
Dispose of the engine pool during application shutdown:
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()
```

## Critical Considerations
- Use async drivers (e.g., `asyncpg`) for all database operations.
- Avoid mixing synchronous and asynchronous database calls in the same route.
- Manage transactions explicitly and avoid implicit commits in dependencies.
- Monitor your database connection pool to avoid exhaustion.

## Integration with LLM Agents
- Provide a standard `get_session` import path for agents to use.
- Document the location of your ORM schemas and Pydantic models.
- Explicitly state that all database interactions must be asynchronous.
