# pyodbc Patterns and Advanced Topics

## Connection Strings

### SQL Server
**Standard (Local/Network):**
```text
DRIVER={ODBC Driver 18 for SQL Server};SERVER=myserver;DATABASE=mydb;UID=user;PWD=pass;Encrypt=yes;TrustServerCertificate=no
```
**Windows Authentication (Trusted Connection):**
```text
DRIVER={ODBC Driver 18 for SQL Server};SERVER=myserver;DATABASE=mydb;Trusted_Connection=yes
```

### PostgreSQL
```text
DRIVER={PostgreSQL Unicode};SERVER=host;PORT=5432;DATABASE=db;UID=user;PWD=pass
```

### MySQL
```text
DRIVER={MySQL ODBC 8.0 Unicode Driver};SERVER=host;PORT=3306;DATABASE=db;USER=user;PASSWORD=pass
```

### Oracle
```text
DRIVER={Oracle in instantclient_21_12};DBQ=//host:1521/service;UID=user;PWD=pass
```

## Advanced Performance

### fast_executemany (SQL Server)
For bulk inserts, `fast_executemany` sends data in batches rather than row-by-row.
```python
with cnxn.cursor() as cur:
    cur.fast_executemany = True
    # data_iterable is a list of tuples
    cur.executemany("INSERT INTO t(c1, c2) VALUES (?, ?)", data_iterable)
```
*Note:* Requires Microsoft ODBC Driver for SQL Server.

## Unicode Handling
Adjust encoding if you encounter character set issues (e.g., typically with older drivers or specific collations).
```python
# Force UTF-8
cnxn.setencoding(encoding='utf-8')
cnxn.setdecoding(pyodbc.SQL_CHAR, encoding='utf-8')
cnxn.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-8')
```

## Troubleshooting

1. **Architecture Mismatch**:
   - Error: `[IM002] [Microsoft][ODBC Driver Manager] Data source name not found and no default driver specified`
   - Cause: Mixing 32-bit Python with 64-bit Drivers (or vice-versa).
   - Fix: Ensure `python -c "import struct; print(struct.calcsize('P') * 8)"` matches your driver architecture.

2. **Driver Not Found**:
   - Check `pyodbc.drivers()` to see the exact name installed on the system. It must match the `DRIVER={...}` string exactly.

3. **Mac/Linux Headers**:
   - Install `unixodbc-dev` (Linux) or `unixodbc` (macOS) before installing `pyodbc` via pip.
