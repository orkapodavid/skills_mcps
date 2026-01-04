# pyodbc Module Reference

## Module Attributes

| Attribute | Description | Default |
|-----------|-------------|---------|
| `version` | Module version (e.g., `4.0.25`) | - |
| `apilevel` | DB API level | `2.0` |
| `lowercase` | Lowercase column names | `False` |
| `native_uuid` | Return UUID as `uuid.UUID` | `False` |
| `pooling` | ODBC connection pooling | `True` |
| `threadsafety` | `1` = threads share module, not connections | `1` |
| `paramstyle` | Parameter style (`?` markers) | `qmark` |

## connect()

```python
pyodbc.connect(connstring, autocommit=False, timeout=0, readonly=False,
               attrs_before=None, encoding='utf-16le', ansi=False, **kwargs)
```

**Keyword Conversion:**
- `host` → `server`
- `user` → `uid`  
- `password` → `pwd`

**Examples:**
```python
# SQL Server
conn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;DATABASE=mydb;UID=user;PWD=pass;Encrypt=no')

# With DSN
conn = pyodbc.connect('DSN=mydsn', autocommit=True)

# With timeout
conn = pyodbc.connect(connstring, timeout=30)
```

## Utility Functions

```python
pyodbc.drivers()        # List available drivers
pyodbc.dataSources()    # Dict of DSNs

pyodbc.DateFromTicks(ticks)       # -> datetime.date
pyodbc.TimeFromTicks(ticks)       # -> datetime.time
pyodbc.TimestampFromTicks(ticks)  # -> datetime.datetime

pyodbc.setDecimalSeparator('.')
pyodbc.getDecimalSeparator()
```
```

---

## **File 2: `pyodbc_connection.md`**

```markdown
# pyodbc Connection Reference

## Attributes

| Attribute | Description |
|-----------|-------------|
| `autocommit` | Auto-commit mode (default: `False`) |
| `timeout` | Query timeout in seconds (0 = disabled) |
| `searchescape` | ODBC search escape character |

## Methods

```python
conn.cursor()      # Create cursor
conn.commit()      # Commit transaction
conn.rollback()    # Rollback transaction
conn.close()       # Close connection

conn.execute(sql, *params)  # Convenience: creates cursor, executes, returns cursor
conn.getinfo(info_type)     # Get ODBC driver info
conn.set_attr(attr_id, value)  # Set connection attribute
```

## Encoding

```python
# For MySQL/PostgreSQL (UTF-8)
conn.setdecoding(pyodbc.SQL_CHAR, encoding='utf-8')
conn.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-8')
conn.setencoding(encoding='utf-8')
```

## Output Converters

```python
conn.add_output_converter(sqltype, func)
conn.remove_output_converter(sqltype)
conn.clear_output_converters()
conn.get_output_converter(sqltype)
```

## Context Manager

```python
with pyodbc.connect(connstring) as conn:
    conn.execute("INSERT ...")
# commit() called on exit, connection NOT closed

# To auto-close:
from contextlib import closing
with closing(pyodbc.connect(connstring)) as conn:
    pass  # Connection closed on exit
```

## Transaction Isolation

```python
conn = pyodbc.connect(connstring, autocommit=True)
conn.set_attr(pyodbc.SQL_ATTR_TXN_ISOLATION, pyodbc.SQL_TXN_SERIALIZABLE)
conn.autocommit = False
```
```

---

## **File 3: `pyodbc_cursor.md`**

```markdown
# pyodbc Cursor Reference

## Attributes

| Attribute | Description |
|-----------|-------------|
| `description` | Column metadata (name, type, size, etc.) |
| `rowcount` | Rows affected (-1 if unknown) |
| `messages` | Diagnostic messages |
| `fast_executemany` | Enable fast batch inserts |

## Execute

```python
cursor.execute(sql, *params)           # Execute with params
cursor.executemany(sql, params_seq)    # Batch execute

# Fast batch insert (SQL Server)
cursor.fast_executemany = True
cursor.executemany("INSERT INTO t VALUES (?, ?)", large_list)
```

## Fetch

```python
cursor.fetchone()       # Single row or None
cursor.fetchall()       # All rows as list
cursor.fetchmany(size)  # Up to size rows
cursor.fetchval()       # First column of first row
```

## Navigation

```python
cursor.skip(count)   # Skip rows
cursor.nextset()     # Move to next result set
```

## Schema Introspection

```python
cursor.tables(table=None, catalog=None, schema=None, tableType=None)
cursor.columns(table=None)
cursor.primaryKeys(table)
cursor.foreignKeys(table=None, foreignTable=None)
cursor.statistics(table)
cursor.procedures()
cursor.getTypeInfo(sqltype=None)
```

## Iteration

```python
for row in cursor.execute("SELECT * FROM users"):
    print(row.name)
```
```

---

## **File 4: `pyodbc_row.md`**

```markdown
# pyodbc Row Reference

## Access

```python
row = cursor.fetchone()

# By index
row[0], row[1]

# By column name
row.user_id, row.user_name

# With SQL AS
cursor.execute("SELECT COUNT(*) AS total FROM users")
row.total
```

## Features

```python
# Values can be replaced
row.timestamp = row.timestamp.replace(tzinfo=utc)

# Metadata available after cursor closed
row.cursor_description

# Picklable
import pickle
data = pickle.dumps(row)
```

