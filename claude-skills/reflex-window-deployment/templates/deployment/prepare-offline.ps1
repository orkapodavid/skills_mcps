# prepare-offline-deployment.ps1
# Run on machine with internet access

param(
    [string]$OutputPath = "C:\OfflineDeployment",
    [string]$PythonVersion = "3.11.6"
)

# Create output structure
$dirs = @("wheelhouse", "installers", "tools", "iis-modules")
foreach ($dir in $dirs) {
    New-Item -ItemType Directory -Path "$OutputPath\$dir" -Force | Out-Null
}

# 1. Download embedded Python
$pythonUrl = "https://www.python.org/ftp/python/$PythonVersion/python-$PythonVersion-embed-amd64.zip"
Invoke-WebRequest -Uri $pythonUrl -OutFile "$OutputPath\installers\python-$PythonVersion-embed-amd64.zip"

# 2. Download get-pip.py
Invoke-WebRequest -Uri "https://bootstrap.pypa.io/get-pip.py" -OutFile "$OutputPath\installers\get-pip.py"

# 3. Download WinSW
$winswUrl = "https://github.com/winsw/winsw/releases/download/v2.12.0/WinSW.NET461.exe"
Invoke-WebRequest -Uri $winswUrl -OutFile "$OutputPath\tools\WinSW.exe"

# 4. Download NSSM
Invoke-WebRequest -Uri "https://nssm.cc/release/nssm-2.24.zip" -OutFile "$OutputPath\tools\nssm-2.24.zip"

# 5. Download IIS modules
$modules = @{
    "rewrite_amd64_en-US.msi" = "https://download.microsoft.com/download/1/2/8/128E2E22-C1B9-44A4-BE2A-5859ED1D4592/rewrite_amd64_en-US.msi"
    "requestRouter_amd64.msi" = "https://go.microsoft.com/fwlink/?LinkID=615136"
}
foreach ($module in $modules.GetEnumerator()) {
    Invoke-WebRequest -Uri $module.Value -OutFile "$OutputPath\iis-modules\$($module.Key)"
}

# 6. Download Python packages
Write-Host "Downloading Python packages..." -ForegroundColor Cyan

# Create temp venv to generate requirements
python -m venv "$OutputPath\temp_venv"
& "$OutputPath\temp_venv\Scripts\pip.exe" install reflex uvicorn msal pyjwt[crypto] httpx

# Export requirements
& "$OutputPath\temp_venv\Scripts\pip.exe" freeze > "$OutputPath\wheelhouse\requirements.txt"

# Download wheels for Windows x64
& "$OutputPath\temp_venv\Scripts\pip.exe" download `
    --only-binary=:all: `
    --platform win_amd64 `
    --python-version 311 `
    -d "$OutputPath\wheelhouse" `
    -r "$OutputPath\wheelhouse\requirements.txt"

# Also download pip, setuptools, wheel for bootstrap
& "$OutputPath\temp_venv\Scripts\pip.exe" download pip setuptools wheel virtualenv -d "$OutputPath\wheelhouse"

# Cleanup temp venv
Remove-Item -Recurse -Force "$OutputPath\temp_venv"

# 7. Generate checksums
Get-ChildItem -Path $OutputPath -Recurse -File | ForEach-Object {
    $hash = Get-FileHash $_.FullName -Algorithm SHA256
    "$($hash.Hash)  $($_.FullName.Replace($OutputPath, '.'))"
} | Out-File "$OutputPath\checksums.sha256"

Write-Host "`nOffline deployment package ready at: $OutputPath" -ForegroundColor Green
Write-Host "Transfer this folder to the air-gapped server" -ForegroundColor Yellow
