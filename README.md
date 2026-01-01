# AI Skills & MCP Configuration Repository

Centralized collection of AI assistant skills and MCP (Model Context Protocol) configurations for Claude, Codex, and Cursor with cross-platform support (Windows and macOS).

## Quick Start

**For MCP Setup**: See [mcp-configs/QUICK-SETUP.md](mcp-configs/QUICK-SETUP.md) for rapid configuration across different AI tools and platforms.

**For Skills**: Browse the `claude-skills/`, `codex-skills/`, or `cursor-rules/` directories for tool-specific capabilities.

## Repository Structure

```
skills_mcps/
├── mcp-configs/          # MCP configuration templates, servers, and setup scripts
├── claude-skills/        # Claude Code and Claude Desktop skills
├── codex-skills/         # OpenAI Codex skills and configurations
└── cursor-rules/         # Cursor IDE rules and configurations
```

## Platform Support

This repository is designed to work seamlessly on:
- **macOS**: Full support for all features
- **Windows**: Full support with platform-specific configurations

## MCP Configuration Hub

The `mcp-configs/` directory provides:
- **Ready-to-use templates** for Claude Desktop, Claude Code, and Cursor
- **Platform-specific configurations** for Windows and macOS
- **Automated setup scripts** for quick deployment
- **Common MCP server configs** (filesystem, GitHub, Postgres, Notion, etc.)
- **Validation tools** to ensure correct configuration

## Usage

### Setting Up MCP

1. Navigate to `mcp-configs/`
2. Follow instructions in `QUICK-SETUP.md`
3. Choose your tool (Claude Desktop, Claude Code, or Cursor)
4. Run the appropriate setup script or manually copy templates

### Using Skills

**Claude Skills**: Navigate to `claude-skills/` and refer to individual skill README files. See `claude-skills/CLAUDE.md` for interaction guidelines.

**Codex Skills**: Coming soon

**Cursor Rules**: Coming soon

## Directory Details

| Directory | Purpose |
|-----------|---------|
| `mcp-configs/` | Central hub for MCP configurations with templates, server configs, and automation scripts |
| `claude-skills/` | Skills for Claude Code and Claude Desktop, including MCP management utilities |
| `codex-skills/` | Skills and configurations for OpenAI Codex (planned) |
| `cursor-rules/` | Rules and configurations for Cursor IDE (planned) |

## Requirements

- **Node.js** v18+ (for MCP servers)
- **Git** (for repository management)
- **Python** 3.8+ (for validation scripts)

## Contributing

This is a private repository for personal use. If you have access and want to add skills or configurations, follow the existing structure and conventions.

## License

Private - All Rights Reserved
