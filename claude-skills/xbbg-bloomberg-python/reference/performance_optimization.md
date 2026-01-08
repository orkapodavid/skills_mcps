# performance_optimization.md

Batching & Parallelism
- Batch tickers (50–100 per request) for `bdp` / `bdh`.
- Use async variants (`abdp`, `abds`, `abdh`) for concurrent requests.
- Enable local caching via `BBG_ROOT` for frequently reused data.

Field & Date Strategies
- Request only essential fields to reduce payload.
- Choose suitable periodicity (`Per='W'`, `'M'`, `'Q'`) for historical data.
- Use `Fill='P'` and `Days='T'` to handle missing/non-trading days.

Intraday/Ticks
- For `bdtick` large pulls, use `timeout=1000` (ms) to avoid empty results.
- Use `session` windows (e.g., `day`, `am_open_30`) to constrain time ranges.

Currency & Multi-market
- Normalize to single currency via `currency='USD'` or post-process with `adjust_ccy`.
- Be mindful of exchange-specific trading sessions and timezones.
