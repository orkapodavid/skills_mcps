# Environment Variables (Windows)

**Summary:** Configure Caddy with env vars.

## Examples
```powershell
$Env:CADDY_HOME = "C:\\caddy"
$Env:XDG_DATA_HOME = "C:\\caddy\\data"
$Env:XDG_CONFIG_HOME = "C:\\caddy\\config"
```

Run Caddy:
```powershell
caddy run --environ
```
