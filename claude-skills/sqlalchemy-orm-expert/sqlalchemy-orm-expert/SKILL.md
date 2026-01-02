---
name: SQLAlchemy ORM Expert
version: 2.0.0
description: This skill should be used when the user asks to "create SQLAlchemy models", "write ORM queries", "set up async database", "implement relationships", "optimize database queries", "handle sessions", "write migrations", "test database code", or mentions SQLAlchemy, PostgreSQL, database ORM, async sessions, query optimization, or customer support data models. Provides comprehensive SQLAlchemy 2.0+ guidance for building customer support systems.
author: Customer Support Tech Enablement Team
version_info:
  sqlalchemy: ">=2.0"
  python: ">=3.10"
tags:
  - python
  - sqlalchemy
  - orm
  - postgresql
  - database
  - customer-support
  - backend
  - fastapi
  - async
  - testing
  - data-curation
context:
  - customer_support
  - technical_enablement
  - backend_engineering
  - data_management
dependencies:
  - sqlalchemy>=2.0
  - asyncpg
  - psycopg2-binary
  - alembic
  - pytest
  - pytest-asyncio
supported_frameworks:
  - FastAPI
  - Flask
  - Django
use_cases:
  - Support ticket management
  - User authentication and authorization
  - Data curation and bulk operations
  - Analytics and reporting
  - Audit trails and compliance
---

# SQLAlchemy ORM Expert Skill

## Overview

Use SQLAlchemy 2.0+ for building customer support systems with robust ORM patterns, async operations, and PostgreSQL integration. This skill provides agent-ready guidance for implementing database models, queries, sessions, and migrations in production support applications.

## When to Use This Skill

Load this skill when handling queries about:
- **Model creation**: Defining database models, relationships, enums
- **Query operations**: Writing selects, filters, joins, aggregations
- **Async patterns**: Setting up async sessions, engines, FastAPI integration
- **Optimization**: Eager loading, N+1 prevention, indexing, connection pooling
- **Data operations**: CRUD, bulk operations, soft deletes, audit trails
- **Testing**: Pytest fixtures, test databases, async test patterns
- **Migrations**: Alembic setup, creating/applying migrations

## Quick Start Pattern

### Define Models

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Ticket(Base):
    __tablename__ = "tickets"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(50), index=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    creator: Mapped["User"] = relationship(back_populates="tickets")
```

### Set Up Async Session

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/db",
    pool_pre_ping=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)
```

### Query with Eager Loading

```python
from sqlalchemy import select
from sqlalchemy.orm import joinedload

async def get_tickets(session):
    stmt = (
        select(Ticket)
        .options(joinedload(Ticket.creator))
        .where(Ticket.status == "open")
    )
    result = await session.execute(stmt)
    return result.unique().scalars().all()
```

## Agent Response Patterns

When responding to user queries, follow these patterns:

### Query: "How do I create a model?"
**Response**: Provide declarative model with Mapped types, show relationship setup, explain indexes.

### Query: "Set up async database"
**Response**: Show async engine creation, session factory setup, FastAPI dependency pattern.

### Query: "Optimize query performance"
**Response**: Identify N+1 issues, demonstrate eager loading (joinedload/selectinload), suggest indexes.

### Query: "Write bulk operations"
**Response**: Show bulk insert/update patterns, explain transaction handling, mention PostgreSQL RETURNING.

### Query: "Test database code"
**Response**: Provide pytest fixtures for engine/session/test data, show async test patterns.

### Query: "Handle migrations"
**Response**: Show Alembic init/revision/upgrade workflow, provide migration template.

## Core Patterns

### Relationships
- **One-to-Many**: Use `relationship()` with `back_populates`
- **Many-to-Many**: Create association table, use `secondary=`
- **Self-Referential**: Foreign key to same table

### Query Optimization
- **Avoid N+1**: Use `joinedload()` for one-to-one, `selectinload()` for collections
- **Indexes**: Add on foreign keys, frequently filtered columns, unique constraints
- **Pagination**: Use `.limit()` and `.offset()` with total count

### Session Management
- **Async**: Always use `async with` for session lifecycle
- **FastAPI**: Create dependency with `Depends(get_db)`
- **Testing**: Rollback after each test, use function scope

### Error Handling
- **Rollback**: Always rollback on exceptions in session context
- **Unique violations**: Catch `IntegrityError` for duplicates
- **Not found**: Use `.scalar_one_or_none()` instead of `.one()`

## Critical Gotchas

1. **Lazy loading in async fails**: Always eager load relationships
2. **Missing `unique()` on joinedload**: Causes duplicate rows
3. **Forgetting `pool_pre_ping`**: Leads to stale connection errors
4. **Mixed sync/async**: Never mix - use async throughout
5. **No indexes on foreign keys**: Performance degrades with scale
6. **Not using transactions**: Risk partial updates on errors
7. **Timezone-naive DateTime**: Always use `timezone=True`
8. **Exposing raw errors**: Catch and transform for user-facing APIs

## Additional Resources

### Reference Files
Detailed patterns and advanced techniques in `references/`:
- **`advanced-patterns.md`** - Complex queries, aggregations, analytics
- **`bulk-operations.md`** - High-performance data curation patterns
- **`testing-patterns.md`** - Comprehensive pytest strategies
- **`error-handling.md`** - Error patterns and edge cases
- **`migration-guide.md`** - Alembic workflows and best practices

### Example Files
Production-ready examples in `EXAMPLES.md`:
- Complete customer support models with relationships
- FastAPI integration with async sessions
- Advanced search with filters and pagination
- Bulk operations for data curation
- Analytics dashboard queries
- Pytest fixtures and test patterns
- Migration templates

### Scripts
Utility scripts in `scripts/` (to be created):
- `validate-models.py` - Check model definitions
- `test-connection.py` - Verify database connectivity
- `generate-migration.sh` - Alembic migration workflow

## How Agents Should Use This Skill

**Step 1: Understand the user query type**
- Model creation → Show declarative pattern with Mapped types
- Query writing → Demonstrate select with filters and eager loading
- Performance → Identify N+1, suggest indexes and optimization
- Testing → Provide pytest fixtures and async test patterns
- Migration → Show Alembic workflow

**Step 2: Provide context-appropriate response**
- Start with quick example for immediate use
- Reference EXAMPLES.md for complete runnable code
- Point to references/ for deep dives on specific topics
- Highlight common pitfalls relevant to the query

**Step 3: Include validation and best practices**
- Show proper error handling
- Mention testing approach
- Suggest performance considerations
- Flag security implications if relevant

**Step 4: Offer next steps**
- Related patterns the user might need
- Testing recommendations
- Performance optimization opportunities
- Migration considerations

## Production Checklist

When implementing SQLAlchemy for production:
- [ ] Models use Mapped[] types with proper nullable/index flags
- [ ] Relationships configured with back_populates and cascade
- [ ] Async engine has pool_pre_ping=True
- [ ] Sessions use expire_on_commit=False for async
- [ ] Queries use eager loading (joinedload/selectinload)
- [ ] Indexes on all foreign keys and filter columns
- [ ] Soft deletes implemented where needed
- [ ] Audit trails for compliance-critical data
- [ ] Error handling wraps all database operations
- [ ] Pytest fixtures for test database lifecycle
- [ ] Alembic migrations for schema changes
- [ ] Connection pooling configured for workload

---

**Built for AI agents assisting with customer support system development**
