# Gemini CLI — MCP Server Setup Guide

Detailed guide for configuring Model Context Protocol (MCP) servers with Gemini CLI on Windows.

> **Main guide**: [README.md](./README.md)
> **Official reference**: [docs/tools/mcp-server.md](https://github.com/google-gemini/gemini-cli/blob/main/docs/tools/mcp-server.md)

---

## Table of Contents

1. [What Are MCP Servers?](#1-what-are-mcp-servers)
2. [Configuration Locations](#2-configuration-locations)
3. [Transport Types](#3-transport-types)
4. [Configuration Reference](#4-configuration-reference)
5. [Common MCP Servers](#5-common-mcp-servers)
6. [Session Commands](#6-session-commands)
7. [Creating Custom MCP Servers](#7-creating-custom-mcp-servers)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. What Are MCP Servers?

MCP (Model Context Protocol) is an open standard that connects AI systems with external tools and data sources. In Gemini CLI, MCP servers extend the agent with custom capabilities — databases, APIs, browser automation, file systems, and more.

Once configured, MCP tools appear alongside built-in tools and can be invoked by the model during conversations.

---

## 2. Configuration Locations

| Scope | Path | Purpose |
|---|---|---|
| **Global** | `~/.gemini/settings.json` | Available in all projects |
| **Project** | `.gemini/settings.json` | Project-specific, team-shared |
| **Extension** | `gemini-extension.json` | Bundled with an extension |

> [!TIP]
> Global settings apply everywhere. Project settings override global for that project.

---

## 3. Transport Types

MCP servers connect via three transport protocols:

| Transport | Property | When to Use |
|---|---|---|
| **Stdio** | `command` + `args` | Local tools, npm packages, Python scripts |
| **SSE** | `url` | Remote servers with Server-Sent Events |
| **HTTP Streaming** | `httpUrl` | Remote servers with HTTP streaming |

### Stdio Example (Local npm Package)

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-filesystem", "."]
    }
  }
}
```

### SSE Example (Remote Server)

```json
{
  "mcpServers": {
    "my-remote-tool": {
      "url": "http://localhost:8080/sse"
    }
  }
}
```

### HTTP Streaming Example

```json
{
  "mcpServers": {
    "my-http-tool": {
      "httpUrl": "http://localhost:8080/stream"
    }
  }
}
```

---

## 4. Configuration Reference

### Full Property Schema

| Property | Type | Required | Description |
|---|---|---|---|
| `command` | `string` | ✅ (stdio) | Path to the executable |
| `args` | `string[]` | — | Command-line arguments for the executable |
| `url` | `string` | ✅ (SSE) | SSE endpoint URL |
| `httpUrl` | `string` | ✅ (HTTP) | HTTP streaming endpoint URL |
| `env` | `object` | — | Environment variables passed to the server process |
| `cwd` | `string` | — | Working directory for the server process |
| `headers` | `object` | — | Custom HTTP headers for `url` or `httpUrl` |
| `timeout` | `number` | — | Timeout in milliseconds |
| `trust` | `boolean` | — | Whether the server is trusted (bypasses prompts) |

### Complete Example

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-github"],
      "env": {
        "GITHUB_TOKEN": "ghp_xxxxxxxxxxxx"
      },
      "timeout": 30000
    },
    "notion": {
      "url": "https://mcp.notion.com/mcp",
      "headers": {
        "Authorization": "Bearer ntn_xxxxxxxxxxxx"
      }
    }
  }
}
```

---

## 5. Common MCP Servers

### Development & Code

| Server | Install (args) | Purpose |
|---|---|---|
| **Filesystem** | `["-y", "@anthropic-ai/mcp-server-filesystem", "."]` | File system operations |
| **Playwright** | `["@playwright/mcp@latest"]` | Browser automation & testing |
| **Context7** | `["-y", "@upstash/context7-mcp"]` | Library documentation lookup |

### Productivity

| Server | Install (args) | Purpose |
|---|---|---|
| **GitHub** | `["-y", "@anthropic-ai/mcp-server-github"]` | PRs, issues, repos |
| **Slack** | `["-y", "@anthropic-ai/mcp-server-slack"]` | Channel messaging |
| **Notion** | SSE: `https://mcp.notion.com/mcp` | Notion workspace access |

### Data & AI

| Server | Install (args) | Purpose |
|---|---|---|
| **PostgreSQL** | `["-y", "@anthropic-ai/mcp-server-postgres", "postgresql://..."]` | Database queries |
| **Sequential Thinking** | `["-y", "@anthropic-ai/mcp-server-sequential-thinking"]` | Step-by-step reasoning |

### Full Template (Global `~/.gemini/settings.json`)

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
        "GITHUB_TOKEN": "ghp_xxxxxxxxxxxx"
      }
    },
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    }
  }
}
```

> [!NOTE]
> Unlike Claude Code's `.mcp.json`, Gemini CLI uses `settings.json` for MCP configuration. The `mcpServers` object is a top-level key in the settings file.

---

## 6. Session Commands

### MCP Management

| Command | Purpose |
|---|---|
| `/mcp` | List all connected MCP servers and their tools |
| `/mcp desc` | Show detailed descriptions of all MCP tools |

### Using MCP Tools

In a Gemini session, reference MCP tools with `@server-name`:

```
> @github List my open pull requests
> @playwright Navigate to localhost:3000 and take a screenshot
> @context7 Look up AG Grid column definition documentation
```

---

## 7. Creating Custom MCP Servers

You can build custom MCP servers using the MCP SDK (available in Python and TypeScript).

### Python MCP Server (Minimal Example)

```python
# my_server.py
from mcp.server import Server

