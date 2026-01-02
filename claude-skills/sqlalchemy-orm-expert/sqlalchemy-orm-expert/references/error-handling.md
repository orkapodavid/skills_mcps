# Error Handling Patterns for SQLAlchemy

Comprehensive error handling strategies for production customer support systems using SQLAlchemy 2.0+.

## Common SQLAlchemy Exceptions

### Import Required Exceptions

```python
from sqlalchemy.exc import (
    IntegrityError,  # Constraint violations (unique, foreign key, check)
    DataError,       # Invalid data type or value
    OperationalError,  # Database operational errors
    DatabaseError,   # Generic database errors
    InvalidRequestError,  # Invalid SQLAlchemy API usage
    NoResultFound,   # Query expected result but found none
    MultipleResultsFound,  # Query expected one result but found multiple
)
from sqlalchemy.orm.exc import (
    DetachedInstanceError,  # Instance not bound to session
    ObjectDeletedError,  # Object was deleted
)
```

## Pattern 1: CRUD Operations Error Handling

### Create with Validation

```python
from fastapi import HTTPException, status

async def create_ticket(
    session: AsyncSession,
    ticket_data: TicketCreate
) -> Ticket:
    """Create ticket with comprehensive error handling."""
    try:
        # Validate creator exists
        creator = await session.get(User, ticket_data.creator_id)
        if not creator:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {ticket_data.creator_id} not found"
            )
        
        if not creator.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User account is inactive"
            )
        
        # Create ticket
        ticket = Ticket(
            ticket_number=generate_ticket_number(),
            title=ticket_data.title,
            description=ticket_data.description,
            creator_id=ticket_data.creator_id
        )
        
        session.add(ticket)
        await session.commit()
        await session.refresh(ticket)
        
        return ticket
        
    except IntegrityError as e:
        await session.rollback()
        
        # Handle specific constraint violations
        if "unique constraint" in str(e.orig):
            if "ticket_number" in str(e.orig):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Ticket number already exists. Retry with new number."
                )
        
        if "foreign key constraint" in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reference to related entity"
            )
        
        # Generic integrity error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data integrity violation"
        )
    
    except DataError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid data format: {str(e.orig)}"
        )
    
    except OperationalError as e:
        await session.rollback()
        
        # Check for specific database errors
        if "timeout" in str(e.orig).lower():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database timeout. Please try again."
            )
        
        if "connection" in str(e.orig).lower():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection error"
            )
        
        # Generic operational error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed"
        )
    
    except Exception as e:
        await session.rollback()
        # Log the full error for debugging
        logger.error(f"Unexpected error creating ticket: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
```

### Read with Not Found Handling

```python
async def get_ticket_by_id(
    session: AsyncSession,
    ticket_id: int
) -> Ticket:
    """Get ticket with proper not-found handling."""
    try:
        # Use get() for primary key lookup
        ticket = await session.get(Ticket, ticket_id)
        
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ticket {ticket_id} not found"
            )
        
        # Check soft delete
        if ticket.deleted_at:
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail=f"Ticket {ticket_id} has been deleted"
            )
        
        return ticket
        
    except DetachedInstanceError:
        # Instance was detached from session
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Session error. Please try again."
        )
    
    except OperationalError as e:
        if "timeout" in str(e.orig).lower():
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Query timeout"
            )
        raise

async def get_ticket_by_number(
    session: AsyncSession,
    ticket_number: str
) -> Ticket:
    """Get ticket by unique field with error handling."""
    try:
        stmt = select(Ticket).where(Ticket.ticket_number == ticket_number)
        result = await session.execute(stmt)
        
        # Use scalar_one() for expected single result
        ticket = result.scalar_one()
        
        return ticket
        
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket {ticket_number} not found"
        )
    
    except MultipleResultsFound:
        # Should never happen with unique constraint
        logger.error(f"Multiple tickets found for number {ticket_number}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Data integrity error"
        )
```

### Update with Optimistic Locking

```python
async def update_ticket_status(
    session: AsyncSession,
    ticket_id: int,
    new_status: str,
    expected_version: int
) -> Ticket:
    """Update with optimistic locking to prevent concurrent modification."""
    try:
        # Load ticket with version check
        stmt = (
            select(Ticket)
            .where(
                and_(
                    Ticket.id == ticket_id,
                    Ticket.version == expected_version,
                    Ticket.deleted_at.is_(None)
                )
            )
            .with_for_update()  # Lock row for update
        )
        result = await session.execute(stmt)
        ticket = result.scalar_one_or_none()
        
        if not ticket:
            # Check if ticket exists but version mismatch
            existing = await session.get(Ticket, ticket_id)
            if not existing or existing.deleted_at:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Ticket {ticket_id} not found"
                )
            
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ticket was modified by another user. Please refresh and try again."
            )
        
        # Perform update
        ticket.status = new_status
        ticket.version += 1
        
        await session.commit()
        await session.refresh(ticket)
        
        return ticket
        
    except OperationalError as e:
        await session.rollback()
        
        if "deadlock" in str(e.orig).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Concurrent modification detected. Please retry."
            )
        
        raise
```

