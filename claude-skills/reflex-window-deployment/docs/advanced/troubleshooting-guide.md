# Troubleshooting Guide

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
