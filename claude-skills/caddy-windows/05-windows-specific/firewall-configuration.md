# Windows Firewall Configuration

**Summary:** Allow inbound traffic to Caddy.

## Open Ports
```powershell
New-NetFirewallRule -DisplayName "Caddy HTTP" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow
New-NetFirewallRule -DisplayName "Caddy HTTPS" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow
```

## Notes
- For local-only dev, you may keep ports closed and use `localhost`
