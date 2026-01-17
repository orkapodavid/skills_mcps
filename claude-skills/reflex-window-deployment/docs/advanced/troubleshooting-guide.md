# Troubleshooting Guide

## The Heuristic Matrix

Troubleshooting is where agents add the most value. Use this matrix to map symptoms to specific IIS/Reflex misconfigurations.

| Symptom | Observation | Heuristic / Cause | Fix |
| :--- | :--- | :--- | :--- |
| **WebSocket Connection Failed (1006)** | The app loads static content, but the connection indicator spins, and the console shows a 1006 error code. | **IIS Feature Missing:** IIS doesn't know how to Upgrade the connection. | Check if the `Web-WebSockets` feature is installed. |
| | | **ARR Disabled:** ARR Proxy functionality is not enabled at the server level. | Enable ARR Proxy in IIS Manager or via `appcmd`. |
| | | **Timeout:** IIS has a default WebSocket timeout. If the user is idle, IIS kills the connection. | Increase `responseTimeout` in `web.config` `system.webServer/proxy`. |
| **502.3 Bad Gateway** | The backend API returns 502.3. | **Service Down:** IIS cannot talk to the backend. | Check if the ReflexBackend service is running. |
| | | **Port Mismatch:** Uvicorn is not listening on the expected port. | Use `netstat -an \| findstr 8000` to verify. |
| | | **IPv4/IPv6:** Uvicorn listening on 127.0.0.1 but IIS trying `localhost` (resolving to ::1). | Ensure both use `127.0.0.1` explicitly. |
| **404.13 Content Length Exceeded** | Uploading a large file fails instantly. | **Request Limits:** IIS `maxAllowedContentLength` default is ~30MB. | Adjust `requestFiltering` in `web.config` (set `maxAllowedContentLength` to 100MB+). |
| **Unexpected response code: 200** | Browser console error during WebSocket handshake. | **Rewrite Rule Fallthrough:** The request fell through to the SPA rule and returned `index.html`. | Ensure `stopProcessing="true"` is set on the WebSocket rule in `web.config`. |

## Failed Request Tracing (FRT)

For errors that defy logic (like 403s or random disconnects), use FRT. This is the "MRI scan" of IIS.

1.  **Open IIS Manager** -> Select Site -> **Failed Request Tracing Rules**.
2.  **Add Rule** -> All Content.
3.  **Status Codes:** `400-999` (Capture all errors).
4.  **Providers:** Select `WWW Server` and crucially **ARR** and **Rewrite**.
5.  Reproduce the error.
6.  Open the XML log in `C:\inetpub\logs\FailedReqLogFiles`.
7.  Look for `REWRITE_ACTION` events to see exactly how the URL was rewritten and where it was sent.

## 502 Error Resolution

| Error Code | Win32 Status | Cause | Solution |
|------------|--------------|-------|----------|
| 502.3 | 12002 | Timeout | Increase proxy timeout to 300+ sec |
| 502.3 | 12030 | Connection aborted | Check backend is running |
| 502.4 | 0 | No server available | Verify backend port and firewall |

```powershell
# Diagnose 502 errors
# Check IIS logs for win32 status
Get-Content C:\inetpub\logs\LogFiles\W3SVC1\*.log -Tail 20 | Select-String "502"

# Increase timeout
appcmd.exe set config -section:system.webServer/proxy /timeout:"00:05:00" /commit:apphost
```

## WebSocket Connection Failures

```powershell
# Verify WebSocket feature enabled
Get-WindowsFeature Web-WebSockets

# Check ARR WebSocket support
appcmd.exe list config -section:system.webServer/proxy

# Test WebSocket endpoint directly
# Should return 101 Switching Protocols
curl -v -H "Upgrade: websocket" -H "Connection: Upgrade" http://localhost:3000/_event/
```

## Authentication Debugging

```powershell
# Check Kerberos tickets
klist

# Purge and refresh tickets
klist purge

# Verify SPN
setspn -L DOMAIN\svc_account

# Check for SPN duplicates
setspn -X

# Enable Kerberos logging
# HKLM\SYSTEM\CurrentControlSet\Control\Lsa\Kerberos\Parameters
# LogLevel = 1
```
