# Deployment Checklist

## Pre-Deployment Checklist

- [ ] **Python 3.11+** installed or embedded Python prepared
- [ ] **Virtual environment** created with all dependencies
- [ ] **rxconfig.py** configured with production URLs
- [ ] **Environment variables** documented and set
- [ ] **Database** migrations completed
- [ ] **Firewall rules** allow IIS ports (80, 443)

## IIS Configuration Checklist

- [ ] **WebSocket Protocol** feature installed
- [ ] **URL Rewrite Module 2.1** installed
- [ ] **Application Request Routing 3.0** installed
- [ ] **Proxy enabled** at server level
- [ ] **Timeout set to 300+ seconds** for WebSocket
- [ ] **responseBufferLimit set to 0** for streaming
- [ ] **SSL certificate** bound to site

## Authentication Checklist (Phase 1: Windows Auth)

- [ ] **Windows Authentication** feature installed
- [ ] **Anonymous Authentication** disabled
- [ ] **SPNs registered** (setspn -X shows no duplicates)
- [ ] **HTTP_X_REMOTE_USER** in allowedServerVariables
- [ ] **Backend validates** X-Remote-User header
- [ ] **Test with domain user** - verify LOGON_USER populated

## Authentication Checklist (Phase 2: Entra ID)

- [ ] **App Registration** completed in Entra admin center
- [ ] **Redirect URIs** configured for all environments
- [ ] **Client secret** generated and stored securely
- [ ] **API permissions** granted admin consent
- [ ] **Session middleware** configured with secure cookies
- [ ] **PKCE enabled** in OAuth flow
- [ ] **Test login flow** end-to-end

## Service Wrapper Checklist

- [ ] **WinSW/NSSM** executable in place
- [ ] **Configuration file** validated (XML syntax)
- [ ] **Log directory** created with write permissions
- [ ] **Environment variables** set in service config
- [ ] **Service installed** and running
- [ ] **Auto-start** enabled
- [ ] **Recovery actions** configured

## Go/No-Go Validation

```powershell
# Quick validation script
$checks = @()

# Check service running
$service = Get-Service -Name "ReflexApp" -ErrorAction SilentlyContinue
$checks += @{Name="Service Running"; Pass=$service.Status -eq "Running"}

# Check port listening
$listener = Get-NetTCPConnection -LocalPort 3000 -State Listen -ErrorAction SilentlyContinue
$checks += @{Name="Port 3000 Listening"; Pass=$listener -ne $null}

# Check IIS site
$site = Get-Website -Name "MyReflexApp" -ErrorAction SilentlyContinue
$checks += @{Name="IIS Site Running"; Pass=$site.State -eq "Started"}

# Check SSL binding
$binding = Get-WebBinding -Name "MyReflexApp" -Protocol https
$checks += @{Name="HTTPS Binding"; Pass=$binding -ne $null}

# Check WebSocket endpoint
try {
    $ws = Invoke-WebRequest -Uri "https://localhost/_event/" -UseBasicParsing -TimeoutSec 5
    $checks += @{Name="WebSocket Endpoint"; Pass=$true}
} catch {
    $checks += @{Name="WebSocket Endpoint"; Pass=$false}
}

# Output results
$checks | ForEach-Object {
    $status = if ($_.Pass) {"✓"} else {"✗"}
    $color = if ($_.Pass) {"Green"} else {"Red"}
    Write-Host "$status $($_.Name)" -ForegroundColor $color
}
```
