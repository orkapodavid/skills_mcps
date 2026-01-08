# deploy-offline.ps1
# Run on air-gapped Windows Server

param(
    [Parameter(Mandatory = $true)]
    [string]$SourcePath,  # Path to transferred offline package
    
    [string]$InstallPath = "C:\ReflexApp",
    [string]$ServiceName = "ReflexApp"
)

$ErrorActionPreference = "Stop"

Write-Host "=== Air-Gapped Reflex Deployment ===" -ForegroundColor Cyan

# 1. Verify checksums
Write-Host "`n[1/6] Verifying file integrity..." -ForegroundColor Yellow
$checksumFile = Join-Path $SourcePath "checksums.sha256"
# (Verification logic here - see full script)

# 2. Extract Python
Write-Host "`n[2/6] Setting up Python..." -ForegroundColor Yellow
$pythonZip = Get-ChildItem "$SourcePath\installers\python-*-embed-amd64.zip" | Select-Object -First 1
Expand-Archive $pythonZip.FullName -DestinationPath "$InstallPath\python" -Force

# Configure embedded Python
$pthFile = Get-ChildItem "$InstallPath\python\python*._pth" | Select-Object -First 1
$pthContent = @"
python311.zip
.
.\Scripts
.\Lib\site-packages
import site
"@
Set-Content -Path $pthFile.FullName -Value $pthContent

# 3. Install pip
Write-Host "`n[3/6] Installing pip..." -ForegroundColor Yellow
$pythonExe = "$InstallPath\python\python.exe"
$wheelhouse = "$SourcePath\wheelhouse"

& $pythonExe "$SourcePath\installers\get-pip.py" --no-index --find-links=$wheelhouse

# 4. Create virtual environment and install packages
Write-Host "`n[4/6] Installing application packages..." -ForegroundColor Yellow
& $pythonExe -m pip install --no-index --find-links=$wheelhouse virtualenv
& $pythonExe -m virtualenv "$InstallPath\venv"
& "$InstallPath\venv\Scripts\pip.exe" install --no-index --find-links=$wheelhouse -r "$wheelhouse\requirements.txt"

# 5. Install IIS modules
Write-Host "`n[5/6] Installing IIS modules..." -ForegroundColor Yellow
net stop WAS /y 2>$null
Start-Process msiexec.exe -ArgumentList "/i `"$SourcePath\iis-modules\rewrite_amd64_en-US.msi`" /qn /norestart" -Wait
Start-Process msiexec.exe -ArgumentList "/i `"$SourcePath\iis-modules\requestRouter_amd64.msi`" /qn /norestart" -Wait
net start WAS
net start W3SVC

# 6. Install Windows service
Write-Host "`n[6/6] Installing Windows service..." -ForegroundColor Yellow
Expand-Archive "$SourcePath\tools\nssm-2.24.zip" -DestinationPath "$InstallPath\tools" -Force
$nssm = "$InstallPath\tools\nssm-2.24\win64\nssm.exe"

& $nssm install $ServiceName "$InstallPath\venv\Scripts\python.exe"
& $nssm set $ServiceName AppParameters "-m reflex run --env prod"
& $nssm set $ServiceName AppDirectory $InstallPath
# (Additional NSSM configuration...)

Write-Host "`n=== Deployment Complete ===" -ForegroundColor Green
