# Claude Code MCP Configuration Template

Project-level MCP configuration for Claude Code (CLI).

## File

- **mcp.json**: Project-level MCP configuration

## Configuration Locations

### Project-level (Recommended)
```bash
.mcp.json  # in your project root
```

### Global
```bash
# macOS/Linux
~/.claude/mcp.json

# Windows
%USERPROFILE%\.claude\mcp.json
```

## Usage

1. Copy `mcp.json` to your project root as `.mcp.json` (note the leading dot)
2. Customize the configuration:
   - Update filesystem paths as needed (`.` means current project)
   - Set environment variables for tokens
   - Add or remove servers based on your needs

## Included MCP Servers

- **Filesystem**: Access current project directory
- **GitHub**: Interact with GitHub repositories (requires GITHUB_TOKEN)

## Environment Variables

Claude Code can read environment variables. Set them before running:

```bash
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"
export NOTION_API_KEY="secret_xxxxxxxxxxxx"
```

Or use a `.env` file in your project (ensure it's in `.gitignore`).

## After Setup

1. Restart your terminal or reload the environment
2. Run your Claude Code commands
3. MCP servers will be available automatically

## Troubleshooting

- Ensure Node.js is installed
- Check that environment variables are set (`echo $GITHUB_TOKEN`)
- Verify JSON syntax
- Check Claude Code logs for errors

For more details, see [../../QUICK-SETUP.md](../../QUICK-SETUP.md)
