# Agent Response Patterns for SQLAlchemy Queries

This guide provides conversational patterns for AI agents responding to user queries about SQLAlchemy ORM operations in customer support systems.

## Response Framework

When responding to SQLAlchemy queries, structure responses as:

1. **Acknowledge the query** - Show understanding of what they're asking
2. **Provide immediate solution** - Quick, copy-paste ready code
3. **Explain key concepts** - Why this approach works
4. **Highlight gotchas** - Common mistakes to avoid
5. **Suggest next steps** - Related patterns they might need

## Query Pattern 1: "How do I create/define a model?"

### User Query Examples:
- "Create a SQLAlchemy model for tickets"
- "Define a User model with relationships"
- "Set up database models for support system"

### Agent Response Template:

```
To create a customer support model, define a declarative class using Mapped types with SQLAlchemy 2.0:

[Provide clean model example with Mapped types, indexes, relationships]

**Key points:**
- Use Mapped[type] for all columns (required by SQLAlchemy 2.0+)
- Add indexes on foreign keys and frequently queried fields
- Define relationships with back_populates for bidirectional access
- Include timestamps (created_at, updated_at) for audit trails

**Common gotchas:**
- Don't forget `nullable=False` for required fields
- Always use timezone-aware DateTime: `DateTime(timezone=True)`
- Use `server_default=func.now()` for automatic timestamps

**Next steps:**
- Add validation using Pydantic models
- Set up async session for FastAPI integration
- Create Alembic migration for this model
```

### Example Response:

**User**: "How do I create a Ticket model?"

**Agent**: 
```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum
from datetime import datetime
import enum

class Base(DeclarativeBase):
    pass

class TicketStatus(enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class Ticket(Base):
    __tablename__ = "tickets"
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Core fields
    ticket_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[TicketStatus] = mapped_column(
        Enum(TicketStatus),
        default=TicketStatus.OPEN,
        index=True  # Index frequently filtered fields
    )
    
    # Foreign keys
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    
    # Timestamps (always timezone-aware)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # Relationships
    creator: Mapped["User"] = relationship("User", back_populates="tickets")
```

**Key points:**
- Uses `Mapped[type]` syntax (SQLAlchemy 2.0 requirement)
- Indexes on `ticket_number`, `status`, and `creator_id` for query performance
- Timezone-aware timestamps with automatic updates
- Enum for status ensures type safety

**Common mistakes to avoid:**
- Forgetting `index=True` on foreign keys → slow queries
- Using `DateTime` without `timezone=True` → timezone bugs
- Not adding `unique=True` on ticket_number → duplicate tickets

**What you need next:**
- User model to complete the relationship
- Async session setup for FastAPI
- See `EXAMPLES.md` for complete working example
```

## Query Pattern 2: "How do I query/search data?"

### User Query Examples:
- "Query tickets by status"
- "Search with multiple filters"
- "Get user with all their tickets"

### Agent Response Template:

```
Use the select() construct with where() for filtering. For related data, add eager loading to avoid N+1 queries:

[Provide query example with eager loading]

**Key points:**
- Always use async/await with AsyncSession
- Use joinedload() for one-to-one/many-to-one relationships
- Use selectinload() for one-to-many/many-to-many relationships
- Call unique() after execute() when using joinedload()

**Critical gotcha:**
- Without eager loading, accessing relationships triggers additional queries (N+1 problem)
- Without unique() on joinedload, you get duplicate rows

**Next steps:**
- Add pagination with limit()/offset()
- Implement full-text search
- Add result count query
```

### Example Response:

**User**: "How do I search tickets with filters?"

**Agent**:
```python
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import joinedload, selectinload

async def search_tickets(
    session: AsyncSession,
    status: Optional[str] = None,
    creator_id: Optional[int] = None,
    search_term: Optional[str] = None
) -> List[Ticket]:
    """Search tickets with optional filters and eager loading."""
    
    # Build base query with eager loading
    stmt = (
        select(Ticket)
        .options(
            joinedload(Ticket.creator),  # Load creator in same query
            selectinload(Ticket.comments)  # Load comments in separate query
        )
    )
    
    # Build filter conditions
    filters = []
    
    if status:
        filters.append(Ticket.status == status)
    
    if creator_id:
        filters.append(Ticket.creator_id == creator_id)
    
    if search_term:
        # Search in title or description
        filters.append(
            or_(
                Ticket.title.ilike(f"%{search_term}%"),
                Ticket.description.ilike(f"%{search_term}%")
            )
        )
    
    # Apply filters if any
    if filters:
        stmt = stmt.where(and_(*filters))
    
    # Execute query
    result = await session.execute(stmt)
    
    # CRITICAL: Use unique() when using joinedload to deduplicate
    tickets = result.unique().scalars().all()
    
    return tickets
