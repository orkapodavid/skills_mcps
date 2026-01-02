# Setup Guide: Python Database Patterns

This guide helps you run the examples in this skill using either a local SQLite file (simplest) or a Dockerized PostgreSQL container.

## Prerequisites

Ensure you have Python 3.10+ installed.

Install the required dependencies:

```bash
pip install sqlalchemy aiosqlite asyncpg
```

## Option 1: Quick Start (SQLite)

The easiest way to test the patterns is using SQLite, which requires no server setup.

1.  Navigate to the skill directory:
    ```bash
    cd claude-skills/python-database-patterns
    ```

2.  Run the provided demo script:
    ```bash
    python3 examples/demo.py
    ```

This script will:
*   Create a local `demo.db` file.
*   Define a `User` model.
*   Insert a user.
*   Query the user back using async SQLAlchemy.

## Option 2: PostgreSQL (via Docker)

For a production-like environment, run PostgreSQL in a container.

1.  **Start Postgres**:
    ```bash
    docker run --name pg-demo -e POSTGRES_PASSWORD=secret -e POSTGRES_DB=demo_db -p 5432:5432 -d postgres:15
    ```

2.  **Update Connection String**:
    Modify your code (or `examples/demo.py`) to use the Postgres connection string:
    ```python
    # DATABASE_URL = "sqlite+aiosqlite:///./demo.db"
    DATABASE_URL = "postgresql+asyncpg://postgres:secret@localhost:5432/demo_db"
    ```

3.  **Run the script**:
    ```bash
    python3 examples/demo.py
    ```

4.  **Cleanup**:
    ```bash
    docker stop pg-demo
    docker rm pg-demo
    ```

## Environment Variables

For security, avoid hardcoding credentials. Use environment variables in your real applications:

```python
import os
url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./default.db")
```
