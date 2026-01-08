# SKILL.md

**xbbg Bloomberg Python Skill**

Overview
- Intuitive Bloomberg data API for Python; DataFrame-first.
- Core functions: `bdp` (reference), `bdh` (historical), `bds` (bulk), `bdib` (intraday bars), `bdtick` (ticks), `beqs` (equity screening), `bql` (query language), `live`/`subscribe` (real-time).
- Utilities: `fieldInfo`, `fieldSearch`, `lookupSecurity`, `getPortfolio`, `fut_ticker`, `active_futures`, `cdx_ticker`, `adjust_ccy`.
- Requirements: Bloomberg C++ SDK ≥ 3.12.1; `blpapi` Python; numpy, pandas, ruamel.yaml, pyarrow; Python 3.10–3.14.
- Install: `pip install xbbg`.
- Connection: default `localhost:8194`; override via `server`/`port` kwargs.

Quick Start
```python
from xbbg import blp

ref = blp.bdp(['AAPL US Equity','MSFT US Equity'], ['PX_LAST','VOLUME'])
print(ref.head())

hist = blp.bdh('SPX Index', ['high','low','last_price'], '2021-01-01', '2021-01-05')
print(hist.tail())

bulk = blp.bds('AAPL US Equity', 'DVD_HIST_ALL')
print(bulk.head())
```

Core Functions Deep Dive
- `bdp(tickers, flds, **kwargs)`: Reference data. Overrides supported (e.g., `VWAP_Dt`). Returns tickers × fields.
- `bdh(tickers, flds, start_date, end_date=None, **kwargs)`: Historical. `Per`, `Fill`, `Days`, `adjust` for splits/dividends.
- `bds(tickers, flds, **kwargs)`: Bulk/tabular (e.g., dividends, cash flows, holders).
- `bdib(ticker, dt, interval=1, session=None, **kwargs)`: Intraday bars; minute or sub‑minute (`intervalHasSeconds=True`). Sessions via exchange metadata.
- `bdtick(ticker, dt, session=None, **kwargs)`: Tick-by-tick; use `timeout` for large requests.
- `beqs(screen, **kwargs)`: Run saved equity screens; enrich with `bdp`.
- `bql(query)`: Bloomberg Query Language; SQL‑like; `for()` must be outside `get()`.
- `live(tickers, fields)`, `subscribe(tickers, fields, interval)`: Real‑time streaming.

Workflows
1) Daily PIPE Screening (BEQS→BDP→BDS)
2) Historical Fundamentals (quarterly `bdh`) and trend metrics
3) Portfolio Monitoring (`bdp` snapshot and PnL)
4) Multi‑currency reporting (`bdh` + `adjust_ccy`)

Configuration & Setup
- Sample `.xbbg.yml` with `bbg`, `cache`, `parallel`, `errors`, `logging` sections.
- Environment: `BBG_ROOT` enables local Parquet caching (Datafeed Addendum applies).

Best Practices
- Batch requests; prefer async (`abdp`/`abdh`) for concurrency.
- Request only necessary fields; choose appropriate periodicity.
- Use sessions (`day`, `am_open_30`) to constrain intraday windows.
- Normalize currency during retrieval or via `adjust_ccy`.

Common Pitfalls
- Empty DataFrame: invalid ticker/field; check formats and enable logging.
- Slow pulls: too many single‑ticker calls; batch and cache.
- Missing dates: use `Fill='P'`, `Days='T'`.
- Currency confusion: set `currency` consistently.
- Connection errors: ensure Terminal logged in; verify host/port.

Integration Patterns
- Dynamics 365 enrichment via REST `PATCH` with `bdp`/`bds` outputs.
- Pandas/Polars workflows; SQL export via `to_sql`.
- Prefect orchestration for daily screens.

References
- Saved pages:
  - /home/user/workspace/resources/webpages/webpage_https:__xbbg.readthedocs.io_en_latest_.md
  - /home/user/workspace/resources/webpages/webpage_GitHub - alpha-xone_xbbg: An intuitive Bloomberg API.md
  - /home/user/workspace/resources/webpages/webpage_xbbg.md
