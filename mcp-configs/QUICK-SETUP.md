# MCP Quick Setup Guide

Get your AI tools connected to MCP servers in minutes with this cross-platform setup guide.

## Prerequisites

| Requirement | Windows | macOS |
|-------------|---------|-------|
| Node.js v18+ | Download from [nodejs.org](https://nodejs.org) or `winget install OpenJS.NodeJS` | `brew install node` |
| Git | `winget install Git.Git` | `brew install git` |
| Python 3.8+ | Download from [python.org](https://python.org) or `winget install Python.Python.3.12` | Included, or `brew install python3` |
| GitHub PAT | Generate at [github.com/settings/tokens](https://github.com/settings/tokens) | Same |

**Verify prerequisites**:
```bash
node --version  # Should be v18 or higher
git --version
python3 --version
```

## Setup by Tool

### Option 1: Automated Setup (Recommended)

**macOS/Linux**:
```bash
cd mcp-configs
chmod +x scripts/setup-mcp.sh
./scripts/setup-mcp.sh
```

**Windows (PowerShell)**:
```powershell
cd mcp-configs
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\setup-mcp.ps1
```

The script will guide you through selecting your tool and copying the appropriate configuration.

### Option 2: Manual Setup

#### Claude Desktop

**macOS**:
```bash
# Create config directory
mkdir -p ~/Library/Application\ Support/Claude

# Copy template
cp mcp-configs/templates/claude-desktop/claude_desktop_config.macos.json \
   ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Edit configuration
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
# or
open -a TextEdit ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Windows (PowerShell)**:
```powershell
# Create config directory
$configDir = "$env:APPDATA\Claude"
New-Item -ItemType Directory -Force -Path $configDir

# Copy template
Copy-Item mcp-configs\templates\claude-desktop\claude_desktop_config.windows.json `
    "$configDir\claude_desktop_config.json"

# Edit configuration
notepad "$configDir\claude_desktop_config.json"
```

**What to customize**:
- Replace `YOUR_USERNAME` with your actual username
- Replace `YOUR_GITHUB_PAT` with your GitHub Personal Access Token
- Update paths to match your project directories
- Add or remove MCP servers as needed

#### Claude Code

**Project-level setup (Recommended)**:
```bash
# Copy template to your project
cp mcp-configs/templates/claude-code/mcp.json /path/to/your/project/.mcp.json

# Edit the config
cd /path/to/your/project
nano .mcp.json
```

**Global setup**:
```bash
# macOS
mkdir -p ~/.claude
cp mcp-configs/templates/claude-code/mcp.json ~/.claude/mcp.json

# Windows
mkdir $env:USERPROFILE\.claude
Copy-Item mcp-configs\templates\claude-code\mcp.json $env:USERPROFILE\.claude\mcp.json
```

#### Cursor

```bash
# Create .cursor directory in your project
mkdir -p /path/to/your/project/.cursor

# Copy template
cp mcp-configs/templates/cursor/mcp.json /path/to/your/project/.cursor/mcp.json

# Edit configuration
cd /path/to/your/project
nano .cursor/mcp.json
```

## Environment Variables Setup

### Creating a .env file (Project-level)

Create a `.env` file in your project (never commit this):

```bash
# .env
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
NOTION_API_KEY=secret_xxxxxxxxxxxx
POSTGRES_CONNECTION_STRING=postgresql://user:password@localhost:5432/dbname
```

### System-level Environment Variables

**macOS/Linux** (add to `~/.zshrc` or `~/.bashrc`):
```bash
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"
export NOTION_API_KEY="secret_xxxxxxxxxxxx"
export POSTGRES_CONNECTION_STRING="postgresql://user:password@localhost:5432/dbname"
```

**Windows (PowerShell)** - User environment:
```powershell
[System.Environment]::SetEnvironmentVariable('GITHUB_TOKEN', 'ghp_xxxxxxxxxxxx', 'User')
[System.Environment]::SetEnvironmentVariable('NOTION_API_KEY', 'secret_xxxxxxxxxxxx', 'User')
```

**Windows (PowerShell)** - Session only:
```powershell
$env:GITHUB_TOKEN="ghp_xxxxxxxxxxxx"
$env:NOTION_API_KEY="secret_xxxxxxxxxxxx"
```

## Validation

Validate your configuration before using:

```bash
# macOS - Claude Desktop
python3 mcp-configs/scripts/validate-config.py ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Windows - Claude Desktop
python mcp-configs\scripts\validate-config.py "$env:APPDATA\Claude\claude_desktop_config.json"

# Project-level config
python3 mcp-configs/scripts/validate-config.py .mcp.json
```

**Expected output**:
```
OK: 4 server(s) configured
```

**If there are issues**:
```
Issues found:
  - Server 'github': contains placeholder values (YOUR_...)
```

## Testing MCP Servers

Test individual MCP servers before adding to configuration:

```bash
# Test filesystem server
npx -y @anthropic-ai/mcp-server-filesystem /tmp

# Test GitHub server (requires GITHUB_TOKEN)
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"
npx -y @anthropic-ai/mcp-server-github

# Test Postgres server (requires connection string)
export POSTGRES_CONNECTION_STRING="postgresql://..."
npx -y @anthropic-ai/mcp-server-postgres
```

## Restart Your AI Tool

After configuration:
1. **Claude Desktop**: Completely quit and restart the application
2. **Claude Code**: Restart the terminal/IDE
3. **Cursor**: Reload the window (`Cmd/Ctrl + Shift + P` → "Reload Window")

## Troubleshooting

### Common Issues

| Issue | Windows Fix | macOS Fix |
|-------|-------------|-----------|
| `npx` not found | Ensure Node.js is installed and in PATH. Use `npx.cmd` in config | Check `which npx`. Reinstall Node.js if needed |
| Permission denied | Run terminal as Administrator | Check file permissions: `chmod 644 config.json` |
| Server timeout | Check firewall rules, ensure MCP server package can be downloaded | Check network settings and npm registry |
| Config not loading | Verify file path is correct. Check JSON syntax | Verify file path. Escape spaces in paths |
| Environment variables not found | Restart terminal/app after setting env vars | Restart terminal. Check with `echo $GITHUB_TOKEN` |

### Platform-Specific Notes

**macOS**:
- Config paths with spaces need escaping: `~/Library/Application\ Support/Claude/`
- Use `open -a` to view configs: `open -a TextEdit config.json`
- Check console for errors: `Console.app` → Filter for "Claude"

**Windows**:
- Use PowerShell (not CMD) for better compatibility
- Paths can use forward slashes: `C:/Users/...` works too
- Check Event Viewer for application errors

### Validation Errors

**Invalid JSON**:
- Use a JSON validator (e.g., [jsonlint.com](https://jsonlint.com))
- Check for trailing commas (not allowed in JSON)
- Ensure all quotes are double quotes (`"`)

**Missing command/args**:
- Each server must have `command` and `args` fields
- Refer to `servers/custom-server-template.json` for structure

**Placeholder values detected**:
- Replace all `YOUR_*` values with actual data
- Example: `YOUR_USERNAME` → `kuro`
- Example: `YOUR_GITHUB_PAT` → `ghp_abc123...`

## Verify MCP is Working

1. Open your AI tool (Claude Desktop, Claude Code, or Cursor)
2. Start a new conversation
3. Check if MCP tools are available:
   - Claude Desktop: Look for server indicators in the UI
   - Claude Code: Use commands that require MCP access
4. Try using a tool:
   - "List files in my projects directory"
   - "Show my recent GitHub repositories"

## Next Steps

- **Customize server configurations**: Edit `mcp-configs/servers/*.json` to fit your needs
- **Add more servers**: Browse [Anthropic MCP Servers](https://github.com/anthropics/mcp-servers)
- **Create custom servers**: Use `servers/custom-server-template.json` as a starting point
- **Explore skills**: Check `claude-skills/mcp-management/` for advanced MCP utilities

## Getting Tokens

### GitHub Personal Access Token (PAT)

1. Go to [github.com/settings/tokens](https://github.com/settings/tokens)
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a name: "MCP Access"
4. Select scopes: `repo`, `read:org`, `read:user`
5. Click "Generate token"
6. Copy the token (starts with `ghp_`)

### Notion API Key

1. Go to [notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Click "New integration"
3. Give it a name and select workspace
4. Copy the "Internal Integration Token" (starts with `secret_`)
5. Share your Notion pages with the integration

## Support

For issues with:
- **This repository**: Check existing skills in `claude-skills/mcp-management/`
- **MCP protocol**: See [modelcontextprotocol.io](https://modelcontextprotocol.io)
- **Specific servers**: Check the [Anthropic MCP repository](https://github.com/anthropics/mcp-servers)
