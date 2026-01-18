# Python pyodbc Guide for SQL Server

## Install
```bash
pip install pyodbc
# Linux requires msodbcsql18 driver and unixODBC
# Windows uses ODBC Driver for SQL Server
```

## Connect (Examples)
```python
import pyodbc

# SQL Authentication
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 18 for SQL Server};'
    'SERVER=server.domain,1433;DATABASE=MyDb;'
    'UID=user;PWD=secret;Encrypt=yes;TrustServerCertificate=no;'
)

# Windows Authentication (Trusted)
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 18 for SQL Server};SERVER=server.domain;DATABASE=MyDb;Trusted_Connection=yes;'
)

# DSN
conn = pyodbc.connect('DSN=MySqlServerDsn;DATABASE=MyDb')
```

## Parameterized Queries
```python
with conn.cursor() as cur:
    cur.execute('SELECT * FROM dbo.Users WHERE id = ?', (user_id,))
    rows = cur.fetchall()
```

## Transactions
```python
conn.autocommit = False
try:
    with conn.cursor() as cur:
        cur.execute('UPDATE dbo.Balance SET amount = amount - ? WHERE id = ?', (amt, src))
        cur.execute('UPDATE dbo.Balance SET amount = amount + ? WHERE id = ?', (amt, dst))
    conn.commit()
except Exception:
    conn.rollback()
    raise
```

## Bulk Insert
- Use `executemany` with fast_executemany for parameter arrays
```python
cur = conn.cursor()
cur.fast_executemany = True
cur.executemany('INSERT INTO dbo.Items (id, name) VALUES (?, ?)', data)
conn.commit()
```
- Or T-SQL `BULK INSERT` with proper format and permissions

## Timeouts and Retries
- Set `Timeout` via connection string or `cur.setinputsizes()` as needed
- Implement simple retry for transient errors (e.g., deadlocks, network)

See `scripts/connect_pyodbc.py`, `scripts/query_runner.py`, and `scripts/bulk_insert.py` for runnable examples.
