# Gemini CLI — Windows Setup & Agent Guide

Complete step-by-step guide for setting up Gemini CLI on Windows with **agent mode**, **GEMINI.md context**, **MCP server integration**, and **extensions**.

> **Source**: [github.com/google-gemini/gemini-cli](https://github.com/google-gemini/gemini-cli) · [geminicli.com/docs](https://geminicli.com/docs/)

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Installation](#2-installation)
3. [Authentication](#3-authentication)
4. [Getting Started](#4-getting-started)
5. [GEMINI.md — Project Context](#5-geminimd--project-context)
6. [Settings & Configuration](#6-settings--configuration)
7. [Built-in Tools](#7-built-in-tools)
8. [Sandbox & Approval Modes](#8-sandbox--approval-modes)
9. [MCP Server Configuration](#9-mcp-server-configuration)
10. [Extensions](#10-extensions)
11. [Slash Commands & Keyboard Shortcuts](#11-slash-commands--keyboard-shortcuts)
12. [Headless Mode (Scripting)](#12-headless-mode-scripting)
13. [IDE Integration](#13-ide-integration)
14. [Verification Checklist](#14-verification-checklist)

---

## 1. Prerequisites

| Requirement | Install Command | Verify |
|---|---|---|
| **Node.js v20+** | `winget install OpenJS.NodeJS` | `node --version` |
| **npm** | Bundled with Node.js | `npm --version` |
| **Git** | `winget install Git.Git` | `git --version` |
| **Google Account** | [accounts.google.com](https://accounts.google.com) | — |

> [!NOTE]
> Node.js v20 or higher is required. The Gemini CLI is an npm package and runs on macOS, Linux, and Windows.

---

## 2. Installation

Choose **one** method:

### Option A: Global npm Install (Recommended)

```powershell
npm install -g @google/gemini-cli
```

### Option B: Run Without Installing (npx)

```powershell
npx @google/gemini-cli
```

### Option C: Anaconda (Restricted Environments)

```powershell
conda create -y -n gemini_env -c conda-forge nodejs
conda activate gemini_env
npm install -g @google/gemini-cli
```

### Verify Installation

```powershell
gemini --version
```

> [!TIP]
> On macOS/Linux, Homebrew (`brew install gemini-cli`) and MacPorts (`sudo port install gemini-cli`) are also available.

---

## 3. Authentication

Launch Gemini CLI and choose an authentication method:

```powershell
gemini
```

### Option 1: Login with Google (Recommended)

Follow the browser-based OAuth flow when prompted. This is the **easiest** method.

**Free tier limits:**
- 60 requests/min, 1,000 requests/day
- Gemini 3 models with 1M token context window
- No API key management required

### Option 2: Gemini API Key

Get a key from [Google AI Studio](https://aistudio.google.com/apikey):

```powershell
# Set for current session
$env:GEMINI_API_KEY = "YOUR_API_KEY"
gemini
```

For persistent API key (User-level env var):

```powershell
[System.Environment]::SetEnvironmentVariable('GEMINI_API_KEY', 'YOUR_API_KEY', 'User')
```

### Option 3: Vertex AI (Enterprise)

```powershell
$env:GOOGLE_API_KEY = "YOUR_API_KEY"
$env:GOOGLE_GENAI_USE_VERTEXAI = "true"
gemini
```

For organization projects with Code Assist License:

```powershell
$env:GOOGLE_CLOUD_PROJECT = "YOUR_PROJECT_ID"
gemini
```

---

## 4. Getting Started

### Basic Usage

```powershell
# Start in current directory
cd C:\path\to\your\project
gemini

# Include additional directories
gemini --include-directories ../lib,../docs

# Use a specific model
gemini -m gemini-2.5-flash
```

### Quick Examples

```powershell
# Inside a Gemini session — ask anything
> Explain the architecture of this codebase
> Find and fix the bug in src/auth.py
> Write unit tests for the utils module
> Create a REST API endpoint for user registration
```

### Initialize Project Context

Inside a Gemini session, generate a starter `GEMINI.md`:

```
/init
```

---

## 5. GEMINI.md — Project Context

`GEMINI.md` is the **primary context file** that Gemini reads with every prompt. It provides project-specific instructions, coding standards, and persona definitions.

### Example GEMINI.md

```markdown
# Project Name

## Tech Stack
- Python 3.12 with uv package manager
- Reflex framework for web UI
- PostgreSQL database

## Conventions
- Use `uv` instead of `pip`
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

### GEMINI.md Hierarchy

The CLI loads context files in a hierarchy, with more specific files overriding general ones:

| Scope | Location | Purpose |
|---|---|---|
| **Global** | `~/.gemini/GEMINI.md` | Personal defaults for all projects |
| **Project Root** | `./GEMINI.md` | Project-specific context (git-tracked) |
| **Subdirectory** | `./src/GEMINI.md` | Component-specific context |

> [!IMPORTANT]
> Files are loaded from the project root upward (identified by `.git` folder), then down into subdirectories. More specific files take precedence.

### Importing Other Files

You can modularize context using the `@file.md` syntax:

```markdown
# Project Context
@coding-standards.md
@architecture.md
```

This supports both relative and absolute paths.

### Customizing Context File Name

In `settings.json`, override the default filename:

```json
{
  "context": {
    "fileName": ["AGENTS.md", "CONTEXT.md", "GEMINI.md"]
  }
}
```

### GEMINI.md vs SYSTEM.md

| File | Layer | Purpose |
|---|---|---|
| `SYSTEM.md` | Firmware | Fundamental operational rules, tool usage, safety |
| `GEMINI.md` | Strategy | High-level persona, coding style, project context |

### Memory Commands

| Command | Purpose |
|---|---|
| `/init` | Generate a starter `GEMINI.md` |
| `/memory show` | Display the combined context sent to the model |
| `/memory add <text>` | Add persistent memory on the fly |
| `/memory refresh` | Reload context files |

---

## 6. Settings & Configuration

### Configuration File Locations

| Scope | Path | Purpose |
|---|---|---|
| **User** | `~/.gemini/settings.json` | Global defaults for all projects |
| **Project** | `.gemini/settings.json` | Project-specific settings |
| **Environment File** | `~/.gemini/.env` or `.gemini/.env` | API keys and secrets |

### Configuration Precedence (lowest → highest)

1. Default values (hardcoded)
2. System defaults file
3. User settings (`~/.gemini/settings.json`)
4. Project settings (`.gemini/settings.json`)
5. System settings file (overrides all settings files)
6. Environment variables (`GEMINI_API_KEY`, `GEMINI_MODEL`, etc.)
7. Command-line arguments (override everything)

### Example `settings.json`

```json
{
  "theme": "dark",
  "model": "gemini-3-pro",
  "context": {
    "fileName": "GEMINI.md"
  },
  "mcpServers": {},
  "sandbox": false
}
```

### Key Environment Variables

| Variable | Purpose |
|---|---|
| `GEMINI_API_KEY` | Gemini API key for authentication |
| `GOOGLE_API_KEY` | Google Cloud/Vertex AI key |
| `GOOGLE_CLOUD_PROJECT` | Google Cloud project ID |
| `GOOGLE_GENAI_USE_VERTEXAI` | Enable Vertex AI mode (`true`) |
| `GEMINI_MODEL` | Override default model |
| `GEMINI_SANDBOX` | Enable sandbox mode |
| `GEMINI_CLI_HOME` | Custom Gemini CLI home directory |

---

## 7. Built-in Tools

Gemini CLI comes with built-in tools the model uses to interact with your local environment:

### File System Tools

| Tool | Purpose |
|---|---|
| `read_file` / `read_many_files` | Read file contents |
| `write_file` | Create or overwrite files |
| `edit` | In-place file modifications |
| `list_directory` | List directory contents |
| `find_files` (GlobTool) | Find files using glob patterns |
| `search_file_content` (GrepTool) | Search for text within files |

### Shell Tool

| Tool | Purpose |
|---|---|
| `run_shell_command` | Execute arbitrary shell commands (tests, builds, scripts) |

### Web Tools

| Tool | Purpose |
|---|---|
| `google_web_search` | Google Search grounding with real-time info |
| `web_fetch` | Fetch and process content from a URL |

### Other Tools

| Tool | Purpose |
|---|---|
| `save_memory` | Persist user preferences across sessions |
| `write_todos` | Write TODO items |

> [!TIP]
> Use the `/tools` slash command to list all available tools in your current session, including MCP-provided tools.

---

## 8. Sandbox & Approval Modes

### Approval Modes

The CLI uses a Human-in-the-Loop (HiTL) approval system for potentially sensitive operations:

| Mode | Flag | Behavior |
|---|---|---|
| **Default** | `--approval-mode default` | Prompts for approval on each tool call |
| **Auto Edit** | `--approval-mode auto_edit` | Auto-approves file edits; prompts for shell commands |
| **YOLO** | `--yolo` or `--approval-mode yolo` | Auto-approves **all** tool calls (use with caution) |

```powershell
# Start with auto-edit mode
gemini --approval-mode auto_edit

# Start in YOLO mode
gemini --yolo

# Allow specific tools without prompting
gemini --allowed-tools read_file,list_directory
```

### Sandboxing

Sandbox mode isolates shell commands and file operations to protect your system:

```powershell
# Enable via flag
gemini --sandbox

# Enable via environment variable
$env:GEMINI_SANDBOX = "true"
gemini
```

> [!CAUTION]
> YOLO mode automatically enables sandboxing for safety. On Windows, Docker or Podman is used for container-based isolation. On macOS, Seatbelt native sandboxing is used.

### Custom Sandbox (Dockerfile)

Create a project-specific sandbox:

```
your-project/
└── .gemini/
    └── Dockerfile    # Custom sandbox environment
```

---

## 9. MCP Server Configuration

> **Full guide**: [mcp-setup-guide.md](./mcp-setup-guide.md)

MCP (Model Context Protocol) servers extend Gemini CLI with custom tools and integrations.

### Configuration in `settings.json`

MCP servers are configured in `~/.gemini/settings.json` (global) or `.gemini/settings.json` (project):

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
        "GITHUB_TOKEN": "YOUR_TOKEN"
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

### MCP Server Properties

| Property | Type | Required | Purpose |
|---|---|---|---|
| `command` | string | ✅ (stdio) | Path to executable |
| `url` | string | ✅ (SSE) | SSE endpoint URL |
| `httpUrl` | string | ✅ (HTTP) | HTTP streaming endpoint URL |
| `args` | string[] | — | Command-line arguments |
| `env` | object | — | Environment variables |
| `cwd` | string | — | Working directory |
| `headers` | object | — | Custom HTTP headers |
| `timeout` | number | — | Timeout in milliseconds |
| `trust` | boolean | — | Whether the server is trusted |

### MCP Slash Commands

| Command | Purpose |
|---|---|
| `/mcp` | List connected MCP servers and their tools |
| `/mcp desc` | Detailed descriptions of available tools |

### Using MCP Tools in Session

```
> @github List my open pull requests
> @slack Send a summary of today's commits to #dev channel
> @database Run a query to find inactive users
```

---

## 10. Extensions

Extensions are self-contained, distributable packages that bundle customizations for Gemini CLI.

### What an Extension Can Bundle

- **Custom Slash Commands** — `.toml` files encapsulating complex prompts
- **MCP Server Configurations** — Connect to external tools and APIs
- **Context Files** — `GEMINI.md` for extension-specific instructions
- **Tool Restrictions** — `excludeTools` to disable specific built-in tools

### Extension Structure

```
my-extension/
├── gemini-extension.json    # Manifest (name, version, configs)
├── GEMINI.md                # Extension-specific context
├── commands/
│   └── my-command.toml      # Custom slash command
└── settings.json            # MCP server configs
```

### Installing Extensions

```powershell
# Install from URL
gemini extensions install <URL>

# Install from local path
gemini extensions install --path=some/local/path
```

### Managing Extensions

| Command | Purpose |
|---|---|
| `/extensions` | List active extensions |
| `gemini extensions install` | Install an extension |
| `gemini extensions list` | List installed extensions |

### Custom Slash Commands

Store command definitions in `.toml` files:

| Scope | Location |
|---|---|
| **Global** | `~/.gemini/commands/` |
| **Project** | `.gemini/commands/` |

---

## 11. Slash Commands & Keyboard Shortcuts

### Slash Commands

| Command | Purpose |
|---|---|
| `/help` | Show available commands |
| `/init` | Generate a starter `GEMINI.md` |
| `/chat` | Start a new chat conversation |
| `/memory show` | Display combined context |
| `/memory add <text>` | Add persistent memory |
| `/memory refresh` | Reload context files |
| `/tools` | List available tools |
| `/mcp` | List MCP servers and tools |
| `/mcp desc` | Detailed tool descriptions |
| `/restore` | Revert file changes |
| `/extensions` | List active extensions |
| `/bug` | Report a bug directly from the CLI |
| `/ide install` | Install IDE companion |
| `/ide enable` | Enable IDE integration |

### Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl+L` | Clear screen |
| `Ctrl+V` | Paste from clipboard |
| `Ctrl+Y` | Toggle YOLO mode |
| `Ctrl+X` | Open in external editor |

---

## 12. Headless Mode (Scripting)

Gemini CLI can run non-interactively for automation and scripting:

### Simple Text Output

```powershell
gemini -p "Explain the architecture of this codebase"
```

### JSON Output (Structured)

```powershell
gemini -p "List all TODO comments in this project" --output-format json
```

### Stream JSON (Real-Time Events)

```powershell
gemini -p "Run tests and deploy" --output-format stream-json
```

### Common Flags for Headless Mode

| Flag | Purpose |
|---|---|
| `-p` / `--prompt` | Non-interactive single prompt |
| `--prompt-interactive` | Interactive mode with initial prompt |
| `--output-format text` | Plain text output (default) |
| `--output-format json` | Structured JSON output |
| `--output-format stream-json` | Newline-delimited JSON events |
| `-m` / `--model` | Select specific model |
| `--debug` | Enable debug mode |

### CI/CD Integration

Use the [Gemini CLI GitHub Action](https://github.com/google-github-actions/run-gemini-cli) for:

- **Pull Request Reviews** — Automated code review with contextual feedback
- **Issue Triage** — Automated labeling and prioritization
- **On-demand Assistance** — Mention `@gemini-cli` in issues and PRs
- **Custom Workflows** — Scheduled and on-demand automation

---

## 13. IDE Integration

Gemini CLI integrates with VS Code via **Gemini Code Assist**:

```
/ide install
/ide enable
```

Features:
- Native diff view for file changes
- Workspace context awareness
- Agent mode for multi-step tasks within the IDE
- Human-in-the-Loop approval for file modifications

---

## 14. Verification Checklist

Run through this after setup to confirm everything works:

- [ ] `node --version` outputs v20+
- [ ] `gemini --version` outputs a version number
- [ ] `gemini` opens a session and authenticates
- [ ] `/init` creates or updates `GEMINI.md`
- [ ] `/tools` lists built-in tools
- [ ] `/mcp` shows configured MCP servers (if any)
- [ ] `/extensions` lists installed extensions (if any)
- [ ] Test a prompt: "Explain the files in this directory"
- [ ] Test shell tool: "Run `node --version` and report the output"
- [ ] Test web search: "Search for the latest Node.js LTS version"

---

## Quick Reference Links

| Resource | URL |
|---|---|
| GitHub Repo | [github.com/google-gemini/gemini-cli](https://github.com/google-gemini/gemini-cli) |
| Documentation Site | [geminicli.com/docs](https://geminicli.com/docs/) |
| Authentication Guide | [docs/get-started/authentication.md](https://github.com/google-gemini/gemini-cli/blob/main/docs/get-started/authentication.md) |
| Configuration Guide | [docs/get-started/configuration.md](https://github.com/google-gemini/gemini-cli/blob/main/docs/get-started/configuration.md) |
| GEMINI.md Reference | [docs/cli/gemini-md.md](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/gemini-md.md) |
| Commands Reference | [docs/cli/commands.md](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/commands.md) |
| Built-in Tools | [docs/tools/index.md](https://github.com/google-gemini/gemini-cli/blob/main/docs/tools/index.md) |
| MCP Server Integration | [docs/tools/mcp-server.md](https://github.com/google-gemini/gemini-cli/blob/main/docs/tools/mcp-server.md) |
| Extensions Guide | [docs/extensions/index.md](https://github.com/google-gemini/gemini-cli/blob/main/docs/extensions/index.md) |
| Sandbox & Security | [docs/cli/sandbox.md](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/sandbox.md) |
| Headless Mode | [docs/cli/headless.md](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/headless.md) |
| Checkpointing | [docs/cli/checkpointing.md](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/checkpointing.md) |
| Custom Commands | [docs/cli/custom-commands.md](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/custom-commands.md) |
| Keyboard Shortcuts | [docs/cli/keyboard-shortcuts.md](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/keyboard-shortcuts.md) |
| GitHub Action | [google-github-actions/run-gemini-cli](https://github.com/google-github-actions/run-gemini-cli) |
| Google AI Studio | [aistudio.google.com](https://aistudio.google.com) |

---

## File Index (This Folder)

| File | Purpose |
|---|---|
| [README.md](./README.md) | This guide — main setup & agent walkthrough |
| [skills-guide.md](./skills-guide.md) | Custom commands, agent skills & extensions |
| [multi-agents-guide.md](./multi-agents-guide.md) | Multi-agent orchestration & Maestro |
| [mcp-setup-guide.md](./mcp-setup-guide.md) | MCP server configuration for Gemini CLI |