app = Server("my-custom-tools")

@app.tool()
async def greet(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}!"

if __name__ == "__main__":
    import asyncio
    asyncio.run(app.run())
```

### Register in `settings.json`

```json
{
  "mcpServers": {
    "my-tools": {
      "command": "python",
      "args": ["C:\\path\\to\\my_server.py"]
    }
  }
}
```

> [!TIP]
> MCP servers can support rich multi-modal content and expose predefined prompts as new slash commands.

---

## 8. Troubleshooting

### Server Not Connecting

1. Verify the server command runs manually in PowerShell
2. Check that `node --version` returns v20+
3. Ensure `npx` can fetch the package (no proxy/firewall blocks)
4. Run `/mcp` in session to check connection status

### Server Timeout

Increase the `timeout` property:

```json
{
  "mcpServers": {
    "slow-server": {
      "command": "npx",
      "args": ["-y", "my-slow-server"],
      "timeout": 60000
    }
  }
}
```

### Tools Not Appearing

1. Check `/mcp` to verify the server is listed and connected
2. Use `/mcp desc` to see tool descriptions
3. Verify the server is exporting tools correctly
4. Restart the Gemini CLI session

### Windows-Specific Issues

| Issue | Solution |
|---|---|
| `npx` not found | Ensure Node.js v20+ is installed and in PATH |
| Firewall blocks | Allow `node.exe` through Windows Firewall |
| Path separators | Use forward slashes (`/`) or escaped backslashes (`\\`) in paths |

---

## Comparison: Gemini CLI vs Claude Code MCP Configuration

| Feature | Gemini CLI | Claude Code |
|---|---|---|
| **Config file** | `settings.json` (`mcpServers` key) | `.mcp.json` (standalone file) |
| **Config location (global)** | `~/.gemini/settings.json` | `~/.claude.json` |
| **Config location (project)** | `.gemini/settings.json` | `.mcp.json` (project root) |
| **CLI management** | Manual JSON editing | `claude mcp add/remove/list` |
| **Transport support** | Stdio, SSE, HTTP Streaming | Stdio, SSE |
| **Env var syntax** | Direct values in `env` | `${VAR}` expansion |
| **Trust/security** | `trust` property | Permission scopes |

---

## Quick Reference Links

| Resource | URL |
|---|---|
| MCP Server Integration | [docs/tools/mcp-server.md](https://github.com/google-gemini/gemini-cli/blob/main/docs/tools/mcp-server.md) |
| Settings & Configuration | [docs/get-started/configuration.md](https://github.com/google-gemini/gemini-cli/blob/main/docs/get-started/configuration.md) |
| Extensions Guide | [docs/extensions/index.md](https://github.com/google-gemini/gemini-cli/blob/main/docs/extensions/index.md) |
| MCP Protocol Spec | [modelcontextprotocol.io](https://modelcontextprotocol.io) |
| MCP Servers Catalog | [github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) |
