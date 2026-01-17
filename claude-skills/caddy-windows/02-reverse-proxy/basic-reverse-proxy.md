# Basic Reverse Proxy

**Summary:** Proxy traffic to a single local backend.

## Use Case
- Frontend on :8080, backend on :3000

## Example
```caddy
:8080 {
  reverse_proxy localhost:3000
}
```

## Validation
```powershell
Invoke-WebRequest http://localhost:8080/api -UseBasicParsing
```

## References
- https://caddyserver.com/docs/caddyfile/directives/reverse_proxy
