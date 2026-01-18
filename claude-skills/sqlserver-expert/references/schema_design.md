# Schema Design Guide (SQL Server)

## Principles
- Model entities with clear primary keys; use surrogate keys when natural keys are unstable
- Normalize to 3NF; denormalize judiciously for query performance
- Use `datetime2`, `decimal(p,s)` for precision; avoid `float` for money
- Define `CHECK` constraints for invariants; `FOREIGN KEY` for integrity
- Partition large tables by ranged keys when beneficial

## Patterns
- Auditing: created_at/updated_at with default constraints
- Soft delete: nullable deleted_at rather than a flag when history matters
- Many-to-many: bridge tables with composite unique keys
- Multi-tenancy: tenant_id with filtered indexes; consider row-level security

## Migration Safety
- Backfill in batches; avoid long exclusive locks
- Add columns nullable first; then backfill; then `NOT NULL` with default
- Use `ONLINE = ON` options where supported
