# Caddyfile Syntax Guide

**Summary:** The human-friendly config format for Caddy.

## Concepts
- Site blocks: `address { ... }`
- Directives: keywords enabling features (e.g., `reverse_proxy`, `file_server`)
- Matchers: filter requests, e.g. `@api { path /api/* }`
- Placeholders: dynamic values like `{path}` `{remote_ip}` `{upstream_hostport}`

## Example
```caddy
:8080 {
  handle /api/* {
    reverse_proxy localhost:3000
  }
  handle {
    root * C:\\www
    file_server
  }
}
```

## Windows Notes
- Escape backslashes: `C:\\path\\to\\dir`
- Use Windows paths for `root`

## References
- https://caddyserver.com/docs/caddyfile
- https://caddyserver.com/docs/caddyfile/concepts
