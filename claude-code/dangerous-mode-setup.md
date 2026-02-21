# Claude Code — Dangerous Automated Mode (Windows)

Full-auto "YOLO mode" setup for Claude Code on Windows so it runs uninterrupted without permission prompts. Includes recommended MCP servers and skills mirrored from an Antigravity IDE setup.

> [!CAUTION]
> `--dangerously-skip-permissions` bypasses **all** permission prompts. Use only on disposable branches or isolated environments. Always have Git as your safety net.

---

## 1. Install & Authenticate

```powershell
# Install (pick one)
irm https://claude.ai/install.ps1 | iex          # PowerShell installer
winget install Anthropic.ClaudeCode               # or via WinGet

# Verify
claude --version

# Auth (browser OAuth)
claude
```

---

## 2. Launch in Dangerous Mode

### Option A: One-Shot (Recommended Daily Driver)

```powershell
claude --dangerously-skip-permissions
```

This skips **all** permission prompts for the entire session — file edits, bash commands, MCP tool calls, everything.

### Option B: PowerShell Alias (Permanent Shortcut)

Add to your `$PROFILE`:

```powershell
# Open profile
notepad $PROFILE

# Add this line:
Set-Alias cca 'claude --dangerously-skip-permissions'
```

Now just type `cca` to launch.

### Option C: Headless / CI Mode

```powershell
claude -p "Run all tests and fix failures" --dangerously-skip-permissions --output-format stream-json
```

- `-p` = non-interactive (pipe mode)
- `--output-format stream-json` = structured output for automation

### Option D: Settings-Based Auto-Accept (Safer Alternative)

Instead of full YOLO, configure `settings.json` to auto-allow most operations:

**`%USERPROFILE%\.claude\settings.json`**

```json
{
    "$schema": "https://json.schemastore.org/claude-code-settings.json",
    "permissions": {
        "defaultMode": "bypassPermissions",
        "allow": [
            "Edit",
            "MultiEdit",
            "Write",
            "Read",
            "Bash(git *)",
            "Bash(npm *)",
            "Bash(npx *)",
            "Bash(uv *)",
            "Bash(python *)",
            "Bash(pip *)",
            "Bash(node *)",
            "Bash(pwsh *)",
            "Bash(mkdir *)",
            "Bash(cp *)",
            "Bash(mv *)",
            "Bash(cat *)",
            "Bash(echo *)",
            "Bash(type *)",
            "Bash(dir *)",
            "Bash(ls *)",
            "Bash(cd *)",
            "Bash(grep *)",
            "Bash(find *)",
            "Bash(head *)",
            "Bash(tail *)",
            "Bash(wc *)",
            "Bash(cargo *)",
            "Bash(dotnet *)",
            "WebFetch"
        ],
        "deny": [
            "Read(./.env)",
            "Read(./.env.*)",
            "Read(./secrets/**)",
            "Read(**/.aws/**)",
            "Bash(rm -rf /)",
            "Bash(format *)"
        ]
    }
}
```

> [!TIP]
> **Option D is the recommended approach**: it gives near-zero-friction development while still protecting secrets and destructive system commands. You can always escalate to full `--dangerously-skip-permissions` when needed.

---

## 3. Recommended MCP Servers

These mirror the Antigravity IDE MCP stack and add development-essential servers.

### Quick Install (CLI Commands)

```powershell
# Context7 — live docs for any library
claude mcp add -s user context7 -- npx -y @upstash/context7-mcp@latest

# Brave Search — web search from within Claude
claude mcp add -s user --env BRAVE_API_KEY=YOUR_KEY brave-search -- npx -y @modelcontextprotocol/server-brave-search

# Sequential Thinking — metacognitive reasoning
claude mcp add -s user sequential-thinking -- npx -y @modelcontextprotocol/server-sequential-thinking

# Playwright — browser automation & testing
claude mcp add -s user playwright -- npx -y @playwright/mcp@latest

# GitHub — PR, issues, repo management
claude mcp add -s user --env GITHUB_TOKEN=$env:GITHUB_TOKEN github -- npx -y @anthropic-ai/mcp-server-github

# Filesystem — explicit file tree access
claude mcp add -s user filesystem -- npx -y @anthropic-ai/mcp-server-filesystem .
```

