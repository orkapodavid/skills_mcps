# PyODBC and Async Integration

PyODBC is blocking. It must be isolated from the async event loop.

## The Thread Offloading Pattern

Wrap all synchronous DB operations in a function and call via `asyncio.to_thread`.

```python
import pyodbc
import asyncio

def _sync_write(records):
    conn = pyodbc.connect("DSN=...")
    cursor = conn.cursor()
    # ... operations ...
    conn.commit()

@task
async def write_to_db(records):
    await asyncio.to_thread(_sync_write, records)
```

## Connection Pooling

PyODBC connections are not thread-safe. Use application-level pooling (e.g., SQLAlchemy `QueuePool`) or create fresh connections in the worker thread scope.
