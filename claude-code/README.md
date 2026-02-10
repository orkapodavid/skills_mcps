# Claude Code — Windows 10 Pro Setup Guide

Complete step-by-step guide for setting up Claude Code locally on Windows 10 Pro with **multi-agent/subagent workflows**, **skills**, and **MCP server** configuration.

> **Source**: [docs.anthropic.com/en/docs/claude-code](https://docs.anthropic.com/en/docs/claude-code/overview)

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Install Claude Code](#2-install-claude-code)
3. [Authentication](#3-authentication)
4. [Project Initialization](#4-project-initialization)
5. [CLAUDE.md — Project Constitution](#5-claudemd--project-constitution)
6. [Settings & Permissions](#6-settings--permissions)
7. [MCP Server Configuration](#7-mcp-server-configuration)
8. [Skills System](#8-skills-system)
9. [Subagents & Multi-Agent Workflows](#9-subagents--multi-agent-workflows)
10. [Hooks](#10-hooks)
11. [Verification Checklist](#11-verification-checklist)

---

## 1. Prerequisites

| Requirement | Install Command | Verify |
|---|---|---|
| **Node.js v18+** | `winget install OpenJS.NodeJS` | `node --version` |
| **Git** | `winget install Git.Git` | `git --version` |
| **Python 3.10+** | `winget install Python.Python.3.12` | `python --version` |
| **Claude Subscription** | [claude.com/pricing](https://claude.com/pricing) — Pro, Max, Teams, or Enterprise | — |

> [!NOTE]
> API key with active billing on [console.anthropic.com](https://console.anthropic.com) also works.

---

## 2. Install Claude Code

Choose **one** method:

### Option A: PowerShell (Recommended)

```powershell
irm https://claude.ai/install.ps1 | iex
```

### Option B: Command Prompt

```cmd
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd
```

### Option C: WinGet

```powershell
winget install Anthropic.ClaudeCode
```

> [!IMPORTANT]
> WinGet does **not** auto-update. Run `winget upgrade Anthropic.ClaudeCode` manually.

### Verify Installation

```powershell
claude --version
```

---

## 3. Authentication

```powershell
claude
# Follow the browser-based OAuth flow to authenticate
```

Or use an API key:

```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-..."
claude
```

For persistent API key (User-level env var):

```powershell
[System.Environment]::SetEnvironmentVariable('ANTHROPIC_API_KEY', 'sk-ant-...', 'User')
```

---

## 4. Project Initialization

```powershell
cd C:\path\to\your\project
claude
```

Inside the Claude Code session:

```
/init
```

This generates a `CLAUDE.md` file with project context. It also creates the `.claude/` directory structure.

### Directory Structure Created

```
your-project/
├── CLAUDE.md                        # Project constitution
├── .claude/
│   ├── settings.json                # Project settings (git-tracked)
│   ├── settings.local.json          # Local settings (git-ignored)
│   ├── agents/                      # Project subagents
│   └── skills/                      # Project skills
├── .mcp.json                        # Project MCP servers
```

---

## 5. CLAUDE.md — Project Constitution

`CLAUDE.md` is the **primary context file** that Claude reads at the start of every session. Place it in your project root.

```markdown
# Project Name

## Tech Stack
- Python 3.12 with uv package manager
- Reflex framework for web UI
- SQLAlchemy for database

## Conventions
- Use `uv` instead of `pip`
- Use `uv run` instead of `python`
- Follow PEP 8 naming conventions
- Type hints required on all functions

## Architecture
- `app/` — main application code
- `tests/` — pytest test suite
- `docs/` — documentation

## Important Notes
- Never commit `.env` files
- Always run tests before committing: `uv run pytest`
```

### CLAUDE.md Hierarchy

| Scope | Location | Purpose |
|---|---|---|
| **User** | `~/.claude/CLAUDE.md` | Personal preferences across all projects |
| **Project** | `./CLAUDE.md` | Project-specific context (git-tracked) |
| **Nested** | `./src/CLAUDE.md` | Subdirectory-specific context |

---

## 6. Settings & Permissions

### Settings File Locations

| Scope | Path | Purpose |
|---|---|---|
| **User** | `%USERPROFILE%\.claude\settings.json` | Global settings for all projects |
| **Project** | `.claude\settings.json` | Team-shared project settings |
| **Local** | `.claude\settings.local.json` | Personal project overrides (git-ignored) |
| **Managed** | `C:\Program Files\ClaudeCode\managed-settings.json` | IT-admin controlled |

### Example `settings.json`

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [
      "Bash(npm run lint)",
      "Bash(npm run test *)",
      "Bash(uv run pytest *)",
      "Read(~/.zshrc)"
    ],
    "deny": [
      "Bash(curl *)",
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)"
    ]
  }
}
```

### Useful In-Session Commands

| Command | Purpose |
|---|---|
| `/init` | Generate CLAUDE.md |
| `/permissions` | Manage tool permissions |
| `/mcp` | Check MCP server status |
| `/agents` | Manage subagents |
| `/hooks` | Manage hooks |
| `/statusline` | Show active subagents |
| `/compact` | Compact context window |

---

## 7. MCP Server Configuration

> **Full guide**: [mcp-setup-guide.md](./mcp-setup-guide.md)

### Configuration Scopes

| Scope | Location | When to Use |
|---|---|---|
| **Project** | `.mcp.json` (project root) | Team-shared servers, git-tracked |
| **Local** | Stored in `~/.claude.json` | Personal/experimental, per-project |
| **User** | Stored in `~/.claude.json` | Personal utilities, all projects |

### Quick MCP Setup via CLI

```powershell
# Add a stdio server (local)
claude mcp add --transport stdio context7 -- npx -y @upstash/context7-mcp

# Add an HTTP server
claude mcp add --transport http notion https://mcp.notion.com/mcp

# Add with scope
claude mcp add --transport stdio playwright --scope project -- npx @playwright/mcp@latest

# Add with environment variables
claude mcp add --transport stdio github --env GITHUB_TOKEN=$env:GITHUB_TOKEN -- npx -y @anthropic-ai/mcp-server-github

# List, get, remove
claude mcp list
claude mcp get github
claude mcp remove github
```

### Project `.mcp.json` Template

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

> [!TIP]
> Use `${ENV_VAR}` syntax in `.mcp.json` for environment variable expansion.
> Use `${VAR:-default}` for fallback values.

---

## 8. Skills System

> **Full guide**: [skills-guide.md](./skills-guide.md)

Skills are reusable instruction packages in `SKILL.md` files that extend Claude's capabilities.

### Skills Directory Locations

| Scope | Path |
|---|---|
| **User** | `%USERPROFILE%\.claude\skills\<skill-name>\SKILL.md` |
| **Project** | `.claude\skills\<skill-name>\SKILL.md` |

### Quick Create a Skill

```powershell
# Create skill directory
mkdir -p $env:USERPROFILE\.claude\skills\my-skill

# Create SKILL.md
notepad $env:USERPROFILE\.claude\skills\my-skill\SKILL.md
```

### SKILL.md Format

```markdown
---
name: deploy-app
description: Deploy the application to production
context: fork
allowed-tools: Bash, Read
---

Deploy the application:
1. Run the test suite: `uv run pytest`
2. Build the application: `uv run build`
3. Push to the deployment target
```

### Key Frontmatter Fields

| Field | Purpose |
|---|---|
| `name` | Skill identifier (also used as `/slash-command`) |
| `description` | When to use this skill (Claude reads this) |
| `context: fork` | Run in isolated subagent context |
| `disable-model-invocation: true` | Only triggered by `/name`, not auto-invoked |
| `allowed-tools` | Restrict available tools |
| `model` | Override model (sonnet, opus, haiku) |
| `argument-hint` | Hint text for arguments, e.g. `[filename]` |

### Skill Directory Structure

```
my-skill/
├── SKILL.md           # Main instructions (required)
├── template.md        # Template for Claude to fill in
├── examples/
│   └── sample.md      # Example output
└── scripts/
    └── helper.py      # Utility script Claude can execute
```

---

## 9. Subagents & Multi-Agent Workflows

> **Full guides**: [subagents-guide.md](./subagents-guide.md) · [multi-agents-guide.md](./multi-agents-guide.md)

### Built-in Subagents

| Subagent | Model | Tools | Purpose |
|---|---|---|---|
| **Explore** | Haiku (fast) | Read-only | File discovery, code search |
| **Plan** | Inherited | Read-only | Codebase research for planning |
| **General-purpose** | Inherited | All tools | Complex research, code modifications |

### Create Custom Subagents

#### Option A: Interactive (`/agents` command)

```
/agents
```

Follow the wizard to create, edit, or delete subagents.

#### Option B: Manual File (`.claude/agents/<name>.md`)

```markdown
---
name: code-reviewer
description: Expert code review specialist. Use immediately after writing or modifying code.
tools: Read, Grep, Glob, Bash
model: sonnet
permissionMode: default
memory: project
---

You are a senior code reviewer. When invoked:
1. Run `git diff` to see recent changes
2. Focus on modified files
3. Review for quality, security, and best practices

Provide feedback by priority:
- **Critical** (must fix)
- **Warnings** (should fix)
- **Suggestions** (consider improving)
```

### Subagent Scope

| Scope | Location |
|---|---|
| **User** (all projects) | `%USERPROFILE%\.claude\agents\` |
| **Project** (team-shared) | `.claude\agents\` |

### Supported Frontmatter Fields

| Field | Values | Purpose |
|---|---|---|
| `name` | string | Identifier |
| `description` | string | When to delegate (Claude reads this) |
| `tools` | Read, Write, Edit, Bash, Grep, Glob, Task, etc. | Allowed tools |
| `disallowedTools` | Same as above | Explicitly denied tools |
| `model` | `sonnet`, `opus`, `haiku`, `inherit` | AI model |
| `permissionMode` | `default`, `acceptEdits`, `dontAsk`, `delegate`, `bypassPermissions`, `plan` | Permission behavior |
| `skills` | List of skill names | Preloaded skills |
| `mcpServers` | MCP server config | Dedicated MCP servers |
| `hooks` | Hook config | Lifecycle hooks |
| `memory` | `user`, `project`, `local` | Persistent memory |
| `maxTurns` | number | Max conversation turns |

### Multi-Agent Workflow Patterns

#### Pattern 1: Isolate High-Volume Operations

```
Use a subagent to run the test suite and report only the failing tests
```

#### Pattern 2: Parallel Research

```
Research the authentication, database, and API modules in parallel using separate subagents
```

#### Pattern 3: Chain Subagents

```
Use the code-reviewer subagent to find issues, then use the debugger subagent to fix them
```

#### Pattern 4: Coordinator Agent

```markdown
---
name: coordinator
description: Coordinates work across specialized agents
tools: Task(worker, researcher), Read, Bash
---
```

### Foreground vs Background

| Mode | Behavior |
|---|---|
| **Foreground** | Blocks main conversation. Permission prompts pass through. |
| **Background** | Runs concurrently. Press `Ctrl+B` to background a running task. MCP tools not available. |

---

## 10. Hooks

Hooks run custom scripts at specific lifecycle events.

### Hook Configuration Location

Configured in `settings.json` (user, project, or local scope).

### Example: Auto-format After File Changes

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/format.ps1",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

### Available Hook Events

| Event | When it Fires |
|---|---|
| `SessionStart` | When Claude Code session begins |
| `UserPromptSubmit` | When user submits a prompt |
| `PreToolUse` | Before a tool is used |
| `PostToolUse` | After a tool is used |
| `PostToolUseFailure` | After a tool use fails |
| `SubagentStart` | When a subagent starts |
| `SubagentStop` | When a subagent stops |
| `Stop` | When Claude finishes responding |
| `PreCompact` | Before context compaction |
| `SessionEnd` | When session ends |

### In-Session Hook Management

```
/hooks
```

---

## 11. Verification Checklist

Run through this after setup to confirm everything works:

- [ ] `claude --version` outputs a version number
- [ ] `claude` opens a session and authenticates
- [ ] `/init` creates or updates `CLAUDE.md`
- [ ] `/mcp` shows all configured MCP servers as connected
- [ ] `/agents` lists built-in + custom subagents
- [ ] Test a skill: `/your-skill-name`
- [ ] Test a subagent: "Use the code-reviewer subagent on this file"
- [ ] Test MCP: "List my GitHub repositories" (if GitHub MCP configured)

---

## Quick Reference Links

| Resource | URL |
|---|---|
| Claude Code Docs | [docs.anthropic.com/en/docs/claude-code](https://docs.anthropic.com/en/docs/claude-code/overview) |
| Subagents | [docs.anthropic.com/.../sub-agents](https://docs.anthropic.com/en/docs/claude-code/sub-agents) |
| Skills | [docs.anthropic.com/.../skills](https://docs.anthropic.com/en/docs/claude-code/skills) |
| MCP | [docs.anthropic.com/.../mcp](https://docs.anthropic.com/en/docs/claude-code/mcp) |
| Hooks | [docs.anthropic.com/.../hooks](https://docs.anthropic.com/en/docs/claude-code/hooks) |
| Settings | [docs.anthropic.com/.../settings](https://docs.anthropic.com/en/docs/claude-code/settings) |
| MCP Servers Catalog | [github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) |

---

## File Index (This Folder)

| File | Purpose |
|---|---|
| [README.md](./README.md) | This guide — main setup walkthrough |
| [subagents-guide.md](./subagents-guide.md) | Detailed subagent configuration & examples |
| [multi-agents-guide.md](./multi-agents-guide.md) | Multi-agent workflows: subagents + agent teams |
| [skills-guide.md](./skills-guide.md) | Skills system deep dive |
| [mcp-setup-guide.md](./mcp-setup-guide.md) | MCP configuration for Windows |
| [templates/](./templates/) | Ready-to-use config templates |
