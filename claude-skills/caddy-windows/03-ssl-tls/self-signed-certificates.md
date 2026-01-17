# Self-Signed Certificates (Local)

**Summary:** Using Caddy's local CA for internal HTTPS.

## Steps
- Run elevated:
  ```powershell
  caddy trust
  ```
- Use `localhost` or `*.internal` hostnames

## References
- https://caddyserver.com/docs/automatic-https#local-https
