# pyodbc Agent Tools

These functions are designed to be used by an LLM agent to interact with a database. They return structured dictionaries indicating success or failure.

## 1. Test Connection
Validates that the connection string works.

```python
def test_connection(conn_str: str, timeout: int = 5) -> dict:
    try:
        with pyodbc.connect(conn_str, timeout=timeout) as cnxn:
            return {"ok": True, "message": "Success"}
    except Exception as e:
        return {"ok": False, "error": str(e)}
```

## 2. Run Query (SELECT)
Executes a read-only query and returns a list of dictionaries.

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

## 3. Run Non-Query (INSERT/UPDATE/DELETE)
Executes a modification query and returns the number of affected rows.

```python
def run_non_query(conn_str: str, sql: str, params: list | tuple = ()) -> dict:
    with pyodbc.connect(conn_str) as cnxn:
        with cnxn.cursor() as cur:
            cur.execute(sql, params)
            return {"ok": True, "rowcount": cur.rowcount}
```

## 4. Run Batch (Bulk)
Executes a bulk insert/update. Supports `fast_executemany` for SQL Server.

```python
def run_batch(conn_str: str, sql: str, rows: list[tuple], fast: bool = False) -> dict:
    with pyodbc.connect(conn_str) as cnxn:
        with cnxn.cursor() as cur:
            if fast:
                cur.fast_executemany = True
            cur.executemany(sql, rows)
            return {"ok": True, "rowcount": cur.rowcount}
```

## 5. Describe Schema
Introspects tables or columns.

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
