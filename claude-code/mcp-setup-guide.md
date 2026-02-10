# MCP Server Configuration — Claude Code on Windows

Step-by-step guide for configuring Model Context Protocol (MCP) servers with Claude Code on Windows 10 Pro.

> **Docs**: [docs.anthropic.com/.../mcp](https://docs.anthropic.com/en/docs/claude-code/mcp)

---

## Overview

MCP servers extend Claude Code with external tool access — databases, APIs, file systems, browsers, and more.

### What You Can Do

- Query databases (PostgreSQL, SQL Server)
- Interact with APIs (GitHub, Notion, Slack, Jira)
- Browse the web (Playwright)
- Search documentation (Context7)
- Access file systems
- Monitor errors (Sentry)

---

## Configuration Scopes

| Scope | Storage | Shared? | When to Use |
|---|---|---|---|
| **Project** | `.mcp.json` in project root | Git-tracked, team-shared | Project-specific tools |
| **Local** | `~/.claude.json` (per-project key) | Not shared | Personal/experimental per project |
| **User** | `~/.claude.json` (global key) | Not shared | Personal tools across all projects |
| **Managed** | `C:\Program Files\ClaudeCode\managed-mcp.json` | Admin-deployed | IT-managed, org-wide |

### Precedence: Managed > User > Project > Local

---

## Adding MCP Servers

### Method 1: CLI Commands (Recommended)

#### Add a Local stdio Server

```powershell
# Basic: context7 documentation search
claude mcp add --transport stdio context7 -- npx -y @upstash/context7-mcp

# With environment variables
claude mcp add --transport stdio github --env GITHUB_TOKEN=%GITHUB_TOKEN% -- npx -y @anthropic-ai/mcp-server-github

# With scope
claude mcp add --transport stdio playwright --scope project -- npx @playwright/mcp@latest

# With multiple args
claude mcp add --transport stdio filesystem -- npx -y @anthropic-ai/mcp-server-filesystem C:\projects
```

#### Add a Remote HTTP Server

```powershell
# Basic
claude mcp add --transport http notion https://mcp.notion.com/mcp

# With auth header
claude mcp add --transport http secure-api https://api.example.com/mcp --header "Authorization: Bearer YOUR_TOKEN"
```

#### Add a Remote SSE Server

```powershell
claude mcp add --transport sse asana https://mcp.asana.com/sse
```

#### Add from JSON Configuration

```powershell
claude mcp add-json weather-api '{"type":"http","url":"https://api.weather.com/mcp","headers":{"Authorization":"Bearer token"}}'
```

#### Import from Claude Desktop

```powershell
claude mcp add-from-claude-desktop
```

### Method 2: Edit `.mcp.json` Directly

Create/edit `.mcp.json` in your project root:

```json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["-y", "package-name"],
      "env": {
        "API_KEY": "${API_KEY}"
      }
    }
  }
}
```

---

## Managing Servers

```powershell
# List all configured servers
claude mcp list

# Get details for a specific server
claude mcp get github

# Remove a server
claude mcp remove github

# Reset project-scoped approval choices
claude mcp reset-project-choices
```

In-session:

```
/mcp
```

Shows server status, connected tools, and any errors.

---

## Environment Variable Expansion

`.mcp.json` supports env var expansion:

```json
{
  "mcpServers": {
    "api-server": {
      "type": "http",
      "url": "${API_BASE_URL:-https://api.example.com}/mcp",
      "headers": {
        "Authorization": "Bearer ${API_KEY}"
      }
    }
  }
}
```

| Syntax | Behavior |
|---|---|
| `${VAR}` | Expands to env var value |
| `${VAR:-default}` | Uses default if VAR not set |

Expansion works in: `command`, `args`, `env`, `url`, `headers`.

### Setting Environment Variables on Windows

```powershell
# Session only
$env:GITHUB_TOKEN = "ghp_xxxxxxxxxxxx"

# Persistent (user-level)
[System.Environment]::SetEnvironmentVariable('GITHUB_TOKEN', 'ghp_xxxxxxxxxxxx', 'User')
```

---

## Recommended MCP Server Stack

### Essential Servers

| Server | Package | Purpose |
|---|---|---|
| **Context7** | `@upstash/context7-mcp` | Documentation search (libraries, frameworks) |
| **GitHub** | `@anthropic-ai/mcp-server-github` | Repo management, PRs, issues |
| **Filesystem** | `@anthropic-ai/mcp-server-filesystem` | File access beyond project |
| **Playwright** | `@playwright/mcp@latest` | Browser automation & testing |

### Database Servers

| Server | Package | Purpose |
|---|---|---|
| **PostgreSQL** | `@anthropic-ai/mcp-server-postgres` | Query PostgreSQL databases |

### Productivity Servers

| Server | Package | Purpose |
|---|---|---|
| **Notion** | Remote HTTP: `https://mcp.notion.com/mcp` | Notion workspace access |

---

## Ready-to-Use Templates

### Minimal Project `.mcp.json`

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    }
  }
}
```

### Full-Stack Development `.mcp.json`

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-filesystem", "."]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    },
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```

### Data Engineering `.mcp.json`

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-postgres"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "${POSTGRES_CONNECTION_STRING}"
      }
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    }
  }
}
```

---

## Using Claude Code as an MCP Server

Claude Code itself can act as an MCP server for other tools:

```powershell
claude mcp serve
```

Config for another MCP client:

```json
{
  "mcpServers": {
    "claude-code": {
      "type": "stdio",
      "command": "claude",
      "args": ["mcp", "serve"],
      "env": {}
    }
  }
}
```

> [!NOTE]
> If you get `spawn claude ENOENT`, use the full path from `where claude`.

---

## MCP in Subagents

Give subagents dedicated MCP servers via their frontmatter:

```yaml
mcpServers:
  slack:
    type: http
    url: https://mcp.slack.com/mcp
    headers:
      Authorization: "Bearer ${SLACK_TOKEN}"
```

> [!WARNING]
> MCP servers are **not available** in background subagents.

---

## Troubleshooting

| Issue | Fix |
|---|---|
| `npx` not found | Ensure Node.js is in PATH. Restart terminal after install. |
| Server timeout | Check firewall rules. Ensure npm registry is reachable. |
| Config not loading | Verify `.mcp.json` is valid JSON. Check for trailing commas. |
| Env vars not expanding | Restart terminal after setting. Use correct `${VAR}` syntax. |
| Permission denied | Run terminal as Administrator if needed. |

### Validate Config

```powershell
# Check JSON syntax
python -c "import json; json.load(open('.mcp.json'))"

# In-session
/mcp
```

### Debug Server

```powershell
# Test a server manually
npx -y @upstash/context7-mcp
# If it starts without errors, the server is working
# Press Ctrl+C to stop
```
