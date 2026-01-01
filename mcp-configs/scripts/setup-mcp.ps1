#Requires -Version 5.1
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)

Write-Host "=== MCP Setup Script (Windows) ===" -ForegroundColor Cyan
Write-Host ""

function Select-Tool {
    Write-Host "Select tool to configure:"
    Write-Host "1) Claude Desktop"
    Write-Host "2) Claude Code"
    Write-Host "3) Cursor"
    $choice = Read-Host "Choice [1-3]"
    
    switch ($choice) {
        "1" { Setup-ClaudeDesktop }
        "2" { Setup-ClaudeCode }
        "3" { Setup-Cursor }
        default { Write-Error "Invalid choice"; exit 1 }
    }
}

function Setup-ClaudeDesktop {
    Write-Host ""
    Write-Host "--- Setting up Claude Desktop ---" -ForegroundColor Yellow
    $ConfigDir = "$env:APPDATA\Claude"
    New-Item -ItemType Directory -Force -Path $ConfigDir | Out-Null
    
    $ConfigFile = "$ConfigDir\claude_desktop_config.json"
    if (Test-Path $ConfigFile) {
        Write-Host "⚠️  Config file already exists" -ForegroundColor Yellow
        $confirm = Read-Host "Backup and replace? [y/N]"
        if ($confirm -eq "y" -or $confirm -eq "Y") {
            $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
            $backup = "$ConfigFile.backup.$timestamp"
            Copy-Item $ConfigFile $backup
            Write-Host "✓ Backup created: $backup" -ForegroundColor Green
        } else {
            Write-Host "Setup cancelled"
            exit 0
        }
    }
    
    $template = "$RepoRoot\mcp-configs\templates\claude-desktop\claude_desktop_config.windows.json"
    Copy-Item $template $ConfigFile
    
    Write-Host "✓ Config copied to: $ConfigFile" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "1. Edit the config file to add your credentials and paths"
    Write-Host "2. Replace YOUR_USERNAME with your actual username"
    Write-Host "3. Replace YOUR_GITHUB_PAT with your GitHub Personal Access Token"
    Write-Host "4. Restart Claude Desktop"
    Write-Host ""
    $editNow = Read-Host "Edit now? [y/N]"
    if ($editNow -eq "y" -or $editNow -eq "Y") {
        notepad $ConfigFile
    }
}

function Setup-ClaudeCode {
    Write-Host ""
    Write-Host "--- Setting up Claude Code ---" -ForegroundColor Yellow
    $projectPath = Read-Host "Project path (or . for current directory)"
    if ([string]::IsNullOrEmpty($projectPath)) { $projectPath = "." }
    $projectPath = Resolve-Path $projectPath
    
    $configFile = "$projectPath\.mcp.json"
    if (Test-Path $configFile) {
        Write-Host "⚠️  Config file already exists at $configFile" -ForegroundColor Yellow
        $confirm = Read-Host "Overwrite? [y/N]"
        if ($confirm -ne "y" -and $confirm -ne "Y") {
            Write-Host "Setup cancelled"
            exit 0
        }
    }
    
    $template = "$RepoRoot\mcp-configs\templates\claude-code\mcp.json"
    Copy-Item $template $configFile
    
    Write-Host "✓ Config copied to: $configFile" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "1. Set environment variables (e.g., `$env:GITHUB_TOKEN='...')"
    Write-Host "2. Customize the config if needed"
    Write-Host "3. Run your Claude Code commands"
}

function Setup-Cursor {
    Write-Host ""
    Write-Host "--- Setting up Cursor ---" -ForegroundColor Yellow
    $projectPath = Read-Host "Project path (or . for current directory)"
    if ([string]::IsNullOrEmpty($projectPath)) { $projectPath = "." }
    $projectPath = Resolve-Path $projectPath
    
    $cursorDir = "$projectPath\.cursor"
    New-Item -ItemType Directory -Force -Path $cursorDir | Out-Null
    
    $configFile = "$cursorDir\mcp.json"
    if (Test-Path $configFile) {
        Write-Host "⚠️  Config file already exists" -ForegroundColor Yellow
        $confirm = Read-Host "Overwrite? [y/N]"
        if ($confirm -ne "y" -and $confirm -ne "Y") {
            Write-Host "Setup cancelled"
            exit 0
        }
    }
    
    $template = "$RepoRoot\mcp-configs\templates\cursor\mcp.json"
    Copy-Item $template $configFile
    
    Write-Host "✓ Config copied to: $configFile" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "1. Set environment variables (e.g., `$env:GITHUB_TOKEN='...')"
    Write-Host "2. Reload Cursor window (Ctrl+Shift+P → Reload Window)"
}

# Main execution
Select-Tool
Write-Host ""
Write-Host "=== Setup complete ===" -ForegroundColor Cyan
