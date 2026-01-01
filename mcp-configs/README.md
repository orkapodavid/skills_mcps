# MCP Configuration Hub

This directory contains ready-to-use MCP (Model Context Protocol) configuration templates, server configurations, setup scripts, and validation tools for quickly setting up MCP across different AI tools and platforms.

## Directory Structure

```
mcp-configs/
├── README.md (this file)
├── QUICK-SETUP.md              # Step-by-step setup guide
├── templates/                  # Tool-specific configuration templates
│   ├── claude-desktop/         # Claude Desktop configs for macOS and Windows
│   ├── claude-code/            # Claude Code project-level configs
│   ├── cursor/                 # Cursor workspace configs
│   └── codex/                  # Codex configs (placeholder)
├── servers/                    # Reusable MCP server configurations
│   ├── filesystem.json
│   ├── github.json
│   ├── postgres.json
│   ├── notion.json
│   └── custom-server-template.json
└── scripts/                    # Automation and validation
    ├── setup-mcp.sh            # macOS/Linux setup script
    ├── setup-mcp.ps1           # Windows PowerShell setup script
    └── validate-config.py      # Configuration validation utility
```

## Quick Start

1. **Read the setup guide**: Start with [QUICK-SETUP.md](QUICK-SETUP.md)
2. **Choose your tool**: Claude Desktop, Claude Code, or Cursor
3. **Run setup script** (recommended):
   - macOS/Linux: `./scripts/setup-mcp.sh`
   - Windows: `.\scripts\setup-mcp.ps1`
4. **Or manually copy**: Copy appropriate template from `templates/` to your config location
5. **Customize**: Edit copied config to add your credentials and paths
6. **Validate**: Run `python scripts/validate-config.py <your-config-file>`

## Supported MCP Servers

| Server | Purpose | Configuration File |
|--------|---------|-------------------|
| Filesystem | Access local files and directories | `servers/filesystem.json` |
| GitHub | Interact with GitHub repositories and APIs | `servers/github.json` |
| Postgres | Query and manage PostgreSQL databases | `servers/postgres.json` |
| Notion | Access Notion workspace | `servers/notion.json` |
| Custom | Template for adding new servers | `servers/custom-server-template.json` |

## Configuration Locations by Tool

### Claude Desktop

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### Claude Code

- **Project-level**: `.mcp.json` in project root (recommended)
- **Global**: `~/.claude/mcp.json` (macOS) or `%USERPROFILE%\.claude\mcp.json` (Windows)

### Cursor

- **Project-level**: `.cursor/mcp.json` in project root

## Platform-Specific Notes

### macOS
- Use `npx` command in configurations
- Paths use forward slashes (`/`)
- Config files in `~/Library/Application Support/`

### Windows
- Use `npx.cmd` command in configurations
- Paths use backslashes (`\`) or forward slashes
- Config files in `%APPDATA%` directory

## Available Templates

| Template | Platform | Description |
|----------|----------|-------------|
| `templates/claude-desktop/claude_desktop_config.macos.json` | macOS | Claude Desktop with common MCP servers |
| `templates/claude-desktop/claude_desktop_config.windows.json` | Windows | Claude Desktop with common MCP servers |
| `templates/claude-code/mcp.json` | Both | Claude Code project-level config |
| `templates/cursor/mcp.json` | Both | Cursor workspace config |

## Environment Variables

Many MCP servers require credentials. Set these as environment variables:

```bash
# GitHub
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"

# Notion
export NOTION_API_KEY="secret_xxxxxxxxxxxx"

# Postgres
export POSTGRES_CONNECTION_STRING="postgresql://user:password@localhost:5432/dbname"
```

**Windows (PowerShell)**:
```powershell
$env:GITHUB_TOKEN="ghp_xxxxxxxxxxxx"
```

## Validation

Before using your configuration, validate it:

```bash
python scripts/validate-config.py ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

The validator checks for:
- Valid JSON syntax
- Required fields (`command`, `args`)
- Placeholder values that need customization
- Proper structure

## Troubleshooting

See [QUICK-SETUP.md](QUICK-SETUP.md) for common issues and solutions.

## Adding Custom MCP Servers

1. Copy `servers/custom-server-template.json`
2. Configure with your server's command and arguments
3. Add to your tool's configuration file
4. Set any required environment variables
5. Restart your AI tool

## Further Reading

- [MCP Documentation](https://modelcontextprotocol.io/)
- [Anthropic MCP Servers](https://github.com/anthropics/mcp-servers)
