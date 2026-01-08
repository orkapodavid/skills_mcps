# Windows Service Management

## WinSW Configuration (winsw.xml)

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- 
  WinSW Configuration for Reflex Application
  Place alongside WinSW.exe (renamed to match app name)
  Download: https://github.com/winsw/winsw/releases/download/v2.12.0/WinSW.NET461.exe
-->
<service>
  <!-- === Service Identity === -->
  <id>ReflexApp</id>
  <name>Reflex Application Service</name>
  <description>Reflex full-stack Python application running on Uvicorn</description>
  
  <!-- === Executable Configuration === -->
  <executable>%BASE%\.venv\Scripts\python.exe</executable>
  <arguments>-m reflex run --env prod --backend-only --backend-port 8000</arguments>
  <workingdirectory>%BASE%</workingdirectory>
  
  <!-- === Environment Variables === -->
  <env name="REFLEX_ENV" value="production"/>
  <env name="API_URL" value="https://myapp.corp.com"/>
  <env name="DATABASE_URL" value="postgresql://user:pass@dbserver/myapp"/>
  <env name="PYTHONUNBUFFERED" value="1"/>
  
  <!-- === Logging with Rotation === -->
  <logpath>%BASE%\logs</logpath>
  <log mode="roll-by-size">
    <sizeThreshold>10240</sizeThreshold>  <!-- 10MB -->
    <keepFiles>10</keepFiles>
  </log>
  
  <!-- === Service Startup === -->
  <startmode>Automatic</startmode>
  <delayedAutoStart>true</delayedAutoStart>
  
  <!-- === Dependencies (wait for network) === -->
  <depend>Tcpip</depend>
  <depend>Dnscache</depend>
  
  <!-- === Recovery on Failure === -->
  <onfailure action="restart" delay="10 sec"/>
  <onfailure action="restart" delay="30 sec"/>
  <onfailure action="restart" delay="60 sec"/>
  <resetfailure>1 hour</resetfailure>
  
  <!-- === Graceful Shutdown === -->
  <stoptimeout>30 sec</stoptimeout>
  <stopparentprocessfirst>true</stopparentprocessfirst>
  
  <!-- === Security (run as service account) === -->
  <serviceaccount>
    <user>NetworkService</user>
  </serviceaccount>
</service>
```

## WinSW Installation Commands

```powershell
# Rename WinSW executable to match your app
Rename-Item WinSW.NET461.exe ReflexApp.exe

# Install service
.\ReflexApp.exe install

# Start service
.\ReflexApp.exe start

# Check status
.\ReflexApp.exe status

# View logs
Get-Content .\logs\ReflexApp.out.log -Tail 50 -Wait
```

## NSSM Installation Script (install-service.ps1)

```powershell
# install-reflex-service.ps1
# NSSM-based service installation for Reflex applications

param(
    [Parameter(Mandatory=$true)]
    [string]$ServiceName,
    
    [Parameter(Mandatory=$true)]
    [string]$AppPath,
    
    [int]$Port = 8000,
    [string]$ApiUrl = "https://myapp.corp.com"
)

$ErrorActionPreference = "Stop"

# Paths
$VenvPython = Join-Path $AppPath ".venv\Scripts\python.exe"
$LogDir = Join-Path $AppPath "logs"
$NssmPath = "nssm.exe"  # Assumes in PATH

# Validate
if (-not (Test-Path $VenvPython)) {
    throw "Virtual environment not found at $VenvPython"
}

# Create log directory
New-Item -ItemType Directory -Path $LogDir -Force | Out-Null

Write-Host "Installing service: $ServiceName" -ForegroundColor Cyan

# Install service
& $NssmPath install $ServiceName $VenvPython "-m" "reflex" "run" "--env" "prod" "--backend-only" "--backend-port" "$Port"

# Application settings
& $NssmPath set $ServiceName AppDirectory $AppPath
& $NssmPath set $ServiceName DisplayName "Reflex App - $ServiceName"
& $NssmPath set $ServiceName Description "Reflex Python application on port $Port"

# Environment variables
& $NssmPath set $ServiceName AppEnvironmentExtra `
    "REFLEX_ENV=production" `
    "API_URL=$ApiUrl" `
    "BACKEND_PORT=$Port" `
    "PYTHONUNBUFFERED=1"

# Logging with rotation
& $NssmPath set $ServiceName AppStdout "$LogDir\stdout.log"
& $NssmPath set $ServiceName AppStderr "$LogDir\stderr.log"
& $NssmPath set $ServiceName AppStdoutCreationDisposition 4
& $NssmPath set $ServiceName AppStderrCreationDisposition 4
& $NssmPath set $ServiceName AppRotateFiles 1
& $NssmPath set $ServiceName AppRotateOnline 1
& $NssmPath set $ServiceName AppRotateBytes 10485760  # 10MB

# Restart behavior
& $NssmPath set $ServiceName AppExit Default Restart
& $NssmPath set $ServiceName AppRestartDelay 5000

# Graceful shutdown (Python needs time)
& $NssmPath set $ServiceName AppStopMethodConsole 15000
& $NssmPath set $ServiceName AppStopMethodWindow 15000
& $NssmPath set $ServiceName AppStopMethodThreads 15000

# Auto-start
& $NssmPath set $ServiceName Start SERVICE_AUTO_START

# Windows-level recovery
sc.exe failure $ServiceName reset= 86400 actions= restart/60000/restart/60000/restart/60000

Write-Host "Service installed successfully!" -ForegroundColor Green
Write-Host "Start with: nssm start $ServiceName" -ForegroundColor Yellow
```