### Or: Global `.mcp.json` (User Scope)

Create/edit `%USERPROFILE%\.claude\.mcp.json`:

```json
{
    "mcpServers": {
        "context7": {
            "command": "npx",
            "args": ["-y", "@upstash/context7-mcp@latest"],
            "env": {
                "DEFAULT_MINIMUM_TOKENS": "10000"
            }
        },
        "brave-search": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-brave-search"],
            "env": {
                "BRAVE_API_KEY": "${BRAVE_API_KEY}"
            }
        },
        "sequential-thinking": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
        },
        "playwright": {
            "command": "npx",
            "args": ["-y", "@playwright/mcp@latest"]
        },
        "github": {
            "command": "npx",
            "args": ["-y", "@anthropic-ai/mcp-server-github"],
            "env": {
                "GITHUB_TOKEN": "${GITHUB_TOKEN}"
            }
        }
    }
}
```

### MCP Server Reference

| Server | What It Does | Why You Need It |
|---|---|---|
| **Context7** | Queries live documentation for any library | Replaces outdated training data with real, current API docs |
| **Brave Search** | Web search | Research errors, find solutions, check latest releases |
| **Sequential Thinking** | Step-by-step reasoning | Better planning for complex multi-step tasks |
| **Playwright** | Browser automation | Test UIs, take screenshots, verify web apps |
| **GitHub** | Git operations via API | Create PRs, manage issues, review code without leaving the CLI |
| **Filesystem** | Explicit file tree access | Needed for some MCP-based workflows |

### Verify MCP Status

Inside a Claude Code session:

```
/mcp
```

All servers should show ✅ connected.

---

## 4. Recommended Skills

Create skills at `%USERPROFILE%\.claude\skills\` (user-global) or `.claude\skills\` (per-project).

### Skill: Commit (Conventional Commits)

**`%USERPROFILE%\.claude\skills\commit\SKILL.md`**

```markdown
---
name: commit
description: Create a conventional commit with a descriptive message
---

Create a git commit following Conventional Commits format:
1. Run `git diff --staged` to see what's staged
2. If nothing staged, run `git add -A`
3. Generate a commit message: `<type>(<scope>): <description>`
   - Types: feat, fix, refactor, docs, test, chore, style, perf
4. Run `git commit -m "<message>"`
5. Show the commit hash and summary
```

### Skill: Quick Test

**`%USERPROFILE%\.claude\skills\test\SKILL.md`**

```markdown
---
name: test
description: Run the project test suite and fix failures
context: fork
---

Run the test suite for this project:
1. Detect the test runner (pytest, jest, vitest, cargo test, etc.)
2. Run all tests
3. If failures exist:
   - Analyze the failure output
   - Fix the root cause (not the test, unless the test is wrong)
   - Re-run to confirm the fix
4. Report: total tests, passed, failed, fixed
```

### Skill: Deep Research

**`%USERPROFILE%\.claude\skills\research\SKILL.md`**

```markdown
---
name: research
description: Deep codebase research and analysis
context: fork
model: sonnet
allowed-tools: Read, Grep, Glob, Bash
---

Perform deep research on the codebase:
1. Understand the directory structure
2. Identify entry points and core modules
3. Map dependencies and data flow
4. Summarize architecture patterns
5. Report findings in a structured format
```

---

## 5. CLAUDE.md — Global User Config

Create `%USERPROFILE%\.claude\CLAUDE.md` for preferences that apply to **all** projects:

```markdown
# Global Claude Code Preferences

## Environment
- Windows 10/11 Pro
- PowerShell 7 (pwsh)
- Default package managers: uv (Python), npm (Node.js)

## Conventions
- Use `uv` instead of `pip` for Python projects
- Use `npx` for one-off Node tools
- Prefer PowerShell-compatible commands (avoid bash-isms like `&&`)
- Always use Git for version control

