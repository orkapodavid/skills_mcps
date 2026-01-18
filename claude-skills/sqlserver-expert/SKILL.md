---
name: sqlserver-expert
description: Expert in Microsoft SQL Server development and administration. Use when writing T-SQL queries, optimizing database performance, designing schemas, configuring SQL Server, or integrating SQL Server with Python using pyodbc packages.
---

# Microsoft SQL Server Expert

This skill equips AnyGen to work effectively with Microsoft SQL Server for T-SQL development, performance tuning, schema design, configuration, and Python integration via `pyodbc`.

## Quick Start

- For T-SQL questions: Prefer concise, correct queries. Use CTEs, window functions, and parameterization. Verify compatibility with SQL Server version when relevant.
- For performance issues: Identify bottlenecks using DMVs, actual execution plans, and wait stats. Apply indexing, statistics updates, and query rewrites.
- For schema design: Normalize for integrity, denormalize for performance when justified. Use proper data types and constraints.
- For Python integration: Use `pyodbc` with parameterized queries, transactions, and robust error handling.

See linked references for details:
- T-SQL patterns: references/t_sql_cheatsheet.md
- Performance tuning guide: references/performance_tuning.md
- Schema design: references/schema_design.md
- Python `pyodbc` guide: references/pyodbc_guide.md

## Workflow

1. Clarify goal and constraints (latency, concurrency, data volume, SQL Server edition/version).
2. Choose approach:
   - Read/write queries → T-SQL patterns
   - Slow query / high CPU → Performance tuning
   - New feature / table changes → Schema design
   - App integration → Python `pyodbc`
3. Execute minimal reproducible steps:
   - Draft T-SQL and test on sample data
   - Capture actual execution plan and key DMVs
   - Apply controlled changes; measure impact
   - Implement parameterized Python code with transactions
4. Validate:
   - Correctness on edge cases
   - Performance targets met
   - Idempotency and rollback safety
5. Document essential decisions (indexes added, isolation level, parameter choices).

## Tools and Resources

- Scripts in `scripts/` are ready-to-run examples:
  - `connect_pyodbc.py` – Connection helpers (SQL auth/Windows/DSN), test query
  - `query_runner.py` – Parameterized query execution with transaction management
  - `bulk_insert.py` – Fast bulk insert from CSV using `BULK INSERT` or `pyodbc` executemany

Use and adapt scripts rather than rewriting from scratch.

## Safety and Best Practices

- Always parameterize to avoid SQL injection.
- Use least-privilege accounts; avoid `sa`.
- Prefer `READ COMMITTED SNAPSHOT` for concurrency-heavy workloads when appropriate.
- For long operations, batch work and monitor locks and waits.
- Keep statistics updated; consider `AUTO_UPDATE_STATISTICS_ASYNC` when suitable.
- Log changes and verify with actual plans; do not rely solely on estimated plans.

## When to Load References

- Need specific T-SQL syntax/patterns → Load `references/t_sql_cheatsheet.md`
- Diagnosing performance or indexing → Load `references/performance_tuning.md`
- Designing tables/keys/constraints → Load `references/schema_design.md`
- Integrating with Python apps → Load `references/pyodbc_guide.md`
