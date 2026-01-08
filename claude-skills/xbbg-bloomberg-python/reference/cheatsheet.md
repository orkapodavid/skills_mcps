# cheatsheet.md

Common Calls
- Reference (BDP): `blp.bdp(['AAPL US Equity'], ['PX_LAST','VOLUME'])`
- History (BDH): `blp.bdh('SPX Index', ['high','low'], '2025-01-01', '2025-01-10')`
- Bulk (BDS): `blp.bds('AAPL US Equity', 'DVD_HIST_ALL')`
- Intraday (BDIB): `blp.bdib(ticker='7974 JT Equity', dt='2025-12-01', session='am_open_30')`
- Ticks (BDTICK): `blp.bdtick('AAPL US Equity', '2025-11-12', session='day', timeout=1000)`
- Screen (BEQS): `blp.beqs(screen='My Saved Screen')`
- BQL: `blp.bql("get(px_last) for('AAPL US Equity')")`
- Live: `blp.live(['AAPL US Equity'], ['LAST_PRICE'])` (context manager)
- Subscribe: `blp.subscribe(['AAPL US Equity'], ['LAST_PRICE'], interval=10)`

Async Variants
- `abdp`, `abds`, `abdh` usable with `asyncio.gather(...)`

Key kwargs
- Historical: `Per`, `Fill`, `Days`, `adjust`, `currency`
- Intraday: `interval`, `intervalHasSeconds`, `session`, `ref`, `tz`
- Connection: `server`, `port` passed via kwargs to any call

Identifier Shortcuts
- Fixed income: `/isin/US123...`, `/cusip/123...`, `/sedol/123...`

Troubleshooting Quick Checks
- Validate tickers/fields; use `fieldInfo`, `fieldSearch`, `lookupSecurity`
- Ensure Bloomberg Terminal logged in; default host/port reachable
- Use `timeout` for large tick requests; batch tickers for `bdp`/`bdh`
