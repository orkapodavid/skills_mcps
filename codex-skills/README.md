# Codex Skills

Codex CLI skills and configuration for OpenAI's Codex agent.

## Setup

### Config (`~/.codex/config.toml`)

```toml
approval_policy = "never"        # No approval prompts
sandbox_mode = "workspace-write" # Write to workspace, sandboxed otherwise
```

**CLI overrides** (highest precedence):
```sh
codex -a never "task"                              # no prompts
codex --yolo "task"                                # no sandbox + no prompts
codex -c approval_policy="never" -c sandbox_mode="workspace-write" "task"
```

### Skills (`~/.agents/skills/`)

Codex scans `$HOME/.agents/skills/` for user-level skills. Each skill is a directory with a `SKILL.md` file using YAML frontmatter:

```markdown
---
name: my-skill
description: When this skill should trigger
---
Instructions for Codex to follow.
```

**Installed skills** (symlinked from `claude-skills/`):

| Skill | Description |
|---|---|
| `uv-package-manager` | Python project management with uv |
| `reflex-dev` | Reflex Python web framework |
| `python-database-patterns` | SQLAlchemy, async DB, migrations |
| `data-pipeline-patterns` | ETL, Prefect workflows, data quality |

### MCP Servers (`~/.codex/config.toml`)

```toml
[mcp_servers.context7]
command = "npx"
args = ["-y", "@upstash/context7-mcp"]

[mcp_servers.brave-search]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-brave-search"]

[mcp_servers.playwright]
command = "npx"
args = ["@playwright/mcp@latest"]
```

Add servers via CLI: `codex mcp add <name> -- <command>`

## References

- [Config Basics](https://developers.openai.com/codex/config-basic/)
- [Agent Skills](https://developers.openai.com/codex/skills/)
- [MCP](https://developers.openai.com/codex/mcp/)
- [Security](https://developers.openai.com/codex/security)
- [Config Reference](https://developers.openai.com/codex/config-reference/)
