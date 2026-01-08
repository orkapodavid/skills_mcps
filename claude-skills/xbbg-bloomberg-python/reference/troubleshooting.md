# troubleshooting.md

Common Issues & Fixes

Empty DataFrame
- Cause: invalid ticker/field; not in trading session; missing permissions.
- Fix: verify identifier format (e.g., `7203 JT Equity`); check `fieldInfo` / `fieldSearch`; ensure Terminal logged in.

Slow Performance
- Cause: excessive single‑ticker calls or wide field sets.
- Fix: batch tickers (50–100); use async (`abdp`/`abdh`); enable local caching (set `BBG_ROOT`).

Missing Dates / Gaps
- Cause: non‑trading days or partial sessions.
- Fix: `Fill='P'`; `Days='T'`; use session windows for intraday.

Currency Inconsistencies
- Cause: mixed currencies across tickers.
- Fix: set `currency='USD'` (or desired currency); post‑process via `adjust_ccy`.

Tick Requests Return Empty
- Cause: timeouts for large ranges.
- Fix: increase `timeout` (e.g., `timeout=1000` ms); narrow `session` window.

Connection Errors
- Cause: wrong host/port or Terminal not running.
- Fix: confirm `localhost:8194` (or set `server`/`port`); verify Bloomberg login.

Diagnostics
```python
from xbbg import blp
import logging
logging.basicConfig(level=logging.DEBUG)

try:
    test = blp.bdp('AAPL US Equity', 'PX_LAST')
    print('✓ Bloomberg connection OK')
except Exception as e:
    print(f'✗ Connection failed: {e}')

# Check field validity
print(blp.fieldInfo(['PX_LAST','CUR_MKT_CAP']))
print(blp.fieldSearch('vwap'))
```