```

**Why this works:**
- `joinedload(Ticket.creator)` loads creator in the same SQL query (efficient for many-to-one)
- `selectinload(Ticket.comments)` loads all comments in a second query (efficient for one-to-many)
- Dynamic filter building allows optional parameters
- `ilike()` provides case-insensitive search

**Critical mistakes to avoid:**
- ❌ Forgetting `unique()` with `joinedload()` → duplicate rows
- ❌ Not using eager loading → N+1 query problem (1 query + N queries for each relationship)
- ❌ Using `joinedload()` for collections → cartesian product with huge result sets

**Performance tips:**
- Add indexes on filtered columns (status, creator_id)
- Use pagination for large result sets
- Consider full-text search for description field

**See also:**
- `EXAMPLES.md` - Example 4 for complete search implementation
- `references/advanced-patterns.md` - Complex filter patterns
```

## Query Pattern 3: "Set up async database / FastAPI integration"

### User Query Examples:
- "Set up async SQLAlchemy with FastAPI"
- "Configure database connection"
- "Create session dependency"

### Agent Response Template:

```
Set up async engine, session factory, and FastAPI dependency:

[Provide complete async setup code]

**Critical settings:**
- `pool_pre_ping=True` prevents stale connection errors
- `expire_on_commit=False` keeps objects usable after commit
- Always use async context manager for session lifecycle

**Common mistakes:**
- Forgetting pool_pre_ping → stale connection errors in production
- Not handling session rollback on errors → transaction leaks
- Using sync engine with async code → runtime errors

**Next steps:**
- Create models and tables
- Implement CRUD endpoints
- Add error handling middleware
```

### Example Response:

**User**: "How do I set up async SQLAlchemy with FastAPI?"

**Agent**:
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator
from fastapi import Depends

# Step 1: Create async engine
async_engine = create_async_engine(
    "postgresql+asyncpg://user:password@localhost:5432/support_db",
    echo=False,  # Set True for SQL logging during development
    pool_pre_ping=True,  # CRITICAL: Verify connections before use
    pool_size=10,  # Number of connections to maintain
    max_overflow=20  # Additional connections when pool full
)

# Step 2: Create session factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,  # CRITICAL: Keep objects usable after commit
    autocommit=False,
    autoflush=False
)

# Step 3: Create FastAPI dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Database session dependency for FastAPI."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()  # Auto-commit on success
        except Exception:
            await session.rollback()  # Auto-rollback on error
            raise
        finally:
            await session.close()

# Step 4: Use in FastAPI endpoint
from fastapi import FastAPI, Depends

app = FastAPI()

@app.get("/tickets/")
async def list_tickets(session: AsyncSession = Depends(get_db)):
    """List tickets using injected session."""
    stmt = select(Ticket).limit(50)
    result = await session.execute(stmt)
    tickets = result.scalars().all()
    return tickets
```

**Critical settings explained:**
- **`pool_pre_ping=True`**: Tests each connection before using it. Without this, you'll get "server closed connection" errors.
- **`expire_on_commit=False`**: Keeps loaded objects usable after commit. With default True, accessing object attributes after commit triggers new queries.
- **Auto-commit/rollback**: The dependency handles commit on success, rollback on error automatically.

**Common mistakes:**
- ❌ Missing `pool_pre_ping` → Stale connection errors after idle periods
- ❌ Missing `expire_on_commit=False` → Extra queries after commit
- ❌ Not using `async with` → Session leaks
- ❌ Calling `session.close()` explicitly when using `async with` → Double-close error

**Production checklist:**
- [ ] Set `echo=False` (don't log SQL in production)
- [ ] Configure `pool_size` for your workload (10-20 typical)
- [ ] Set up health check endpoint
- [ ] Add connection pool monitoring
- [ ] Configure timeouts

**Next steps:**
- Create database models
- Implement CRUD operations
- Add migration with Alembic
```

