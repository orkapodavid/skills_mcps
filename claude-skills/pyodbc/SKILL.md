---
name: pyodbc-expert
description: This skill should be used when the user asks to "connect to SQL Server using Python", "use pyodbc", "fix ODBC errors", "write database tools in Python", or "perform bulk inserts with pyodbc".
---

# pyodbc Expert

This skill provides expertise in using the `pyodbc` library for Python database connectivity.

## Core Usage

### Installation
Install via pip. Ensure ODBC drivers are installed for your OS/Database.
```bash
pip install pyodbc
```
Check drivers: `print(pyodbc.drivers())`.

### Connection Pattern
Use a connection string with `pyodbc.connect()`. Always use a context manager to ensure connections are closed.

```python
import pyodbc
# DSN-less example (Recommended)
conn_str = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=...;UID=...;PWD=..."
with pyodbc.connect(conn_str) as cnxn:
    # Use connection
    pass
```

### Executing Queries
Use cursors for execution. Always use **parameter binding** (`?`) to prevent SQL injection.

```python
with cnxn.cursor() as cur:
    # SELECT
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()

    # INSERT/UPDATE
    cur.execute("UPDATE users SET name = ? WHERE id = ?", (new_name, user_id))
    # Transaction is committed automatically when exiting the connection block
```

## Best Practices

1.  **Security**: Never string-format SQL queries. Always use `?` placeholders.
2.  **Transactions**: `pyodbc` defaults to `autocommit=False`. Use `with cnxn:` to manage transactions automatically (commit on exit, rollback on error).
3.  **Performance**: Use `fast_executemany = True` for bulk inserts on SQL Server.

## Additional Resources

### Reference Files
- **`references/patterns.md`** - Connection strings for various DBs (PostgreSQL, MySQL, Oracle), advanced performance tips (`fast_executemany`), and Unicode handling.
- **`references/agent-tools.md`** - Ready-to-use Python functions (`test_connection`, `run_query`) for building AI agents.

### Examples
- **`examples/demo.py`** - A complete, runnable script demonstrating connection, table creation, parameterized insertion, and querying.
