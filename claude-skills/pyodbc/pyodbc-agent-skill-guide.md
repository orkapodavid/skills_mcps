# pyodbc Agent Skill Guide for LLM Coders

## Purpose
A practical Markdown guide to help an LLM coder implement a robust database “agent skill” using `pyodbc`. It covers installation, cross‑DB driver setup, safe query execution, transactions, performance, Unicode, error handling, and ready‑to‑use function patterns suitable for LLM tool calls.

> Source: Official pyodbc GitHub Wiki (see References)

---

## Quick Overview
- `pyodbc` is a Python DB-API 2.0 compliant ODBC interface.
- Works across Windows/Linux/macOS with appropriate ODBC drivers.
- Parameter style is `qmark` (`?` placeholders). Always bind values—never string‑interpolate.
- Transactions default to manual commit (`autocommit=False`); set `autocommit=True` when needed.
- Performance: `fast_executemany` can massively speed up bulk inserts on SQL Server.

---

## Prerequisites & Installation

### Python & OS
- Python 3.x supported (legacy 2.7 also historically mentioned).
- OS: Windows, Linux, macOS.

### System Dependencies
- Windows: Typically uses precompiled wheels; just `pip install pyodbc` (ensure proper Visual C++ runtime when needed).
- Linux/macOS: Requires ODBC headers/libraries.
  - Debian/Ubuntu: `sudo apt-get install -y unixodbc unixodbc-dev`
  - RHEL/CentOS/Fedora: `sudo yum install -y unixODBC unixODBC-devel`
  - macOS (Homebrew): `brew install unixodbc`

### Install pyodbc
```bash
pip install pyodbc
```

---

## Driver Setup by Database

> Ensure 64‑bit Python uses 64‑bit ODBC drivers.

- SQL Server:
  - Windows: Microsoft ODBC Driver for SQL Server (e.g., 17/18).
  - Linux: Install `msodbcsql17` or `msodbcsql18` via Microsoft repo.
- PostgreSQL: `psqlODBC` (PostgreSQL Unicode driver).
- MySQL: MySQL Connector/ODBC (e.g., 8.0 Unicode).
- Oracle: Oracle Instant Client + Oracle ODBC driver. On Linux, configure `LD_LIBRARY_PATH`, optionally `TNS_ADMIN`.
- SQLite: SQLite ODBC driver (often you may prefer Python’s `sqlite3`, but ODBC is possible).

List installed drivers in Python:
```python
import pyodbc
print(pyodbc.drivers())
```

---

## Connection Patterns

### DSN‑less (common for scripts)
```python
import pyodbc
cnxn = pyodbc.connect(
    "DRIVER={ODBC Driver 18 for SQL Server};SERVER=server;DATABASE=db;UID=user;PWD=pass;TrustServerCertificate=yes",
    timeout=5,
)
```

### DSN
```python
cnxn = pyodbc.connect("DSN=my_dsn;UID=user;PWD=pass", timeout=5)
```

### Typical Examples
- SQL Server:
  ```text
  DRIVER={ODBC Driver 18 for SQL Server};SERVER=host,1433;DATABASE=db;UID=user;PWD=pass;Encrypt=yes;TrustServerCertificate=no
  ```
- PostgreSQL:
  ```text
  DRIVER={PostgreSQL Unicode};SERVER=host;PORT=5432;DATABASE=db;UID=user;PWD=pass
  ```
- MySQL:
  ```text
  DRIVER={MySQL ODBC 8.0 Unicode Driver};SERVER=host;PORT=3306;DATABASE=db;USER=user;PASSWORD=pass
  ```
- Oracle:
  ```text
  DRIVER={Oracle in instantclient_21_12};DBQ=//host:1521/service;UID=user;PWD=pass
  ```

---

## Core Usage

### Parameterized Queries (qmark style)
```python
with cnxn.cursor() as cur:
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    rows = cur.fetchall()
```

### Fetching Results
```python
row = cur.fetchone()       # single row or None
rows = cur.fetchall()      # list of rows
rows = cur.fetchmany(100)  # up to arraysize
```

### Transactions
```python
cnxn.autocommit = False    # default per DB-API
with cnxn:
    with cnxn.cursor() as cur:
        cur.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (amt, from_id))
        cur.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (amt, to_id))
# exiting the with cnxn block commits; exceptions roll back
```

### Cursor Notes
- Cursors share the same connection state; changes in one are visible to others.
- Use context manager (`with cnxn.cursor() as cur:`) to ensure proper cleanup.

---

## Advanced Topics

### Unicode & Encoding
- Defaults generally UTF‑8; but you can adjust:
```python
cnxn.setencoding(encoding='utf-8')
cnxn.setdecoding(pyodbc.SQL_CHAR, encoding='utf-8')
cnxn.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-8')
```

### Performance: fast_executemany (SQL Server)
```python
with cnxn.cursor() as cur:
    cur.fast_executemany = True
    cur.executemany("INSERT INTO t(col1, col2) VALUES (?, ?)", data_iterable)
```
> Requires Microsoft ODBC Driver; huge speedup for bulk insert.

### Row Factory (structured results)
```python
def dict_row(cursor, row):
    return {d[0]: v for d, v in zip(cursor.description, row)}

with cnxn.cursor() as cur:
    cur.rowfactory = dict_row
    cur.execute("SELECT * FROM users")
    result = cur.fetchall()   # list of dicts
```

