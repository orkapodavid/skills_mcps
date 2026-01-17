# Directives Reference (Common)

- `reverse_proxy`: Proxy to upstreams; supports load balancing and health checks.
- `file_server`: Serve static files from `root`.
- `encode`: Enable gzip/zstd compression.
- `log`: Configure access logs.
- `handle` / `handle_path`: Group routes; rewrite path prefix.
- `route`: Advanced handler sequencing.
- `tls`: Configure certificates, client auth.
- `header_up`/`header_down`: Manipulate headers to/from upstream.

## References
- https://caddyserver.com/docs/caddyfile/directives