**Note:** Slicing returns tuples, not Rows.
```

---

## **File 5: `pyodbc_exceptions.md`**

```markdown
# pyodbc Exceptions Reference

## Hierarchy

```
Error
└── DatabaseError
    ├── DataError        (22***)
    ├── OperationalError (HYT00, HYT01 - timeouts)
    ├── IntegrityError   (23***, 40002 - constraints)
    ├── InternalError
    ├── ProgrammingError (24***, 25***, 42*** - SQL errors)
    └── NotSupportedError (0A000)
```

## Handling

```python
try:
    cursor.execute("INSERT INTO users VALUES (?)", value)
    conn.commit()
except pyodbc.IntegrityError:
    conn.rollback()  # Constraint violation
except pyodbc.ProgrammingError:
    pass  # SQL syntax error
except pyodbc.OperationalError:
    pass  # Timeout, connection issue
```
```

---

## **File 6: `pyodbc_connections.md`**

```markdown
# pyodbc Database Connections

## SQL Server

```python
# Windows
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 18 for SQL Server};'
    'SERVER=localhost;DATABASE=mydb;'
    'UID=user;PWD=pass;Encrypt=no'
)

# Windows Auth
conn = pyodbc.connect('...;Trusted_Connection=yes')

# Linux - same driver string after installing Microsoft ODBC driver
```

## MySQL

```python
conn = pyodbc.connect(
    'DRIVER={MySQL ODBC 8.0 ANSI Driver};'  # ANSI for utf8mb4
    'SERVER=localhost;DATABASE=mydb;'
    'UID=root;PWD=pass;charset=utf8mb4'
)
conn.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-8')
conn.setencoding(encoding='utf-8')
```

## PostgreSQL

```python
conn = pyodbc.connect(
    'DRIVER={PostgreSQL Unicode};'
    'SERVER=localhost;DATABASE=mydb;'
    'UID=postgres;PWD=pass'
)
conn.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-8')
conn.setencoding(encoding='utf-8')
conn.maxwrite = 1024 * 1024 * 1024  # Fix slow writes
```

## SQLite

```python
conn = pyodbc.connect('DRIVER={SQLite3 ODBC Driver};DATABASE=mydb.sqlite')
```
```

---

## **File 7: `pyodbc_features.md`**

```markdown
# pyodbc Features Reference

## fetchval()
```python
count = cursor.execute("SELECT COUNT(*) FROM t").fetchval()
```

## fast_executemany (SQL Server)
```python
cursor.fast_executemany = True
cursor.executemany("INSERT INTO t VALUES (?, ?)", params)
```

## Column Name Access
```python
row.user_name  # Instead of row[0]
```

## Chaining
```python
row = cursor.execute("SELECT * FROM t WHERE id=?", 1).fetchone()
```

## Autocommit
```python
conn = pyodbc.connect(connstring, autocommit=True)
conn.autocommit = False  # Toggle
```

## Query Timeout
```python
conn.timeout = 30  # Seconds
```

## Lowercase Columns
```python
pyodbc.lowercase = True
```
```

---

## **File 8: `pyodbc_stored_procedures.md`**

```markdown
# pyodbc Stored Procedures

## Basic Call
```python
cursor.execute("{CALL usp_GetUser (?)}", user_id)
```

## Output Parameters (SQL Server)
```python
sql = """
SET NOCOUNT ON;
DECLARE @out NVARCHAR(100);
EXEC dbo.usp_MyProc @in=?, @out=@out OUTPUT;
SELECT @out AS result;
"""
cursor.execute(sql, input_val)
# Fetch procedure results first, then output param
```

## Return Value
```python
sql = """
SET NOCOUNT ON;
DECLARE @rv INT;
EXEC @rv = dbo.usp_MyProc;
SELECT @rv AS return_value;
"""
return_val = cursor.execute(sql).fetchval()
```

## Multiple Result Sets
```python
cursor.execute("{CALL usp_MultiResults}")
results1 = cursor.fetchall()
if cursor.nextset():
    results2 = cursor.fetchall()
```
```

---

## **File 9: `pyodbc_data_types.md`**

```markdown
# pyodbc Data Types

## Python → ODBC

| Python | ODBC |
|--------|------|
| `None` | varies |
| `bool` | BIT |
| `int` | SQL_BIGINT |
| `float` | SQL_DOUBLE |
| `Decimal` | SQL_NUMERIC |
| `str` | SQL_VARCHAR |
| `bytes` | SQL_VARBINARY |
| `datetime.date` | SQL_TYPE_DATE |
| `datetime.time` | SQL_TYPE_TIME |
| `datetime.datetime` | SQL_TYPE_TIMESTAMP |
| `uuid.UUID` | SQL_GUID |

## ODBC → Python

| ODBC | Python |
|------|--------|
| NULL | `None` |
| SQL_BIT | `bool` |
| SQL_*INT | `int` |
| SQL_FLOAT/DOUBLE | `float` |
| SQL_DECIMAL | `Decimal` |
| SQL_CHAR/WCHAR | `str` |
| SQL_BINARY | `bytes` |
| SQL_TYPE_DATE | `datetime.date` |
| SQL_TYPE_TIME | `datetime.time` |
| SQL_TIMESTAMP | `datetime.datetime` |
| SQL_GUID | `str` (or `uuid.UUID` if `native_uuid=True`) |
```