### Delete with Cascade Handling

```python
async def delete_ticket(
    session: AsyncSession,
    ticket_id: int,
    hard_delete: bool = False
) -> Dict[str, Any]:
    """Delete ticket with soft delete support."""
    try:
        ticket = await session.get(Ticket, ticket_id)
        
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ticket {ticket_id} not found"
            )
        
        if hard_delete:
            # Hard delete - will cascade to comments, attachments
            await session.delete(ticket)
            await session.commit()
            
            return {
                "deleted": True,
                "hard_delete": True,
                "ticket_id": ticket_id
            }
        else:
            # Soft delete
            ticket.deleted_at = datetime.utcnow()
            await session.commit()
            
            return {
                "deleted": True,
                "hard_delete": False,
                "ticket_id": ticket_id,
                "can_restore": True
            }
        
    except IntegrityError as e:
        await session.rollback()
        
        if "foreign key constraint" in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot delete ticket: related records exist"
            )
        
        raise
    
    except ObjectDeletedError:
        # Object was already deleted
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail=f"Ticket {ticket_id} was already deleted"
        )
```

## Pattern 2: Transaction Error Handling

### Multi-Operation Transaction

```python
async def transfer_ticket_ownership(
    session: AsyncSession,
    ticket_id: int,
    new_owner_id: int,
    reason: str
) -> Dict[str, Any]:
    """Transfer ticket with transaction rollback on any error."""
    savepoint = None
    
    try:
        # Create savepoint for nested transaction
        savepoint = await session.begin_nested()
        
        # Step 1: Load and validate ticket
        ticket = await session.get(Ticket, ticket_id)
        if not ticket:
            raise ValueError(f"Ticket {ticket_id} not found")
        
        # Step 2: Load and validate new owner
        new_owner = await session.get(User, new_owner_id)
        if not new_owner or not new_owner.is_active:
            raise ValueError(f"Invalid new owner {new_owner_id}")
        
        # Step 3: Store old owner for audit
        old_owner_id = ticket.creator_id
        
        # Step 4: Update ticket
        ticket.creator_id = new_owner_id
        
        # Step 5: Create audit log
        audit_log = AuditLog(
            table_name="tickets",
            record_id=ticket_id,
            action="TRANSFER_OWNERSHIP",
            changes={
                "old_owner_id": old_owner_id,
                "new_owner_id": new_owner_id,
                "reason": reason
            }
        )
        session.add(audit_log)
        
        # Step 6: Create notification
        notification = Notification(
            user_id=new_owner_id,
            type="ticket_assigned",
            message=f"Ticket {ticket.ticket_number} assigned to you"
        )
        session.add(notification)
        
        # Commit all changes atomically
        await session.commit()
        
        return {
            "success": True,
            "ticket_id": ticket_id,
            "old_owner_id": old_owner_id,
            "new_owner_id": new_owner_id
        }
        
    except ValueError as e:
        # Business logic validation error
        if savepoint:
            await savepoint.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except IntegrityError as e:
        if savepoint:
            await savepoint.rollback()
        
        logger.error(f"Integrity error in transfer: {e}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Data integrity violation during transfer"
        )
    
    except Exception as e:
        if savepoint:
            await savepoint.rollback()
        
        logger.error(f"Unexpected error in transfer: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Transfer failed"
        )
```

## Pattern 3: Connection and Session Errors

### Connection Pool Exhaustion

```python
from sqlalchemy.pool import QueuePool
from contextlib import asynccontextmanager

class DatabaseSessionManager:
    """Manage database sessions with connection pool monitoring."""
    
    def __init__(self, engine):
        self.engine = engine
        self.session_factory = async_sessionmaker(
            bind=engine,
            expire_on_commit=False
        )
    
    @asynccontextmanager
    async def session(self):
        """Get session with pool exhaustion handling."""
        session = self.session_factory()
        
        try:
            yield session
            await session.commit()
        
        except OperationalError as e:
            await session.rollback()
            
            # Check for pool exhaustion
            if "QueuePool limit" in str(e):
                logger.error("Connection pool exhausted")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Service temporarily unavailable. Too many concurrent requests."
                )
            
            # Check for connection timeout
            if "timeout" in str(e.orig).lower():
                logger.warning("Database connection timeout")
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail="Database connection timeout"
                )
            
            raise
        
        except Exception as e:
            await session.rollback()
            raise
        
        finally:
            await session.close()
    
    def get_pool_status(self) -> Dict[str, int]:
        """Get current connection pool statistics."""
        pool = self.engine.pool
        return {
            "size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "total": pool.size() + pool.overflow()
        }
```

### Stale Connection Recovery

