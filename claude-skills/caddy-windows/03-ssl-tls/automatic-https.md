# Automatic HTTPS

**Summary:** Caddy enables HTTPS by default.

## Local Development
- `https://localhost` works out of the box
- Run elevated `caddy trust` to install local CA

## Public Domains
- Ensure DNS A/AAAA records point to your machine
- Open ports 80/443 (and forward to Caddy if needed)

## Example
```caddy
example.test {
  respond "Secure!"
}
```

## References
- https://caddyserver.com/docs/automatic-https
