# AGENTS.md - AI Assistant Guide

**Purpose**: This document helps AI assistants (LLMs) understand and effectively reuse this repository's structure, skills, and configurations.

## Repository Overview

This is a centralized collection of AI assistant skills and MCP (Model Context Protocol) configurations optimized for Claude, Codex, and Cursor with full cross-platform support (macOS and Windows).

**Key Capabilities**:
- Ready-to-use MCP server configurations and templates
- 14+ specialized Claude skills for development workflows
- Cross-platform setup automation scripts
- Skill creation and management utilities

## Quick Navigation

| Path | Purpose | When to Use |
|------|---------|-------------|
| `mcp-configs/` | MCP setup hub | Setting up MCP servers, validating configs |
| `claude-skills/` | Claude skills library | Python dev, testing, databases, web frameworks |
| `codex-skills/` | Codex skills (planned) | Future OpenAI Codex integrations |
| `cursor-rules/` | Cursor rules (planned) | Future Cursor IDE rules |

## Repository Structure

```
skills_mcps/
├── README.md                       # Main entry point
├── AGENTS.md                       # This file - LLM guide
├── SETUP-COMPLETE.md              # Setup history and git status
├── mcp-configs/                    # MCP Configuration Hub
│   ├── QUICK-SETUP.md             # Step-by-step setup guide
│   ├── README.md                  # MCP hub documentation
│   ├── templates/                 # Tool-specific configs
│   │   ├── claude-desktop/        # macOS & Windows templates
│   │   ├── claude-code/           # Project-level config
│   │   ├── cursor/                # Workspace config
│   │   └── codex/                 # Placeholder
│   ├── servers/                   # Reusable server configs
│   │   ├── filesystem.json        # Local file access
│   │   ├── github.json            # GitHub API integration
│   │   ├── postgres.json          # PostgreSQL database
│   │   ├── notion.json            # Notion workspace
│   │   └── custom-server-template.json
│   └── scripts/                   # Automation tools
│       ├── setup-mcp.sh           # macOS/Linux setup
│       ├── setup-mcp.ps1          # Windows PowerShell setup
│       └── validate-config.py     # Config validator
└── claude-skills/                  # Claude Skills Library
    ├── CLAUDE.md                  # Interaction guidelines
    ├── README.md                  # Skills overview
    ├── SKILL.md                   # Example skill format
    ├── EXAMPLES.md                # Comprehensive examples
    ├── plugin.json                # Claude plugin metadata
    ├── mcp-management/            # MCP server management tools
    ├── project-planner-skill/     # Project planning utilities
    ├── skill-creator/             # Skill creation tools
    ├── skill-installer/           # Skill installation utilities
    ├── pytest/                    # Testing patterns & examples
    ├── python-database-patterns/  # SQLAlchemy, async, migrations
    ├── python-packaging/          # Package management
    ├── async-python-patterns/     # Async/await patterns
    ├── data-pipeline-patterns/    # ETL, Prefect, data quality
    ├── reflex-dev/                # Reflex framework development
    ├── cli/                       # CLI development tools
    ├── microsoft-docs/            # Microsoft docs access
    ├── sqlserver-expert/          # SQL Server expertise
    ├── assets/                    # Shared templates
    ├── examples/                  # Working code examples
    ├── references/                # Technical documentation
    └── scripts/                   # Utility scripts
```

## MCP Configuration Hub (`mcp-configs/`)

### Purpose
Centralized hub for MCP server setup across multiple AI tools and platforms.