```python
from sqlalchemy.exc import DBAPIError

async def execute_with_retry(
    session: AsyncSession,
    stmt,
    max_retries: int = 3
):
    """Execute query with automatic retry on stale connection."""
    
    for attempt in range(max_retries):
        try:
            result = await session.execute(stmt)
            return result
        
        except OperationalError as e:
            # Check if connection was lost
            if "connection" in str(e.orig).lower() and attempt < max_retries - 1:
                logger.warning(f"Connection lost, retrying (attempt {attempt + 1}/{max_retries})")
                
                # Rollback and start fresh
                await session.rollback()
                
                # Wait before retry (exponential backoff)
                await asyncio.sleep(2 ** attempt)
                continue
            
            # Max retries reached or different error
            raise
        
        except DBAPIError as e:
            # DBAPI-level error
            if e.connection_invalidated and attempt < max_retries - 1:
                logger.warning("Connection invalidated, retrying")
                await session.rollback()
                await asyncio.sleep(2 ** attempt)
                continue
            
            raise
```

## Pattern 4: Validation and Business Logic Errors

### Custom Validation Decorators

```python
from functools import wraps
from typing import Callable

def validate_session(func: Callable):
    """Decorator to validate session state."""
    @wraps(func)
    async def wrapper(session: AsyncSession, *args, **kwargs):
        if not session.is_active:
            raise InvalidRequestError("Session is not active")
        
        if session.in_transaction():
            logger.warning(f"{func.__name__} called within existing transaction")
        
        return await func(session, *args, **kwargs)
    
    return wrapper

def validate_entity(model_class):
    """Decorator to validate entity before database operation."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(session: AsyncSession, entity_id: int, *args, **kwargs):
            entity = await session.get(model_class, entity_id)
            
            if not entity:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"{model_class.__name__} {entity_id} not found"
                )
            
            # Check soft delete
            if hasattr(entity, "deleted_at") and entity.deleted_at:
                raise HTTPException(
                    status_code=status.HTTP_410_GONE,
                    detail=f"{model_class.__name__} {entity_id} was deleted"
                )
            
            return await func(session, entity, *args, **kwargs)
        
        return wrapper
    
    return decorator

# Usage
@validate_session
@validate_entity(Ticket)
async def close_ticket(
    session: AsyncSession,
    ticket: Ticket,  # Will be loaded and validated by decorator
    resolution: str
) -> Ticket:
    """Close ticket with automatic validation."""
    ticket.status = "closed"
    ticket.resolved_at = datetime.utcnow()
    ticket.resolution = resolution
    
    await session.commit()
    return ticket
```

## Pattern 5: Logging and Monitoring

### Query Performance Monitoring

```python
import time
from contextlib import contextmanager

@contextmanager
def monitor_query(operation: str, threshold_ms: float = 100):
    """Monitor query execution time and log slow queries."""
    start = time.time()
    
    try:
        yield
    finally:
        duration_ms = (time.time() - start) * 1000
        
        if duration_ms > threshold_ms:
            logger.warning(
                f"Slow query detected",
                extra={
                    "operation": operation,
                    "duration_ms": duration_ms,
                    "threshold_ms": threshold_ms
                }
            )
        else:
            logger.debug(
                f"Query completed",
                extra={
                    "operation": operation,
                    "duration_ms": duration_ms
                }
            )

# Usage
async def get_tickets(session: AsyncSession):
    with monitor_query("get_tickets"):
        result = await session.execute(select(Ticket))
        return result.scalars().all()
```

### Error Aggregation for Alerting

```python
from collections import defaultdict
from datetime import datetime, timedelta

class ErrorTracker:
    """Track database errors for alerting."""
    
    def __init__(self):
        self.errors = defaultdict(list)
        self.window_minutes = 5
    
    def record_error(self, error_type: str, details: str):
        """Record an error occurrence."""
        self.errors[error_type].append({
            "timestamp": datetime.utcnow(),
            "details": details
        })
        
        # Clean old errors
        self._cleanup_old_errors()
        
        # Check if alert threshold exceeded
        self._check_alert_threshold(error_type)
    
    def _cleanup_old_errors(self):
        """Remove errors outside time window."""
        cutoff = datetime.utcnow() - timedelta(minutes=self.window_minutes)
        
        for error_type in list(self.errors.keys()):
            self.errors[error_type] = [
                e for e in self.errors[error_type]
                if e["timestamp"] > cutoff
            ]
            
            if not self.errors[error_type]:
                del self.errors[error_type]
    
    def _check_alert_threshold(self, error_type: str):
        """Alert if error rate exceeds threshold."""
        count = len(self.errors[error_type])
        
        if count >= 10:  # 10 errors in 5 minutes
            logger.critical(
                f"High error rate detected",
                extra={
                    "error_type": error_type,
                    "count": count,
                    "window_minutes": self.window_minutes
                }
            )
            
            # Send alert (implement your alerting logic)
            send_alert(f"Database error spike: {error_type}")

# Global error tracker
error_tracker = ErrorTracker()

# Use in exception handlers
except OperationalError as e:
    error_tracker.record_error("OperationalError", str(e))
    # ... handle error
```

---

**Follow these patterns to build resilient customer support systems that handle errors gracefully and provide clear feedback to users and operators.**
