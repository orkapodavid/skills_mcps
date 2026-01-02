# pyodbc Wiki Summary for Database Agent Implementation

## 1. Installation Requirements & Setup
- **Python Versions:** Supports Python 3.x (and older 2.7).
- **OS Support:** Windows, Linux, macOS.
- **Dependencies:** 
  - Windows: Typically uses pre-compiled wheels.
  - Linux/macOS: Requires `unixODBC` development headers (`unixodbc-dev` on Debian/Ubuntu, `unixODBC-devel` on RedHat/CentOS).
- **Major Databases & Drivers:**
  - **SQL Server:** Microsoft ODBC Driver for SQL Server (e.g., version 17 or 18).
  - **PostgreSQL:** PostgreSQL ODBC driver (`psqlODBC`).
  - **MySQL:** MySQL Connector/ODBC.
  - **Oracle:** Oracle Instant Client + Oracle ODBC Driver. Requires setting `LD_LIBRARY_PATH` and `TNS_ADMIN` on Linux.
  - **SQLite:** SQLite ODBC driver (less common as `sqlite3` is built-in, but possible via pyodbc).

## 2. Basic Usage
- **Connecting:** `cnxn = pyodbc.connect('DRIVER={...};SERVER=...;DATABASE=...;UID=...;PWD=...')`
- **Connection Strings:** Can be DSN-based (`DSN=my_dsn;UID=...`) or DSN-less (full driver details).
- **Executing Queries:** `cursor = cnxn.cursor(); cursor.execute("SELECT * FROM table WHERE col = ?", param)`
- **Parameters:** Uses `?` as the placeholder (qmark style). Named parameters are NOT natively supported in the SQL string.
- **Fetching Results:** `cursor.fetchone()`, `cursor.fetchall()`, `cursor.fetchmany(size)`.
- **Transactions:** Handled at Connection level. `cnxn.commit()`, `cnxn.rollback()`.
- **Cursor Behavior:** Cursors are not isolated; changes in one are visible to others on the same connection.

## 3. Advanced Topics
- **Unicode/Encoding:** Use `cnxn.setencoding()` and `cnxn.setdecoding()` to handle non-UTF-8 databases.
- **fast_executemany:** `cursor.fast_executemany = True`. Significantly speeds up `executemany()` for SQL Server. Requires specific drivers (Microsoft ODBC Driver for SQL Server).
- **Data Types:** pyodbc maps ODBC types to Python types (e.g., SQL_VARCHAR to `str`, SQL_DECIMAL to `decimal.Decimal`).
- **Rowfactory:** Can be implemented by assigning a callable to `cursor.row_factory`. Useful for returning dicts or namedtuples.
- **Autocommit:** `cnxn.autocommit = True`. Defaults to `False` (per DB-API 2.0).
- **Timeout:** `cnxn.timeout = seconds` (for queries). Connection timeout is set in `connect(..., timeout=X)`.
- **Error Handling:** Base class `pyodbc.Error`. Specific ones: `ProgrammingError`, `OperationalError`, `IntegrityError`, `DataError`.
- **Context Managers:** `with pyodbc.connect(...) as cnxn:` (commits on exit if no error, rolls back otherwise). `with cnxn.cursor() as crsr:`.
- **Arraysize:** `cursor.arraysize` controls how many rows `fetchmany()` retrieves by default.

## 4. Driver-Specific Notes
- **SQL Server (Linux):** Requires Microsoft's repository and `msodbcsql17` or `msodbcsql18` packages.
- **PostgreSQL:** Use `Driver={PostgreSQL Unicode}`. Be wary of case sensitivity in table names.
- **MySQL:** `Driver={MySQL ODBC 8.0 Unicode Driver}`. Note different connection string keys (`PORT` vs `SERVER`).

## 5. Troubleshooting
- **Missing Drivers:** `pyodbc.drivers()` returns a list of available driver names.
- **DSN vs Connection String:** Connection strings are more portable for scripts; DSNs require system-level configuration (`odbc.ini`).
- **Architecture Mismatch:** 64-bit Python requires 64-bit ODBC drivers.

## 6. Security Considerations
- **SQL Injection:** Always use `?` placeholders. **Never** use f-strings or `.format()` to inject variables into SQL.
- **Credentials:** Avoid hardcoding. Use environment variables or secret managers. Use `Trusted_Connection=yes` (Windows) or `Authentication=ActiveDirectoryIntegrated` where possible.

## 7. Useful Snippets for Agent Actions

### Test Connection
```python
import pyodbc
def test_connection(conn_str):
    try:
        with pyodbc.connect(conn_str, timeout=5) as cnxn:
            return True, "Success"
    except Exception as e:
        return False, str(e)
```

### Run Query (SELECT)
```python
def run_query(cnxn, sql, params=()):
    with cnxn.cursor() as cursor:
        cursor.execute(sql, params)
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
```

### Run Non-Query (INSERT/UPDATE/DELETE)
```python
def run_non_query(cnxn, sql, params=()):
    with cnxn.cursor() as cursor:
        cursor.execute(sql, params)
        return cursor.rowcount
```

### Describe Schema
```python
def describe_schema(cnxn, table_name=None):
    with cnxn.cursor() as cursor:
        if table_name:
            return [tuple(row) for row in cursor.columns(table=table_name)]
        else:
            return [row.table_name for row in cursor.tables(tableType='TABLE')]
```

## Referenced URLs
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
