# Local Development HTTPS

**Summary:** Options for HTTPS in local dev.

## Patterns
- Use `localhost` and trust local CA
- For custom domains, use hosts file mapping and local CA

## Verify
```powershell
Invoke-WebRequest https://localhost -SkipCertificateCheck
```

## References
- https://caddyserver.com/docs/automatic-https#local-https
