# Refactoring Patterns for Modern Python

## Pydantic V2 Migration

- **Core Changes**: See [pydantic-v2.md](references/pydantic-v2.md) for detailed migration steps, including `model_validate_json` optimization and validator refactoring.
- **Architectural Shift**: Move from loose parsing to strict Rust-backed validation.
- **Key optimizations**:
  - Replace `json.loads(...)` + `parse_obj(...)` with `model_validate_json(...)`.
  - Use `ConfigDict` instead of inner `Config` class.
  - Migrate validators to `@field_validator` and `@model_validator`.

## Prefect 3.0 Orchestration

- **Taskification**: See [prefect-3.md](references/prefect-3.md) for breaking code into atomic tasks.
- **Async Handling**: Wrap blocking calls (like `requests` or `pyodbc`) using `asyncio.to_thread`.
- **Concurrency**: Use `.submit()` for parallel execution and `.map()` for batch processing.

## Modern Networking with HTTPX

- **Migration**: See [httpx.md](references/httpx.md) for moving from `requests` to `httpx`.
- **Connection Pooling**: Use a shared `async with httpx.AsyncClient() as client` context manager.
- **HTTP/2**: Enable with `http2=True` for performance.

## Legacy Database Integration (PyODBC)

- **Blocking I/O**: See [pyodbc.md](references/pyodbc.md) for safe integration in async loops.
- **Pattern**: Isolate database operations in synchronous functions and call via `await asyncio.to_thread(...)`.

## Development Environment (Marimo)

- **Reactive Notebooks**: See [marimo.md](references/marimo.md) for using Marimo as a reproducible development and validation environment.
- **DAG Execution**: Ensure no hidden state; dependency flow must be explicit.
