# Claude Desktop MCP Configuration Templates

Platform-specific configuration templates for Claude Desktop.

## Files

- **claude_desktop_config.macos.json**: Configuration for macOS
- **claude_desktop_config.windows.json**: Configuration for Windows

## Configuration Location

### macOS
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

### Windows
```
%APPDATA%\Claude\claude_desktop_config.json
```

Or in PowerShell:
```powershell
$env:APPDATA\Claude\claude_desktop_config.json
```

## Usage

1. Copy the appropriate template for your platform
2. Place it in the correct location (see above)
3. Customize the configuration:
   - Replace `YOUR_USERNAME` with your actual username
   - Replace `YOUR_GITHUB_PAT` with your GitHub Personal Access Token
   - Update filesystem paths to match your project directories
   - Add or remove servers as needed

## Included MCP Servers

Both templates include:

- **Filesystem**: Access local files and directories
- **GitHub**: Interact with GitHub repositories
- **Postgres**: Database queries (optional, can be removed)
- **Notion**: Access Notion workspace (optional, can be removed)

## Platform Differences

| Aspect | macOS | Windows |
|--------|-------|---------|
| Command | `npx` | `npx.cmd` |
| Path separator | `/` | `\` or `/` |
| Home directory | `/Users/username` | `C:\Users\username` |

## After Setup

1. Restart Claude Desktop completely
2. Open a new conversation
3. Verify MCP servers are loaded (look for server indicators in UI)

## Troubleshooting

- Ensure Node.js is installed (`node --version`)
- Check JSON syntax is valid (no trailing commas)
- Verify environment variables are set
- Check Claude Desktop logs for errors

For more details, see [../../QUICK-SETUP.md](../../QUICK-SETUP.md)
