# Install Caddy (Standalone)

**Summary:** Install Caddy as a standalone binary on Windows for local dev.

## Use Cases
- Quick local HTTP(S) server
- Reverse proxy to local apps

## Prerequisites
- Windows 10/11
- PowerShell 5.0+

## Steps
1. Download Caddy:
   - Chocolatey: `choco install caddy`
   - Scoop: `scoop install caddy`
   - Webi: `curl.exe https://webi.ms/caddy | powershell`
   - Manual: Download `caddy.exe` from GitHub Releases and put it in `%PATH%`
2. Verify:
   ```powershell
   caddy version
   ```
3. Run demo:
   ```powershell
   New-Item -ItemType File -Path .\Caddyfile -Value ":2015 {\n  respond \"Hello Caddy!\"\n}"
   caddy run --config .\Caddyfile
   ```

## Validation
- PowerShell:
  ```powershell
  Invoke-WebRequest http://localhost:2015 -UseBasicParsing | Select-Object -ExpandProperty Content
  ```

## Troubleshooting
- Ensure `%PATH%` contains the folder with `caddy.exe`
- Unblock downloaded binary: Right-click > Properties > Unblock

## References
- https://caddyserver.com/docs/install
- https://github.com/caddyserver/caddy/releases
