---
name: refactoring
description: Modernize Python codebases using Pydantic V2, Prefect 3.0, HTTPX, Marimo, and PyODBC. Use this skill when asked to refactor legacy scripts, improve performance/reliability, or migrate to asynchronous architectures.
metadata:
  short-description: Refactor Python to modern async stack
---

# Refactoring Skill

This skill provides a comprehensive framework for modernizing legacy Python applications. It focuses on transitioning from synchronous, imperative scripts to robust, asynchronous, and observable workflows.

## When to Use

Use this skill when the user wants to:
1.  **Refactor Legacy Code**: Modernize `requests`, `pyodbc`, or script-based workflows.
2.  **Migrate Libraries**: Upgrade to Pydantic V2, Prefect 3.0, or HTTPX.
3.  **Improve Reliability**: Add retries, type safety, and observability to pipelines.
4.  **Boost Performance**: Switch to asynchronous I/O and strict Rust-based validation.

## Core Refactoring Pillars

### 1. Data Validation (Pydantic V2)
Shift from loose dictionary parsing to strict, Rust-backed models.
- **Reference**: [pydantic-v2.md](references/pydantic-v2.md)
- **Key Action**: Replace `json.loads` with `model_validate_json`. Use `ConfigDict` and `model_validator`.

### 2. Orchestration (Prefect 3.0)
Transform monolithic scripts into atomic, retriable tasks.
- **Reference**: [prefect-3.md](references/prefect-3.md)
- **Key Action**: Decorate functions with `@task`. Handle blocking I/O in async tasks using `asyncio.to_thread`.

### 3. Networking (HTTPX)
Move from blocking `requests` to non-blocking `httpx`.
- **Reference**: [httpx.md](references/httpx.md)
- **Key Action**: Use `async with httpx.AsyncClient()` for connection pooling. Enable HTTP/2.

### 4. Database Integration (PyODBC)
Integrate legacy SQL drivers safely into async loops.
- **Reference**: [pyodbc.md](references/pyodbc.md)
- **Key Action**: Isolate blocking PyODBC calls in separate threads to prevent heartbeat failures.

### 5. Development Environment (Marimo)
Ensure reproducibility and reactive development.
- **Reference**: [marimo.md](references/marimo.md)
- **Key Action**: Develop and validate async flows in Marimo notebooks before productionizing.

## Architectural Patterns

### The "Async-Safe" Wrapper Pattern
When integrating blocking legacy libraries (like PyODBC) into async Prefect flows:

```python
@task
async def safe_db_op(data):
    # Offload blocking sync function to a thread
    await asyncio.to_thread(sync_db_function, data)
```

### The "Client Lifecycle" Pattern
Efficiently manage network resources in flows:

```python
@flow
async def data_pipeline(ids):
    # Single client instance reused for all tasks
    async with httpx.AsyncClient(http2=True) as client:
        futures = [fetch_task.submit(id, client) for id in ids]
        results = [f.result() for f in futures]
```

## Resources

- **Overview**: [overview.md](references/overview.md) - Summary of the refactoring strategy.
- **Source Material**: [Source.md](Source.md) - Deep dive technical background.