## Query Pattern 4: "Optimize query performance"

### User Query Examples:
- "My queries are slow"
- "How to avoid N+1 queries"
- "Optimize ticket loading"

### Agent Response Template:

```
Query performance issues are usually caused by N+1 queries (lazy loading relationships) or missing indexes. Fix with eager loading and index analysis:

[Provide before/after comparison]

**Diagnosis:**
- Check query count in logs (should be constant, not proportional to results)
- Use EXPLAIN ANALYZE to see query plan
- Monitor which relationships are accessed

**Solutions:**
- Eager load with joinedload()/selectinload()
- Add indexes on filtered/joined columns
- Consider read replicas for analytics

**Next steps:**
- Profile queries in production
- Add query timing middleware
- Implement caching for hot paths
```

### Example Response:

**User**: "My ticket list query is slow and making too many database queries"

**Agent**:

This is the classic N+1 query problem. Here's the fix:

**❌ Problem (N+1 queries):**
```python
# This creates 1 + N queries (1 for tickets, 1 for each creator)
async def get_tickets_slow(session: AsyncSession):
    stmt = select(Ticket).limit(50)
    result = await session.execute(stmt)
    tickets = result.scalars().all()
    
    # Each access triggers a new query!
    for ticket in tickets:
        print(ticket.creator.full_name)  # New query for each ticket
    
    return tickets
# Result: 51 queries (1 + 50)
```

**✅ Solution (2 queries with eager loading):**
```python
from sqlalchemy.orm import joinedload, selectinload

async def get_tickets_fast(session: AsyncSession):
    stmt = (
        select(Ticket)
        .options(
            joinedload(Ticket.creator),  # Load creators in same query
            joinedload(Ticket.assignee),  # Load assignees in same query
            selectinload(Ticket.comments)  # Load all comments in 2nd query
        )
        .limit(50)
    )
    
    result = await session.execute(stmt)
    tickets = result.unique().scalars().all()
    
    # No additional queries!
    for ticket in tickets:
        print(ticket.creator.full_name)  # Already loaded
        print(f"Comments: {len(ticket.comments)}")  # Already loaded
    
    return tickets
# Result: 2 queries total (1 for tickets+creators+assignees, 1 for all comments)
```

**Why this is 25x faster:**
- Before: 51 queries (1 + 50 × 1 for creators)
- After: 2 queries (1 for tickets, 1 for comments)
- Latency reduced from ~500ms to ~20ms

**Which eager loading strategy to use:**
- **`joinedload()`** - Use for many-to-one, one-to-one (single related item)
  - Example: `Ticket.creator`, `Ticket.assignee`
  - Loads in same query using JOIN
  
- **`selectinload()`** - Use for one-to-many, many-to-many (collections)
  - Example: `Ticket.comments`, `Ticket.tags`
  - Loads in separate query using IN clause

**Don't forget:**
- Call `.unique()` when using `joinedload()` to remove duplicate rows
- Add indexes on foreign keys (creator_id, assignee_id)
- Check query execution with `echo=True` during development

**Additional optimizations:**
```python
# Add composite index for common filter patterns
__table_args__ = (
    Index("ix_ticket_status_created", "status", "created_at"),
)

# Use pagination to limit result size
stmt = stmt.offset(page * page_size).limit(page_size)

# Consider caching for frequently accessed data
@cache(ttl=300)  # Cache for 5 minutes
async def get_open_tickets_count(session):
    ...
```

**See also:**
- `references/advanced-patterns.md` - Complex query optimization
- `EXAMPLES.md` - Example 5 for complete eager loading patterns
```

## Query Pattern 5: "Write tests"

### User Query Examples:
- "Test SQLAlchemy code"
- "Set up test database"
- "Write pytest fixtures"

### Agent Response Template:

```
Use pytest with async fixtures for isolated test database:

[Provide pytest fixture setup]

**Key patterns:**
- Session-scoped engine (create once)
- Function-scoped session (rollback after each test)
- Factory fixtures for test data
- Use in-memory SQLite or test Postgres DB

**Best practices:**
- Always rollback after tests
- Use separate test database
- Create realistic test data
- Test both success and error cases

