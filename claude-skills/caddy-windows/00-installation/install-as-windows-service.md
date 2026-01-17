# Install as Windows Service

**Summary:** Run Caddy as a Windows Service for auto-start and restart.

## Use Cases
- Always-on local reverse proxy
- Background service during development

## Prerequisites
- Admin PowerShell
- `c:\	ools\\nssm\\nssm.exe` (or WinSW) installed

## Steps (NSSM)
1. Create Caddyfile (e.g. `C:\\caddy\\Caddyfile`).
2. Install service:
   ```powershell
   nssm install Caddy "C:\\path\\to\\caddy.exe" run --config "C:\\caddy\\Caddyfile"
   nssm set Caddy AppDirectory "C:\\caddy"
   nssm set Caddy Start SERVICE_AUTO_START
   nssm set Caddy AppStdout "C:\\caddy\\logs\\stdout.log"
   nssm set Caddy AppStderr "C:\\caddy\\logs\\stderr.log"
   nssm start Caddy
   ```

## Steps (WinSW)
1. Download WinSW (winsw.exe) and place next to `caddy.exe`.
2. Create `caddy.xml`:
   ```xml
   <service>
     <id>caddy</id>
     <name>Caddy</name>
     <executable>caddy.exe</executable>
     <arguments>run --config C:\\caddy\\Caddyfile</arguments>
     <logpath>C:\\caddy\\logs</logpath>
     <onfailure action="restart"/>
   </service>
   ```
3. Install and start:
   ```powershell
   .\winsw.exe install
   .\winsw.exe start
   ```

## Validation
```powershell
Get-Service Caddy
Get-Process caddy
```

## Troubleshooting
- Ensure service account has write access to Caddy data dir
- Open firewall for ports 80/443 if using public domains

## References
- https://caddyserver.com/docs/install
- https://caddyserver.com/docs/automatic-https
