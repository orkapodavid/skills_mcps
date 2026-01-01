# Cursor MCP Configuration Template

Project-level MCP configuration for Cursor IDE.

## File

- **mcp.json**: Cursor workspace MCP configuration

## Configuration Location

```bash
.cursor/mcp.json  # in your project root
```

## Usage

1. Create `.cursor` directory in your project root
2. Copy `mcp.json` to `.cursor/mcp.json`
3. Customize the configuration:
   - Update filesystem paths as needed
   - Set environment variables for tokens
   - Add or remove servers based on your needs

## Included MCP Servers

- **Filesystem**: Access current project directory
- **GitHub**: Interact with GitHub repositories (requires GITHUB_TOKEN)

## Environment Variables

Set environment variables before opening Cursor:

```bash
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"
```

## After Setup

1. Reload Cursor window: `Cmd/Ctrl + Shift + P` → "Reload Window"
2. MCP servers should be available in Cursor's AI features

## Troubleshooting

- Ensure Node.js is installed
- Check that `.cursor` directory exists
- Verify JSON syntax
- Reload Cursor window after config changes

For more details, see [../../QUICK-SETUP.md](../../QUICK-SETUP.md)