## Code Style
- Type hints required on all Python functions
- Use descriptive variable names
- Follow project-specific linting rules

## Workflow
- Always run tests before committing
- Use conventional commits (feat, fix, refactor, etc.)
- Check for breaking changes before pushing
```

---

## 6. Useful Subagents

Create at `%USERPROFILE%\.claude\agents\` for global availability.

### Code Reviewer

**`%USERPROFILE%\.claude\agents\code-reviewer.md`**

```markdown
---
name: code-reviewer
description: Review recent code changes for quality and correctness
tools: Read, Grep, Glob, Bash
model: sonnet
---

Review the latest code changes:
1. Run `git diff` to see uncommitted changes
2. Check for: bugs, security issues, performance problems, style violations
3. Categorize findings: Critical / Warning / Suggestion
4. Provide specific fix recommendations
```

### Debugger

**`%USERPROFILE%\.claude\agents\debugger.md`**

```markdown
---
name: debugger
description: Root cause analysis for bugs and errors
tools: Read, Grep, Glob, Bash
model: sonnet
---

Debug the reported issue:
1. Reproduce or understand the error
2. Trace the root cause through the codebase
3. Propose a fix with rationale
4. Verify the fix resolves the issue
```

---

## 7. Quick Reference

### Launch Modes

| Command | Mode |
|---|---|
| `claude` | Normal — asks permission for everything |
| `claude` + `Shift+Tab` | Accept-edits — auto-approves file edits only |
| `claude --dangerously-skip-permissions` | Full YOLO — no prompts at all |
| `claude -p "task" --dangerously-skip-permissions` | Headless YOLO — unattended automation |

### In-Session Shortcuts

| Key / Command | Action |
|---|---|
| `Shift+Tab` | Cycle: normal → accept-edits → plan mode |
| `Escape` | Interrupt current operation |
| `/compact` | Compress context window |
| `/mcp` | Check MCP server status |
| `/agents` | Manage subagents |
| `/permissions` | View/edit permission rules |
| `/clear` | Clear conversation |

### File Locations

| What | Path |
|---|---|
| Global settings | `%USERPROFILE%\.claude\settings.json` |
| Global CLAUDE.md | `%USERPROFILE%\.claude\CLAUDE.md` |
| Global skills | `%USERPROFILE%\.claude\skills\` |
| Global agents | `%USERPROFILE%\.claude\agents\` |
| Global MCP | `%USERPROFILE%\.claude\.mcp.json` |
| Project settings | `.claude\settings.json` |
| Project MCP | `.mcp.json` |
| Project CLAUDE.md | `CLAUDE.md` |

---

## 8. Safety Guardrails (Even in YOLO Mode)

Even with `--dangerously-skip-permissions`, protect yourself:

1. **Git is your undo button** — always work on a branch, commit often
2. **Keep `.env` in deny list** — prevent secret leakage
3. **Sandbox setting** — enable sandbox for extra isolation:
   ```json
   {
       "sandbox": {
           "enabled": true,
           "autoAllowBashIfSandboxed": true,
           "network": {
               "allowedDomains": ["github.com", "*.npmjs.org", "registry.yarnpkg.com"],
               "allowLocalBinding": true
           }
       }
   }
   ```
4. **Review before push** — YOLO for local work, review before `git push`

---

## Sources

- [Claude Code Settings (Official)](https://code.claude.com/docs/en/settings)
- [Claude Code MCP (Official)](https://code.claude.com/docs/en/mcp)
- [Claude Code Auto-Approve Guide (SmartScope, 2026)](https://smartscope.blog/en/generative-ai/claude/claude-code-auto-permission-guide/)
- [--dangerously-skip-permissions Deep Dive (PromptLayer)](https://blog.promptlayer.com/claude-dangerously-skip-permissions/)
- [Best MCP Servers for Claude Code (MCPcat)](https://mcpcat.io/guides/best-mcp-servers-for-claude-code/)
