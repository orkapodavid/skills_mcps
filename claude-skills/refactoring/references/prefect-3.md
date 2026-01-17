# Prefect 3.0 Refactoring Guide

Prefect 3.0 introduces transactional semantics and native async support.

## Taskification

Break code into atomic tasks based on I/O boundaries.
- **Good**: Separate "Download", "Process", "Upload".
- **Bad**: Single task for ETL.

## Async/Sync Divide

Blocking calls in `async def` tasks halt the event loop, causing heartbeat failures.

**Anti-pattern:**
```python
@task
async def unsafe_task():
    data = requests.get(url) # BLOCKS LOOP
    return data
```

**Correct Pattern:**
```python
@task
async def safe_task():
    data = await asyncio.to_thread(requests.get, url)
    return data
```

## Concurrency

- `task.submit()`: Returns a `PrefectFuture`. Use for heterogeneous tasks. Gather results with `[f.result() for f in futures]`.
- `task.map()`: Use for homogenous batch processing over an iterable.

## Persistence

Task return values must be serializable (cloudpickle). Do not return live database connections or file handles. Return metadata (paths, connection strings) instead.
