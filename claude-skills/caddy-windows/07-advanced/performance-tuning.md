# Performance Tuning

**Summary:** Improve throughput and latency.

## Tips
- Enable compression: `encode gzip zstd`
- Tune transport timeouts in `reverse_proxy`
- Use `keepalive` settings for HTTP transport
- Prefer `handle` blocks to avoid matcher overhead
- Serve static assets via `file_server` with caching headers

## References
- https://caddyserver.com/docs/caddyfile/directives/reverse_proxy#transports
