# Troubleshooting on Windows

**Symptoms & Fixes**
- `permission denied` writing data: Run elevated or change data dir to writable location (`XDG_DATA_HOME`)
- HTTPS errors on localhost: Run `caddy trust` elevated
- Service not starting: Check service account permissions, paths, and logs
- Reverse proxy 502: Verify backend is listening and reachable

**Validation Commands**
```powershell
Test-NetConnection -ComputerName localhost -Port 3000
Invoke-WebRequest http://localhost:8080 -UseBasicParsing
```
