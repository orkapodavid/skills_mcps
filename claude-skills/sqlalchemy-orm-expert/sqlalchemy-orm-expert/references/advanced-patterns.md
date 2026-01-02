# Advanced SQLAlchemy Patterns for Customer Support Systems

This reference provides advanced patterns for complex queries, aggregations, analytics, and sophisticated ORM techniques specific to customer support applications.

## Complex Query Patterns

### Multi-Filter Search with Dynamic Conditions

Build complex search queries dynamically based on user input:

```python
from sqlalchemy import select, and_, or_, func
from typing import Optional, List

async def advanced_ticket_search(
    session: AsyncSession,
    search_term: Optional[str] = None,
    status_list: Optional[List[str]] = None,
    priority_list: Optional[List[str]] = None,
    assignee_id: Optional[int] = None,
    created_after: Optional[datetime] = None,
    has_comments: Optional[bool] = None
) -> tuple[List[Ticket], int]:
    """Dynamic search with multiple optional filters."""
    
    # Base query with eager loading
    stmt = (
        select(Ticket)
        .options(
            joinedload(Ticket.creator),
            joinedload(Ticket.assignee),
            selectinload(Ticket.tags)
        )
    )
    
    # Build filter list dynamically
    filters = [Ticket.deleted_at.is_(None)]  # Always exclude soft-deleted
    
    if search_term:
        filters.append(
            or_(
                Ticket.title.ilike(f"%{search_term}%"),
                Ticket.description.ilike(f"%{search_term}%"),
                Ticket.ticket_number.ilike(f"%{search_term}%")
            )
        )
    
    if status_list:
        filters.append(Ticket.status.in_(status_list))
    
    if priority_list:
        filters.append(Ticket.priority.in_(priority_list))
    
    if assignee_id:
        filters.append(Ticket.assignee_id == assignee_id)
    
    if created_after:
        filters.append(Ticket.created_at >= created_after)
    
    # Apply all filters
    stmt = stmt.where(and_(*filters))
    
    # Handle comment filter (requires join)
    if has_comments is not None:
        if has_comments:
            stmt = stmt.join(Ticket.comments).group_by(Ticket.id).having(
                func.count(Comment.id) > 0
            )
        else:
            stmt = stmt.outerjoin(Ticket.comments).group_by(Ticket.id).having(
                func.count(Comment.id) == 0
            )
    
    # Get total count before pagination
    count_stmt = select(func.count()).select_from(stmt.distinct().subquery())
    total = (await session.execute(count_stmt)).scalar_one()
    
    # Execute main query
    result = await session.execute(stmt)
    tickets = list(result.unique().scalars().all())
    
    return tickets, total
```

### Window Functions for Rankings

Use window functions for analytics:

```python
from sqlalchemy import select, func, over

async def get_top_agents_by_resolution_time(
    session: AsyncSession,
    limit: int = 10
) -> List[Dict]:
    """Rank agents by average resolution time using window functions."""
    
    stmt = (
        select(
            User.full_name,
            func.count(Ticket.id).label("ticket_count"),
            func.avg(
                func.extract("epoch", Ticket.resolved_at - Ticket.created_at) / 3600
            ).label("avg_resolution_hours"),
            func.rank().over(
                order_by=func.avg(
                    func.extract("epoch", Ticket.resolved_at - Ticket.created_at)
                ).asc()
            ).label("rank")
        )
        .join(Ticket, Ticket.assignee_id == User.id)
        .where(
            and_(
                Ticket.resolved_at.is_not(None),
                Ticket.deleted_at.is_(None)
            )
        )
        .group_by(User.id, User.full_name)
        .order_by(text("avg_resolution_hours ASC"))
        .limit(limit)
    )
    
    result = await session.execute(stmt)
    return [
        {
            "agent": row[0],
            "tickets_resolved": row[1],
            "avg_hours": float(row[2]),
            "rank": row[3]
        }
        for row in result
    ]
```

### Subqueries and CTEs

Common Table Expressions for complex logic:

```python
from sqlalchemy import select, func, literal_column

async def get_tickets_with_response_stats(
    session: AsyncSession
) -> List[Dict]:
    """Get tickets with first response time using CTE."""
    
    # CTE for first comment timestamps
    first_comment_cte = (
        select(
            Comment.ticket_id,
            func.min(Comment.created_at).label("first_comment_at")
        )
        .group_by(Comment.ticket_id)
        .cte("first_comments")
    )
    
    # Main query joining with CTE
    stmt = (
        select(
            Ticket.id,
            Ticket.ticket_number,
            Ticket.title,
            Ticket.created_at,
            first_comment_cte.c.first_comment_at,
            (
                func.extract(
                    "epoch",
                    first_comment_cte.c.first_comment_at - Ticket.created_at
                ) / 3600
            ).label("response_time_hours")
        )
        .outerjoin(
            first_comment_cte,
            Ticket.id == first_comment_cte.c.ticket_id
        )
        .where(Ticket.deleted_at.is_(None))
        .order_by(Ticket.created_at.desc())
    )
    
    result = await session.execute(stmt)
    return [
        {
            "ticket_id": row[0],
            "ticket_number": row[1],
            "title": row[2],
            "created_at": row[3],
            "first_response_at": row[4],
            "response_hours": float(row[5]) if row[5] else None
        }
        for row in result
    ]
```

