# T-SQL Cheatsheet (SQL Server)

## Query Patterns
- Filtering: `SELECT cols FROM dbo.Table WITH (INDEX(idx_name)) WHERE predicate;`
- Window functions: `ROW_NUMBER()`, `LAG()`, `LEAD()`, `SUM() OVER (PARTITION BY ... ORDER BY ...)`
- CTEs: `WITH cte AS (...) SELECT ... FROM cte;`
- Upserts:
  - MERGE (caution about concurrency)
  - Pattern: Try-Update then Insert
    ```sql
    UPDATE t SET ... FROM dbo.Table t WITH (UPDLOCK, HOLDLOCK) WHERE key = @key;
    IF @@ROWCOUNT = 0 INSERT dbo.Table(...)
    VALUES (...);
    ```
- Pagination: `OFFSET @skip ROWS FETCH NEXT @take ROWS ONLY`
- JSON: `OPENJSON`, `JSON_VALUE`, `JSON_QUERY`
- Temporal tables: `FOR SYSTEM_TIME AS OF @ts`

## Indexing
- Prefer clustered index on stable, narrow key.
- Include columns to cover queries; avoid over-wide keys.
- Use filtered indexes for selective predicates.
- Maintain with `ALTER INDEX ... REORGANIZE/REBUILD` and `UPDATE STATISTICS`.

## Isolation & Concurrency
- Default: READ COMMITTED
- RCSI: `ALTER DATABASE db SET READ_COMMITTED_SNAPSHOT ON;`
- Snapshot: `SET TRANSACTION ISOLATION LEVEL SNAPSHOT;`
- Lock hints sparingly; prefer query rewrites or indexing.

## DMVs for Diagnostics
- Wait stats: `sys.dm_os_wait_stats`
- Query store/Top queries: `sys.query_store_runtime_stats`
- Active requests: `sys.dm_exec_requests`
- Plans: `sys.dm_exec_query_plan`, `sys.dm_exec_cached_plans`
- Index usage: `sys.dm_db_index_usage_stats`

## Common Tasks
- SARGability: avoid functions on indexed columns in predicates.
- Date handling: use `datetime2`; avoid implicit conversions.
- TVPs: use table-valued parameters for batch operations.
- Tempdb: monitor contention; pre-size files; use multiple data files.
