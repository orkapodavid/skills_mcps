# configuration.md

.xbbg.yml example with performance-related settings:

```yaml
bbg:
  host: localhost
  port: 8194
  timeout: 30000

cache:
  enabled: true
  directory: ~/.xbbg/cache
  ttl: 3600

parallel:
  max_workers: 4
  batch_size: 50

errors:
  retry_attempts: 3
  retry_delay: 5
  ignore_field_errors: true
  ignore_security_errors: true

logging:
  level: INFO
  file: ~/.xbbg/logs/xbbg.log
```

Notes:
- xbbg supports per-call overrides like `server` / `port` via kwargs.
- Local Parquet caching is enabled when `BBG_ROOT` is set in environment.
- Ensure compliance with Bloomberg Datafeed Addendum; data must remain on the local PC.
