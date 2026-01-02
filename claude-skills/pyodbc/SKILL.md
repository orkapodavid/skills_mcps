---
name: pyodbc-expert
description: Expert in using pyodbc library for connecting Python to ODBC databases. Use when writing Python code to interact with databases like SQL Server, PostgreSQL, MySQL, Oracle, etc. via ODBC.
---

# pyodbc Expert

You are an expert in using `pyodbc`, a Python DB-API 2.0 compliant ODBC interface.

## Quick Overview
- **Protocol**: ODBC (Open Database Connectivity)
- **Parameter Style**: `qmark` (`?` placeholders). Always bind values—never string‑interpolate.
- **Transactions**: Default is manual commit (`autocommit=False`); set `autocommit=True` when needed.
- **Performance**: `fast_executemany` can massively speed up bulk inserts on SQL Server.

## Installation & Drivers

### Install
```bash
pip install pyodbc
```
Ensure you have the correct ODBC driver for your database and OS installed (e.g., `msodbcsql18` for SQL Server, `psqlODBC` for PostgreSQL).

### Check Drivers
```python
import pyodbc
print(pyodbc.drivers())
```

## Connection Patterns

### DSN‑less (Portable)
```python
import pyodbc
# SQL Server Example
cnxn = pyodbc.connect(
    "DRIVER={ODBC Driver 18 for SQL Server};SERVER=server;DATABASE=db;UID=user;PWD=pass;TrustServerCertificate=yes",
    timeout=5,
)
```

### DSN
```python
cnxn = pyodbc.connect("DSN=my_dsn;UID=user;PWD=pass", timeout=5)
```

## Core Usage

### Parameterized Queries (qmark style)
```python
with cnxn.cursor() as cur:
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    rows = cur.fetchall()
```

### Transactions
```python
cnxn.autocommit = False    # default
with cnxn:
    with cnxn.cursor() as cur:
        cur.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (amt, from_id))
        cur.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (amt, to_id))
# exiting block commits; exceptions roll back
```

## Advanced Topics

### Fast Bulk Inserts (SQL Server)
```python
with cnxn.cursor() as cur:
    cur.fast_executemany = True
    cur.executemany("INSERT INTO t(col1, col2) VALUES (?, ?)", data_iterable)
```

### Dictionary Row Factory
```python
def dict_row(cursor, row):
    return {d[0]: v for d, v in zip(cursor.description, row)}

with cnxn.cursor() as cur:
    cur.rowfactory = dict_row
    cur.execute("SELECT * FROM users")
    result = cur.fetchall()   # list of dicts
```

## Agent Skill Design (Tool Functions)

### 1. Test Connection
```python
def test_connection(conn_str: str, timeout: int = 5) -> dict:
    try:
        with pyodbc.connect(conn_str, timeout=timeout) as cnxn:
            return {"ok": True, "message": "Success"}
    except Exception as e:
        return {"ok": False, "error": str(e)}
```

### 2. Run Query (SELECT)
```python
def run_query(conn_str: str, sql: str, params: list | tuple = ()) -> dict:
    with pyodbc.connect(conn_str) as cnxn:
        with cnxn.cursor() as cur:
            cur.execute(sql, params)
            if cur.description:
                cols = [d[0] for d in cur.description]
                rows = [dict(zip(cols, r)) for r in cur.fetchall()]
                return {"ok": True, "rows": rows, "columns": cols}
            return {"ok": True, "message": "No results"}
```

### 3. Run Non-Query (INSERT/UPDATE/DELETE)
```python
def run_non_query(conn_str: str, sql: str, params: list | tuple = ()) -> dict:
    with pyodbc.connect(conn_str) as cnxn:
        with cnxn.cursor() as cur:
            cur.execute(sql, params)
            return {"ok": True, "rowcount": cur.rowcount}
```

### 4. Run Batch (Bulk)
```python
def run_batch(conn_str: str, sql: str, rows: list[tuple], fast: bool = False) -> dict:
    with pyodbc.connect(conn_str) as cnxn:
        with cnxn.cursor() as cur:
            if fast:
                cur.fast_executemany = True
            cur.executemany(sql, rows)
            return {"ok": True, "rowcount": cur.rowcount}
```

### 5. Describe Schema
```python
def describe_schema(conn_str: str, table_name: str | None = None) -> dict:
    with pyodbc.connect(conn_str) as cnxn:
        with cnxn.cursor() as cur:
            if table_name:
                cols = [tuple(r) for r in cur.columns(table=table_name)]
                return {"ok": True, "columns": cols}
            else:
                tbls = [r.table_name for r in cur.tables(tableType='TABLE')]
                return {"ok": True, "tables": tbls}
```

## Best Practices

- **Security**: Always use parameter binding (`?`)—never string format values.
- **Resources**: Use context managers (`with`) for connections and cursors.
- **Encoding**: Defaults generally UTF‑8. Use `cnxn.setencoding` if needed.
- **Troubleshooting**: Check drivers with `pyodbc.drivers()`. Ensure architecture matches (64-bit Python needs 64-bit drivers).
