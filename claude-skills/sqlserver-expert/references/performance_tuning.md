# Performance Tuning Guide (SQL Server)

## Identify Bottlenecks
1. Capture actual execution plan
2. Measure waits: high `PAGEIOLATCH` → IO; `CXPACKET`/`CXCONSUMER` → parallelism; `LCK_*` → locks
3. Profile top queries via Query Store or DMVs

## Fix Patterns
- SARGable predicates; remove non-deterministic functions from WHERE
- Right indexes: covering, filtered, composite (left-most)
- Reduce row size: correct data types; `varchar` vs `nvarchar` appropriately
- Statistics: `UPDATE STATISTICS dbo.Table WITH FULLSCAN` where needed
- Parameter sniffing: use `OPTION(RECOMPILE)` for outliers or `OPTIMIZE FOR (@p = value)`; consider local variables
- Memory grants: review `Actual Memory Grant` and spills; try rewrites and indexes
- Parallelism: set `cost threshold for parallelism` and `max degree of parallelism` thoughtfully

## Maintenance
- Index reorganize/rebuild based on fragmentation thresholds
- Auto stats on; async for volatile workloads
- Track baselines and regressions; use Query Store forcing carefully

## Troubleshooting Scripts
See `scripts/query_runner.py` for capturing timings and `scripts/bulk_insert.py` for load performance patterns.