### Timeouts
- Connection timeout: `pyodbc.connect(..., timeout=5)`
- Query timeout (per connection): `cnxn.timeout = 30`

### Arraysize
- `cursor.arraysize` controls default fetch batch size for `fetchmany()`.

### Autocommit
- `cnxn.autocommit = True` if you prefer auto‑committed operations.

### Exceptions
- Base: `pyodbc.Error`. Common subclasses: `ProgrammingError`, `OperationalError`, `IntegrityError`, `DataError`.

---

## Security Best Practices
- Always use parameter binding (`?`)—never string format values into SQL.
- Avoid hardcoding credentials. Use env variables or secret managers.
- Prefer integrated/managed auth when available (e.g., `Trusted_Connection` on Windows, Azure AD).
- Limit permissions of the DB user used by the agent.

---

## Troubleshooting Checklist
- Missing driver: `pyodbc.drivers()` must show your driver name.
- DSN vs DSN‑less: DSNs require `odbc.ini`/system config; DSN‑less is portable.
- Architecture: 64‑bit Python must use 64‑bit ODBC driver.
- Case sensitivity: PostgreSQL table/column names may be case‑sensitive.
- Network/SSL: Ensure proper `Encrypt`, CA certs, and port.

---

## Agent Skill Design (LLM Tool Functions)

Design the agent skill as a set of callable tools the LLM can invoke. Keep inputs minimal and explicit; return safe, structured outputs.

### 1) test_connection
Purpose: Validate a connection string.
```python
import pyodbc

def test_connection(conn_str: str, timeout: int = 5) -> dict:
    try:
        with pyodbc.connect(conn_str, timeout=timeout) as cnxn:
            return {"ok": True, "message": "Success"}
    except Exception as e:
        return {"ok": False, "error": str(e)}
```

### 2) run_query (SELECT)
Purpose: Execute read‑only queries; return rows as list of dicts.
```python
import pyodbc

def run_query(conn_str: str, sql: str, params: list | tuple = ()) -> dict:
    with pyodbc.connect(conn_str) as cnxn:
        with cnxn.cursor() as cur:
            cur.execute(sql, params)
            cols = [d[0] for d in cur.description]
            rows = [dict(zip(cols, r)) for r in cur.fetchall()]
            return {"ok": True, "rows": rows, "columns": cols}
```

### 3) run_non_query (INSERT/UPDATE/DELETE)
Purpose: Execute mutation queries; return affected rowcount.
```python
def run_non_query(conn_str: str, sql: str, params: list | tuple = ()) -> dict:
    with pyodbc.connect(conn_str) as cnxn:
        with cnxn.cursor() as cur:
            cur.execute(sql, params)
            return {"ok": True, "rowcount": cur.rowcount}
```

### 4) run_batch (bulk insert/update)
Purpose: Use `executemany`; optionally enable `fast_executemany` for SQL Server.
```python
def run_batch(conn_str: str, sql: str, rows: list[tuple], fast: bool = False) -> dict:
    with pyodbc.connect(conn_str) as cnxn:
        with cnxn.cursor() as cur:
            if fast:
                cur.fast_executemany = True
            cur.executemany(sql, rows)
            return {"ok": True, "rowcount": cur.rowcount}
```

### 5) describe_schema (tables/columns)
Purpose: Inspect tables or columns.
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

### Tool Input Validation Tips
- Validate `sql` (e.g., only allow `SELECT` for `run_query` if you want read‑only safety).
- Enforce parameter types and lengths; reject overly long inputs.
- Never attempt to parse user‑provided identifiers without strict rules.

### Return Format
- Prefer JSON‑serializable dicts with `ok: bool`, `data` fields, and `error` messages when applicable.

---

## Testing & QA
- Unit tests: Mock connections or use a test DB; verify parameter binding, row shape, and error propagation.
- Load tests: Measure `run_batch` with and without `fast_executemany` (SQL Server).
- Unicode tests: Insert/fetch non‑ASCII text; verify encoding.
- Transaction tests: Ensure rollback on exceptions.

---

## References (pyodbc Wiki)
- https://github.com/mkleehammer/pyodbc/wiki
- https://github.com/mkleehammer/pyodbc/wiki/Install
- https://github.com/mkleehammer/pyodbc/wiki/Getting-started
- https://github.com/mkleehammer/pyodbc/wiki/Connection
- https://github.com/mkleehammer/pyodbc/wiki/Cursor
- https://github.com/mkleehammer/pyodbc/wiki/Binding-Parameters
- https://github.com/mkleehammer/pyodbc/wiki/Unicode
- https://github.com/mkleehammer/pyodbc/wiki/Exceptions
- https://github.com/mkleehammer/pyodbc/wiki/fast_executemany-support-for-various-ODBC-drivers
- https://github.com/mkleehammer/pyodbc/wiki/Connecting-to-SQL-Server-from-Linux
- https://github.com/mkleehammer/pyodbc/wiki/Connecting-to-PostgreSQL
- https://github.com/mkleehammer/pyodbc/wiki/Connecting-to-MySQL
- https://github.com/mkleehammer/pyodbc/wiki/Connecting-to-Oracle-from-RHEL-or-Centos
