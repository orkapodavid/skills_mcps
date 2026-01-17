# Placeholders & Functions

**Summary:** Dynamic values usable in Caddyfile.

## Common Placeholders
- `{path}`: Request path
- `{query}`: Query string
- `{remote_ip}`: Client IP
- `{host}`: Request host
- `{upstream_hostport}`: Current upstream host:port
- `{http.reverse_proxy.active.target_upstream}`: Active upstream in health checks

## Example
```caddy
reverse_proxy https://api.example.com {
  header_up Host {upstream_hostport}
}
```

## References
- https://caddyserver.com/docs/caddyfile/concepts#placeholders