## Analytics Patterns

### Time-Series Aggregation

Ticket creation trends over time:

```python
from sqlalchemy import select, func, cast, Date

async def get_ticket_trends(
    session: AsyncSession,
    start_date: datetime,
    end_date: datetime
) -> List[Dict]:
    """Get daily ticket creation counts."""
    
    stmt = (
        select(
            cast(Ticket.created_at, Date).label("date"),
            func.count(Ticket.id).label("count"),
            func.count(
                case((Ticket.priority == "urgent", 1))
            ).label("urgent_count")
        )
        .where(
            and_(
                Ticket.created_at >= start_date,
                Ticket.created_at <= end_date,
                Ticket.deleted_at.is_(None)
            )
        )
        .group_by(cast(Ticket.created_at, Date))
        .order_by(cast(Ticket.created_at, Date).asc())
    )
    
    result = await session.execute(stmt)
    return [
        {
            "date": row[0],
            "total": row[1],
            "urgent": row[2]
        }
        for row in result
    ]
```

### Cohort Analysis

Analyze ticket resolution by cohort:

```python
async def analyze_resolution_by_cohort(
    session: AsyncSession,
    cohort_field: str = "category"
) -> List[Dict]:
    """Analyze resolution metrics by category/priority cohort."""
    
    cohort_column = getattr(Ticket, cohort_field)
    
    stmt = (
        select(
            cohort_column.label("cohort"),
            func.count(Ticket.id).label("total_tickets"),
            func.count(
                case((Ticket.status == "resolved", 1))
            ).label("resolved_count"),
            (
                func.count(case((Ticket.status == "resolved", 1))) * 100.0 /
                func.count(Ticket.id)
            ).label("resolution_rate"),
            func.avg(
                case(
                    (
                        Ticket.resolved_at.is_not(None),
                        func.extract("epoch", Ticket.resolved_at - Ticket.created_at) / 3600
                    )
                )
            ).label("avg_resolution_hours")
        )
        .where(Ticket.deleted_at.is_(None))
        .group_by(cohort_column)
        .order_by(text("total_tickets DESC"))
    )
    
    result = await session.execute(stmt)
    return [
        {
            "cohort": row[0],
            "total": row[1],
            "resolved": row[2],
            "resolution_rate": float(row[3]),
            "avg_hours": float(row[4]) if row[4] else None
        }
        for row in result
    ]
```

## Hybrid Properties and Methods

### Computed Properties with SQL Expressions

```python
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

class Ticket(Base):
    # ... existing fields ...
    
    @hybrid_property
    def is_overdue(self) -> bool:
        """Check if ticket is overdue (Python-level)."""
        if self.status in ["resolved", "closed"]:
            return False
        age_days = (datetime.utcnow() - self.created_at).days
        return age_days > 7
    
    @is_overdue.expression
    def is_overdue(cls):
        """Check if ticket is overdue (SQL-level)."""
        return and_(
            cls.status.notin_(["resolved", "closed"]),
            func.extract("day", func.now() - cls.created_at) > 7
        )
    
    @hybrid_method
    def is_escalation_needed(self, hours_threshold: int = 48) -> bool:
        """Check if escalation is needed (Python-level)."""
        if self.status != "open":
            return False
        age_hours = (datetime.utcnow() - self.created_at).total_seconds() / 3600
        return age_hours > hours_threshold
    
    @is_escalation_needed.expression
    def is_escalation_needed(cls, hours_threshold: int = 48):
        """Check if escalation is needed (SQL-level)."""
        return and_(
            cls.status == "open",
            func.extract("epoch", func.now() - cls.created_at) / 3600 > hours_threshold
        )
```

Usage in queries:

```python
# Query using hybrid property
overdue_tickets = await session.execute(
    select(Ticket).where(Ticket.is_overdue)
)

# Query using hybrid method
escalation_needed = await session.execute(
    select(Ticket).where(Ticket.is_escalation_needed(24))
)
```

## Event Listeners for Automation

### Automatic Timestamp Updates

```python
from sqlalchemy import event
from datetime import datetime

@event.listens_for(Ticket, "before_update")
def update_modified_timestamp(mapper, connection, target):
    """Automatically update updated_at on changes."""
    target.updated_at = datetime.utcnow()

@event.listens_for(Ticket, "before_update")
def set_resolved_timestamp(mapper, connection, target):
    """Set resolved_at when status changes to resolved."""
    # Check if status changed to resolved
    state = inspect(target)
    hist = state.get_history("status", passive=True)
    
    if hist.has_changes():
        old_status = hist.deleted[0] if hist.deleted else None
        new_status = hist.added[0] if hist.added else None
        
        if new_status == "resolved" and old_status != "resolved":
            target.resolved_at = datetime.utcnow()
```

