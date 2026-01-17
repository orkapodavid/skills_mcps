# Monitoring & Logging

**Summary:** Observe Caddy behavior.

## Access Logs
```caddy
:8080 {
  log {
    output file C:\\caddy\\logs\\access.log
    format console
  }
}
```

## Metrics
- Use sidecar exporters or scrape logs for analytics

## References
- https://caddyserver.com/docs/logging