**Next steps:**
- Add factories for complex models
- Test with different data scenarios
- Measure test coverage
```

### Example Response:

**User**: "How do I write tests for SQLAlchemy code?"

**Agent**:
```python
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# conftest.py - Pytest fixtures

@pytest.fixture(scope="session")
def test_database_url():
    """Test database URL (use separate test database!)."""
    return "postgresql+asyncpg://test_user:test_pass@localhost/test_support_db"

@pytest.fixture(scope="session")
async def async_engine(test_database_url):
    """Create test engine once per session."""
    engine = create_async_engine(
        test_database_url,
        echo=True  # See SQL queries during testing
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup: drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

@pytest.fixture
async def async_session(async_engine):
    """Create fresh session for each test with automatic rollback."""
    async_session_factory = async_sessionmaker(
        bind=async_engine,
        expire_on_commit=False
    )
    
    async with async_session_factory() as session:
        yield session
        # Rollback after test to isolate tests
        await session.rollback()

@pytest.fixture
async def test_user(async_session):
    """Create test user for tests that need one."""
    user = User(
        email="test@example.com",
        full_name="Test User",
        password_hash="hashed_password",
        is_active=True
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    return user

# test_tickets.py - Actual tests

@pytest.mark.asyncio
async def test_create_ticket(async_session, test_user):
    """Test ticket creation."""
    ticket = Ticket(
        ticket_number="TEST-001",
        title="Test ticket",
        description="Test description",
        creator_id=test_user.id
    )
    
    async_session.add(ticket)
    await async_session.commit()
    await async_session.refresh(ticket)
    
    # Assertions
    assert ticket.id is not None
    assert ticket.status == TicketStatus.OPEN
    assert ticket.created_at is not None

@pytest.mark.asyncio
async def test_search_tickets(async_session, test_user):
    """Test ticket search with filters."""
    # Create test data
    ticket1 = Ticket(
        ticket_number="TEST-001",
        title="Payment issue",
        description="Can't process payment",
        status=TicketStatus.OPEN,
        creator_id=test_user.id
    )
    ticket2 = Ticket(
        ticket_number="TEST-002",
        title="Login problem",
        description="Can't log in",
        status=TicketStatus.RESOLVED,
        creator_id=test_user.id
    )
    async_session.add_all([ticket1, ticket2])
    await async_session.commit()
    
    # Test search
    stmt = select(Ticket).where(Ticket.status == TicketStatus.OPEN)
    result = await async_session.execute(stmt)
    tickets = result.scalars().all()
    
    # Assertions
    assert len(tickets) == 1
    assert tickets[0].ticket_number == "TEST-001"

@pytest.mark.asyncio
async def test_eager_loading(async_session, test_user):
    """Test that eager loading prevents N+1 queries."""
    # Create ticket
    ticket = Ticket(
        ticket_number="TEST-001",
        title="Test ticket",
        description="Test description",
        creator_id=test_user.id
    )
    async_session.add(ticket)
    await async_session.commit()
    
    # Clear session to force fresh load
    async_session.expire_all()
    
    # Load with eager loading
    stmt = (
        select(Ticket)
        .options(joinedload(Ticket.creator))
        .where(Ticket.id == ticket.id)
    )
    result = await async_session.execute(stmt)
    loaded_ticket = result.unique().scalar_one()
    
    # Access creator should not trigger query (already loaded)
    assert loaded_ticket.creator.email == test_user.email
```

**Key points:**
- **Session scope engine**: Created once, shared across all tests (fast)
- **Function scope session**: Fresh session per test, auto-rollback for isolation
- **Factory fixtures**: `test_user` creates reusable test data
- **`@pytest.mark.asyncio`**: Required for async test functions

**Best practices:**
- Use separate test database (never production!)
- Rollback after each test for isolation
- Test both success and error paths
- Use realistic test data

**Common mistakes:**
- ❌ Not rolling back → Tests affect each other
- ❌ Using production database → Data loss risk
- ❌ Forgetting `@pytest.mark.asyncio` → "coroutine was never awaited" error

**Next steps:**
- Add factories with pytest-factoryboy for complex test data
- Test error cases (unique violations, not found, etc.)
- Measure coverage with pytest-cov
- See `references/testing-patterns.md` for advanced patterns
```

---

**Use these response patterns to provide consistent, helpful, and actionable guidance to users working with SQLAlchemy in customer support systems.**