### Validation on Insert

```python
@event.listens_for(Ticket, "before_insert")
@event.listens_for(Ticket, "before_update")
def validate_ticket_data(mapper, connection, target):
    """Validate ticket data before save."""
    if not target.title or len(target.title.strip()) < 5:
        raise ValueError("Ticket title must be at least 5 characters")
    
    if target.priority not in ["low", "medium", "high", "urgent"]:
        raise ValueError(f"Invalid priority: {target.priority}")
```

## Polymorphic Relationships

### Single Table Inheritance

```python
class BaseEntity(Base):
    __tablename__ = "entities"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(50))
    name: Mapped[str] = mapped_column(String(255))
    
    __mapper_args__ = {
        "polymorphic_on": entity_type,
        "polymorphic_identity": "base"
    }

class Customer(BaseEntity):
    __mapper_args__ = {
        "polymorphic_identity": "customer"
    }
    
    company_name: Mapped[Optional[str]] = mapped_column(String(255))
    industry: Mapped[Optional[str]] = mapped_column(String(100))

class Agent(BaseEntity):
    __mapper_args__ = {
        "polymorphic_identity": "agent"
    }
    
    department: Mapped[Optional[str]] = mapped_column(String(100))
    skill_level: Mapped[Optional[int]] = mapped_column(Integer)
```

### Joined Table Inheritance

```python
class Person(Base):
    __tablename__ = "persons"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    person_type: Mapped[str] = mapped_column(String(50))
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255))
    
    __mapper_args__ = {
        "polymorphic_on": person_type
    }

class Customer(Person):
    __tablename__ = "customers"
    
    id: Mapped[int] = mapped_column(ForeignKey("persons.id"), primary_key=True)
    account_type: Mapped[str] = mapped_column(String(50))
    
    __mapper_args__ = {
        "polymorphic_identity": "customer"
    }

class Agent(Person):
    __tablename__ = "agents"
    
    id: Mapped[int] = mapped_column(ForeignKey("persons.id"), primary_key=True)
    department: Mapped[str] = mapped_column(String(100))
    
    __mapper_args__ = {
        "polymorphic_identity": "agent"
    }
```

## Advanced Index Patterns

### Composite Indexes

```python
from sqlalchemy import Index

class Ticket(Base):
    __tablename__ = "tickets"
    
    # ... fields ...
    
    __table_args__ = (
        # Composite index for common query pattern
        Index("ix_ticket_status_priority", "status", "priority"),
        
        # Composite index with included columns (PostgreSQL)
        Index(
            "ix_ticket_assignee_status",
            "assignee_id",
            "status",
            postgresql_include=["created_at", "priority"]
        ),
        
        # Partial index for open tickets only
        Index(
            "ix_ticket_open",
            "created_at",
            "priority",
            postgresql_where=text("status = 'open' AND deleted_at IS NULL")
        ),
    )
```

### Expression Indexes

```python
from sqlalchemy import func, Index

class Ticket(Base):
    __tablename__ = "tickets"
    
    # ... fields ...
    
    __table_args__ = (
        # Index on lowercase email for case-insensitive search
        Index("ix_ticket_title_lower", func.lower(title)),
        
        # Index on date part for time-based queries
        Index("ix_ticket_created_date", func.date(created_at)),
    )
```

## Connection and Session Patterns

### Read Replica Configuration

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# Write engine (primary)
write_engine = create_async_engine(
    "postgresql+asyncpg://user:pass@primary.db.local/support",
    pool_size=20,
    max_overflow=40
)

# Read engine (replica)
read_engine = create_async_engine(
    "postgresql+asyncpg://user:pass@replica.db.local/support",
    pool_size=30,  # More connections for read-heavy workload
    max_overflow=60
)

# Session factories
WriteSession = async_sessionmaker(bind=write_engine, expire_on_commit=False)
ReadSession = async_sessionmaker(bind=read_engine, expire_on_commit=False)

# Usage
async def get_analytics_data():
    """Use read replica for analytics."""
    async with ReadSession() as session:
        return await session.execute(heavy_analytics_query)

async def create_ticket(data):
    """Use write engine for mutations."""
    async with WriteSession() as session:
        ticket = Ticket(**data)
        session.add(ticket)
        await session.commit()
        return ticket
```

### Custom Session with Routing

```python
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Literal

class RoutedSession:
    """Session that routes queries to appropriate database."""
    
    def __init__(self):
        self.write_factory = WriteSession
        self.read_factory = ReadSession
    
    def get_session(
        self,
        mode: Literal["read", "write"] = "read"
    ) -> AsyncSession:
        """Get session for specified mode."""
        if mode == "write":
            return self.write_factory()
        return self.read_factory()

# Usage
router = RoutedSession()

async with router.get_session("read") as session:
    # Read operations
    tickets = await session.execute(select(Ticket))

async with router.get_session("write") as session:
    # Write operations
    session.add(new_ticket)
    await session.commit()
```

---

**These patterns are production-tested in high-scale customer support systems. Use them as templates and adapt to your specific requirements.**