### Key Files
- **QUICK-SETUP.md**: Step-by-step instructions for MCP setup
- **README.md**: Comprehensive MCP documentation
- **templates/**: Platform-specific configuration templates
- **servers/**: Reusable server configurations (filesystem, GitHub, Postgres, Notion)
- **scripts/**: Automated setup and validation tools

### Configuration Locations

**Claude Desktop**:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

**Claude Code**:
- Project: `.mcp.json` in project root (recommended)
- Global: `~/.claude/mcp.json` (macOS) or `%USERPROFILE%\.claude\mcp.json` (Windows)

**Cursor**:
- Project: `.cursor/mcp.json` in project root

### Common Tasks

**Setup MCP for a tool**:
1. Read `mcp-configs/QUICK-SETUP.md`
2. Choose template from `templates/<tool-name>/`
3. Copy template to config location
4. Customize with credentials/paths
5. Validate with `python scripts/validate-config.py <config-file>`

**Add a new MCP server**:
1. Copy `servers/custom-server-template.json`
2. Configure command, args, and environment variables
3. Add to tool's configuration file
4. Set required environment variables

## Claude Skills Library (`claude-skills/`)

### Purpose
Collection of specialized skills for Claude Code and Claude Desktop covering Python development, testing, databases, web frameworks, and more.

### Skill Categories

**Development & Tooling**:
- `mcp-management/`: MCP server configuration and testing
- `cli/`: CLI application development
- `skill-creator/`: Create new skills with templates
- `skill-installer/`: Install skills from GitHub

**Python Development**:
- `pytest/`: Testing patterns, fixtures, mocking, async tests
- `python-database-patterns/`: SQLAlchemy, async DB, migrations, connection pooling
- `python-packaging/`: Package structure, dependencies, publishing
- `async-python-patterns/`: Async/await, asyncio, concurrent patterns

**Data & Pipelines**:
- `data-pipeline-patterns/`: ETL patterns, Prefect workflows, data quality checks
- `sqlserver-expert/`: T-SQL, stored procedures, Node.js integration

**Web Development**:
- `reflex-dev/`: Reflex framework (Python web apps with React-like syntax)
  - Comprehensive references for components, state, events, forms, tables, charts
  - Azure authentication integration
  - Enterprise patterns and best practices

**Project Management**:
- `project-planner-skill/`: Project planning, task breakdown, documentation generation

**Documentation Access**:
- `microsoft-docs/`: Microsoft documentation search and retrieval

### Skill Structure

Each skill directory typically contains:
- `SKILL.md` or `README.md`: Skill description and usage
- `scripts/`: Implementation scripts (Python, TypeScript, Shell)
- `references/`: Supporting technical documentation
- `assets/`: Templates, examples, configuration files
- `examples/`: Working code examples

### Key Resources

**CLAUDE.md**: Interaction guidelines for Claude Code
- Be extremely concise, sacrifice grammar for brevity
- No emojis
- Double-check and research, prioritize accuracy
- Suggest only necessary code changes
- Use `uv` instead of `pip`, use `uv run` instead of `python`
- Include unresolved questions at end of plans

**EXAMPLES.md**: Comprehensive skill examples (53KB of examples)

**references/**: Extensive technical documentation
- Reflex framework documentation (20+ `.mdc` files)
- Database patterns (SQLAlchemy, connection pooling, migrations)
- Data pipeline patterns (Prefect, PIT patterns, quality checks)
- MCP protocol and configuration guides

### Common Skill Usage Patterns

**Using a skill**:
1. Navigate to skill directory: `claude-skills/<skill-name>/`
2. Read `SKILL.md` or `README.md` for usage instructions
3. Check `references/` for detailed technical documentation
4. Review `examples/` for working code samples
5. Use `scripts/` for automation utilities

**Creating a new skill**:
1. Use `skill-creator/scripts/init_skill.py` to scaffold new skill
2. Follow existing skill structure
3. Add SKILL.md with description and examples
4. Include scripts, references, and assets as needed
5. Validate with `skill-creator/scripts/quick_validate.py`

**Installing external skills**:
1. Use `skill-installer/scripts/install-skill-from-github.py`
2. List curated skills: `skill-installer/scripts/list-curated-skills.py`

## Tech Stack & Requirements

**Languages**:
- Python 3.8+ (skills, scripts, validation)
- TypeScript/Node.js 18+ (MCP servers, management tools)
- Shell/PowerShell (setup automation)

**Key Technologies**:
- MCP (Model Context Protocol)
- SQLAlchemy (async database patterns)
- Pytest (testing framework)
- Prefect (data pipelines)
- Reflex (web framework)
- Node.js `mssql` package (SQL Server)

**Tools**:
- `uv` (Python package manager - preferred over pip)
- Git (version control)
- npx/npx.cmd (MCP server execution)

## Development Workflows

### Setting Up MCP for Development

```bash
# Navigate to MCP configs
cd mcp-configs

# Run setup script (macOS/Linux)
./scripts/setup-mcp.sh

# Or Windows
.\scripts\setup-mcp.ps1

# Validate configuration
python scripts/validate-config.py <config-file>
```

### Creating a New Skill

```bash
# Use skill creator
cd claude-skills/skill-creator
uv run scripts/init_skill.py

# Or manually create structure
mkdir claude-skills/my-new-skill
cd claude-skills/my-new-skill
mkdir scripts references assets
touch SKILL.md README.md
```

### Testing MCP Servers

Use `mcp-management/` skill for:
- Testing MCP server connectivity
- Validating server configurations
- Managing server lifecycle
- Debugging server issues

### Working with Databases

Use `python-database-patterns/` for:
- Async SQLAlchemy patterns
- Connection pooling setup
- Alembic migrations
- Transaction management

See `assets/alembic.ini.template` for migration configuration.

### Building Web Apps with Reflex

Use `reflex-dev/` for comprehensive patterns:
- State management and event handlers
- Form validation and data tables
- Azure authentication integration
- AG Grid and AG Charts integration
- Enterprise patterns and best practices

Check `references/` for detailed component documentation.

## Platform-Specific Considerations

### macOS
- Use `npx` in MCP configurations
- Paths use forward slashes (`/`)
- Config location: `~/Library/Application Support/`
- Scripts: `.sh` files

### Windows
- Use `npx.cmd` in MCP configurations
- Paths use backslashes (`\`) or forward slashes
- Config location: `%APPDATA%`
- Scripts: `.ps1` files

### Cross-Platform Best Practices
- Use `.gitattributes` for line ending normalization (already configured)
- Test scripts on both platforms
- Use path utilities for dynamic path handling
- Set environment variables appropriately per platform

## Environment Variables

Common environment variables for MCP servers:

```bash
# GitHub
GITHUB_TOKEN="ghp_xxxxxxxxxxxx"

# Notion
NOTION_API_KEY="secret_xxxxxxxxxxxx"

# PostgreSQL
POSTGRES_CONNECTION_STRING="postgresql://user:password@localhost:5432/dbname"

# SQL Server (for Node.js mssql)
SQL_USER="username"
SQL_PASSWORD="password"
SQL_SERVER="localhost"
SQL_DATABASE="dbname"
```

## File Naming Conventions

- **Skills**: `SKILL.md` (skill definition), `README.md` (usage guide)
- **Scripts**: `snake_case.py`, `kebab-case.sh`, `PascalCase.ps1`
- **Configs**: `kebab-case.json`, `config.yaml`
- **Templates**: `template-name.template`, `*.md.template`
- **Documentation**: `UPPERCASE.md` (root), `kebab-case.md` (references)

## Git Configuration

- **`.gitignore`**: Excludes `.DS_Store`, `__pycache__`, `node_modules/`, `.env`, etc.
- **`.gitattributes`**: Normalizes line endings across platforms
- **Branch**: `main` (or `master`)
- **Visibility**: Private repository

## Common AI Assistant Tasks

### Task: Set up MCP for Claude Desktop on macOS
1. Read `mcp-configs/QUICK-SETUP.md`
2. Copy `mcp-configs/templates/claude-desktop/claude_desktop_config.macos.json`
3. Install to `~/Library/Application Support/Claude/claude_desktop_config.json`
4. Customize server configurations and credentials
5. Restart Claude Desktop

### Task: Create a new Python skill
1. Use `claude-skills/skill-creator/scripts/init_skill.py`
2. Follow prompts to scaffold skill structure
3. Edit generated `SKILL.md` with description and examples
4. Add implementation scripts to `scripts/`
5. Validate with `quick_validate.py`

### Task: Add async database support to project
1. Reference `claude-skills/python-database-patterns/`
2. Read `references/sqlalchemy-async.md` for patterns
3. Copy `assets/alembic.ini.template` for migrations
4. Review `references/connection-pooling.md` for pool configuration
5. Implement using documented patterns

### Task: Build Reflex web application
1. Reference `claude-skills/reflex-dev/`
2. Check `examples/` for starter templates
3. Read relevant references (e.g., `reflex-state-model.mdc`, `reflex-forms.mdc`)
4. Review `references/patterns.md` for best practices
5. Implement components using documented patterns

### Task: Write pytest tests
1. Reference `claude-skills/pytest/`
2. Read `SKILL.md` for testing patterns
3. Check `EXAMPLES.md` for test examples
4. Use fixtures, parametrization, and async patterns as documented
5. Run tests with `uv run pytest`

## Troubleshooting

### MCP Server Not Working
1. Validate config: `python mcp-configs/scripts/validate-config.py <config>`
2. Check environment variables are set
3. Verify server command exists (e.g., `npx` or `npx.cmd`)
4. Check server logs in tool's diagnostic panel
5. Use `mcp-management/` skill for debugging

### Skill Not Loading
1. Verify skill structure matches convention
2. Check `SKILL.md` exists and is properly formatted
3. Ensure scripts have correct permissions
4. Validate with `skill-creator/scripts/quick_validate.py`

### Cross-Platform Issues
1. Check path separators (use platform-appropriate)
2. Verify line endings (`.gitattributes` should handle this)
3. Use `npx.cmd` on Windows, `npx` on macOS/Linux
4. Check environment variable syntax per platform

## Best Practices for AI Assistants

1. **Read skill documentation first**: Always check `SKILL.md` or `README.md` before using a skill
2. **Use references**: Extensive documentation in `references/` directories
3. **Follow conventions**: Adhere to established file naming and structure patterns
4. **Validate configurations**: Always validate MCP configs before deployment
5. **Be platform-aware**: Use appropriate commands and paths for target platform
6. **Prefer `uv` over `pip`**: Use `uv` for Python package management when possible
7. **Be concise**: Follow `CLAUDE.md` guidelines - sacrifice grammar for brevity, no emojis
8. **Check examples**: Review working examples before implementing new features
9. **Leverage templates**: Use provided templates in `assets/` directories
10. **Update memory**: When encountering new patterns, update repository knowledge

## Key Insight Patterns

**When user asks about MCP setup**:
→ Direct to `mcp-configs/QUICK-SETUP.md` and relevant templates

**When user needs database patterns**:
→ Use `claude-skills/python-database-patterns/` with references

**When user wants to build web apps**:
→ Use `claude-skills/reflex-dev/` with comprehensive component docs

**When user needs testing help**:
→ Use `claude-skills/pytest/` with examples and patterns

**When user wants to create skills**:
→ Use `claude-skills/skill-creator/` with scaffolding scripts

**When user encounters SQL Server tasks**:
→ Use `claude-skills/sqlserver-expert/` for T-SQL and Node.js patterns

## Additional Resources

- **Main README**: `/README.md` - Repository overview
- **Setup Guide**: `/SETUP-COMPLETE.md` - Git setup and push instructions
- **MCP Quick Setup**: `/mcp-configs/QUICK-SETUP.md` - MCP configuration guide
- **Claude Guidelines**: `/claude-skills/CLAUDE.md` - Interaction preferences
- **Skill Examples**: `/claude-skills/EXAMPLES.md` - 53KB of comprehensive examples

## Version Information

- **Repository Status**: Ready for use, git initialized
- **Total Files**: 246+ files tracked
- **Total Skills**: 14 Claude skills
- **Supported Platforms**: macOS, Windows
- **Supported Tools**: Claude Desktop, Claude Code, Cursor (planned: Codex)
- **Last Updated**: January 1, 2026

---

**For LLMs**: This repository is optimized for reuse. Always read relevant skill documentation, use provided templates, validate configurations, and follow established conventions. Prioritize accuracy and conciseness in all interactions.
