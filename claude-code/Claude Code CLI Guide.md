# Claude Code CLI — Comprehensive Practical Guide (2026)

> This guide consolidates official Claude Code documentation into one practical reference for day-to-day use of the **Claude Code terminal CLI**.
>
> Primary sources (official docs):
> - Overview: https://code.claude.com/docs/en/overview
> - Quickstart: https://code.claude.com/docs/en/quickstart
> - CLI reference: https://code.claude.com/docs/en/cli-reference
> - Common workflows: https://code.claude.com/docs/en/common-workflows
> - Interactive mode reference: https://code.claude.com/docs/en/interactive-mode
> - Settings: https://code.claude.com/docs/en/settings
> - Permissions: https://code.claude.com/docs/en/permissions
> - Hooks guide + reference: https://code.claude.com/docs/en/hooks-guide and https://code.claude.com/docs/en/hooks
> - Skills: https://code.claude.com/docs/en/skills
> - Subagents: https://code.claude.com/docs/en/sub-agents
> - Programmatic usage (“headless” / Agent SDK CLI): https://code.claude.com/docs/en/headless
> - MCP: https://code.claude.com/docs/en/mcp
> - Checkpointing: https://code.claude.com/docs/en/checkpointing
> - Troubleshooting: https://code.claude.com/docs/en/troubleshooting

---

## 0) Mental model: what Claude Code CLI is

Claude Code is an *agentic coding tool* that can read your codebase, edit files, run commands, and integrate with developer tooling (git, test runners, MCP servers, etc.) directly from your terminal. It has:

- **Interactive mode**: `claude` opens a REPL-like session.
- **Print / non-interactive mode**: `claude -p "..."` runs a task and exits (useful for scripts/CI).  
  (Docs now frame this as the Agent SDK CLI; the behavior and flags remain the same.)

Official overview: https://code.claude.com/docs/en/overview

---

## 1) Install & update

### 1.1 Install (recommended native installer)

**macOS / Linux / WSL**

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

**Windows PowerShell**

```powershell
irm https://claude.ai/install.ps1 | iex
```

**Windows CMD**

```bat
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd
```

Docs: https://code.claude.com/docs/en/setup and https://code.claude.com/docs/en/quickstart

### 1.2 Update

```bash
claude update
```

Docs: https://code.claude.com/docs/en/setup

### 1.3 Sanity check

```bash
claude --version
claude doctor
```

Docs: https://code.claude.com/docs/en/setup and https://code.claude.com/docs/en/interactive-mode

---

## 2) Authenticate

Start a session and follow the login flow:

```bash
claude
```

Then in-session:

- `/login` to sign in
- `/logout` to sign out

Troubleshooting login issues: https://code.claude.com/docs/en/troubleshooting

---

## 3) The two core usage modes

### 3.1 Interactive mode (daily driver)

```bash
cd /path/to/repo
claude
```

Use it like a conversation:

- “give me an overview of this repo”
- “find where auth tokens are refreshed”
- “fix the failing tests and verify they pass”

Quickstart walkthrough: https://code.claude.com/docs/en/quickstart

### 3.2 Print / non-interactive mode (scripts & CI)

```bash
claude -p "Summarize this repo"
```

Return formats:

```bash
claude -p "Summarize this repo" --output-format text
claude -p "Summarize this repo" --output-format json
claude -p "Summarize this repo" --output-format stream-json
```

Structured output with JSON Schema:

```bash
claude -p "Extract function names from auth.py" \
  --output-format json \
  --json-schema '{"type":"object","properties":{"functions":{"type":"array","items":{"type":"string"}}},"required":["functions"]}'
```

Docs: https://code.claude.com/docs/en/headless

---

## 4) Essential CLI commands & flags you’ll actually use

### 4.1 Commands

- `claude` — start interactive session
- `claude "task"` — start interactive session with an initial prompt
- `claude -p "task"` — print mode, then exit
- `claude -c` / `--continue` — continue most recent conversation in this directory
- `claude -r <id-or-name>` / `--resume <id-or-name>` — resume by ID/name or open picker
- `claude update` — update CLI
- `claude mcp ...` — manage MCP servers

Docs: https://code.claude.com/docs/en/cli-reference

### 4.2 High-impact flags

- **Permissions**
  - `--permission-mode <default|acceptEdits|plan|dontAsk|bypassPermissions>`
  - `--allowedTools "..."` / `--disallowedTools "..."`
  - `--dangerously-skip-permissions` (high risk; see permissions section)

- **Sessions**
  - `--continue` (`-c`)
  - `--resume` (`-r`)
  - `--fork-session` (resume but branch to a new session ID)

- **Worktrees**
  - `--worktree` (`-w`) — start Claude in an isolated git worktree (see §7)

- **Project access**
  - `--add-dir ../other-repo` — allow Claude to access additional directories

- **Output / scripting** (print mode)
  - `--output-format text|json|stream-json`
  - `--include-partial-messages` (stream-json)

- **Prompt control**
  - `--append-system-prompt "..."`
  - `--system-prompt "..."` (replaces defaults; use carefully)

Docs: https://code.claude.com/docs/en/cli-reference and https://code.claude.com/docs/en/headless

---

## 5) Interactive mode: commands, shortcuts, and practical habits

### 5.1 Must-know built-in commands

- `/help` — show help
- `/config` — open settings UI
- `/permissions` — adjust permissions and “don’t ask again” rules
- `/resume` / `/rename` — manage sessions
- `/compact [instructions]` — summarize conversation to save context
- `/rewind` — restore code+conversation to a checkpoint (see §10)
- `/mcp` — manage/auth MCP connections
- `/model` — switch model
- `/debug` — help troubleshoot current session
- `/doctor` — installation health

Docs: https://code.claude.com/docs/en/interactive-mode

### 5.2 Power shortcuts

- `?` — show shortcuts for your terminal
- `Ctrl+O` — verbose mode (see what tools were used)
- `Shift+Tab` — cycle permission modes (Normal → Auto-accept edits → Plan)
- `Esc` `Esc` — open rewind/summarize menu
- `Ctrl+B` — background a running command/agent
- `! <cmd>` — bash mode: run a command and include output in context
- `@` — reference files/directories/resources via autocomplete

Docs: https://code.claude.com/docs/en/interactive-mode

---

## 6) Permissions: keep it safe *and* fast

Claude Code’s permission system is designed so you can allow what’s routine while protecting what’s risky.

### 6.1 Permission modes (big picture)

- `default`: prompts as needed (normal)
- `acceptEdits`: auto-accept file edits for the session
- `plan`: read-only analysis and planning (no edits, no commands)
- `dontAsk`: auto-deny tools unless explicitly allowed by rules
- `bypassPermissions`: no prompts (dangerous; use only in safe sandbox)

Docs: https://code.claude.com/docs/en/permissions

### 6.2 Permission rules (allow / ask / deny)

Rules match tools, optionally with specifiers:

- Allow all git status:

```json
{ "permissions": { "allow": ["Bash(git status *)"] } }
```

- Deny secrets:

```json
{ "permissions": { "deny": ["Read(./.env)", "Read(./secrets/**)"] } }
```

Rules exist in `~/.claude/settings.json`, `.claude/settings.json`, or `.claude/settings.local.json` (see §8).

Docs: https://code.claude.com/docs/en/permissions and https://code.claude.com/docs/en/settings

### 6.3 Best-practice pattern

1. Start in `plan` for big changes:

```bash
claude --permission-mode plan
```

2. Review plan; then switch to `acceptEdits` (or stay in default) for implementation.
3. Use **fine-grained allow rules** for repeated safe commands (`git diff`, `npm test`, etc.).

Best practices: https://code.claude.com/docs/en/best-practices

---

## 7) Parallel work with Git worktrees

Claude supports **two complementary approaches**:

### 7.1 Standard Git worktree workflow (manual control)

```bash
git worktree add ../project-feature-a -b feature-a
cd ../project-feature-a
claude
```

This is the canonical Git method and works with any tooling.

Docs: https://code.claude.com/docs/en/common-workflows#run-parallel-claude-code-sessions-with-git-worktrees

### 7.2 Claude-managed isolation: `--worktree` / `-w`

The CLI supports a flag documented in the official CLI reference:

- `--worktree` / `-w`: start Claude in an isolated git worktree.

Use this when you want Claude Code to set up isolation for the session automatically.

Docs: https://code.claude.com/docs/en/cli-reference

**Important practical note:** each worktree is a separate working directory, so you usually need to run project setup (deps/venv) per worktree.

---

## 8) Configuration & where things live (settings, memory, MCP)

### 8.1 Configuration scopes (precedence)

Highest → lowest precedence:

1. **Managed** (org-wide) settings
2. **Command line args**
3. **Local** project settings (`.claude/settings.local.json`)
4. **Project** settings (`.claude/settings.json`)
5. **User** settings (`~/.claude/settings.json`)

Docs: https://code.claude.com/docs/en/settings

### 8.2 Key files & directories

- `~/.claude/settings.json` — your global preferences
- `.claude/settings.json` — shared repo config (commit it)
- `.claude/settings.local.json` — your local overrides (gitignored)
- `~/.claude.json` — global state (theme, OAuth, MCP user/local config)
- `.mcp.json` — project-scoped MCP servers

Troubleshooting lists these too: https://code.claude.com/docs/en/troubleshooting

### 8.3 Memory (CLAUDE.md) and rules

Claude loads instruction files at session start.

- Project memory: `./CLAUDE.md` or `./.claude/CLAUDE.md`
- Local memory: `./CLAUDE.local.md` (auto-gitignored)
- Modular rules: `./.claude/rules/*.md`
- User memory: `~/.claude/CLAUDE.md`

Docs: https://code.claude.com/docs/en/memory

**Tip:** Put “how to build/test/lint” and “project conventions” in `CLAUDE.md` so Claude doesn’t have to rediscover them every session.

---

## 9) Hooks: enforce workflows deterministically

Hooks run your shell commands automatically at specific lifecycle events.

Common uses:

- auto-format after edits
- block edits to protected files (like `.env`)
- send notifications when Claude needs input
- run tests after edits (optionally async)

Docs:
- Guide: https://code.claude.com/docs/en/hooks-guide
- Reference schemas: https://code.claude.com/docs/en/hooks

---

## 10) Safety nets: checkpointing, rewind, compact

### 10.1 Checkpointing & `/rewind`

Claude Code records checkpoints automatically for **file edits made via its edit/write tools**.

- `Esc` `Esc` or `/rewind` opens restore/summarize options.
- You can restore code, conversation, or both.

Limitations: changes made by **bash commands** are not tracked by checkpointing.

Docs: https://code.claude.com/docs/en/checkpointing

### 10.2 `/compact`

Use `/compact` (optionally with instructions) to reduce context usage during long sessions.

Docs: https://code.claude.com/docs/en/interactive-mode and https://code.claude.com/docs/en/best-practices

---

## 11) Skills: reusable slash commands

Skills are directories containing `SKILL.md` plus optional supporting files/scripts.

Where skills live:

- Personal: `~/.claude/skills/<name>/SKILL.md`
- Project: `.claude/skills/<name>/SKILL.md`

Key patterns:

- `disable-model-invocation: true` for “side-effect” workflows you only want to trigger manually.
- `allowed-tools:` to grant a skill specific tool access.
- `context: fork` + `agent:` to run the skill in an isolated subagent context.

Docs: https://code.claude.com/docs/en/skills

---

## 12) Subagents: specialized assistants inside a session

Subagents are Markdown files with YAML frontmatter, stored at:

- Project: `.claude/agents/`
- User: `~/.claude/agents/`

Subagents help by isolating high-volume output (tests, log scans) and enforcing tool constraints.

Docs: https://code.claude.com/docs/en/sub-agents

---

## 13) MCP: connect Claude Code to external tools

MCP lets Claude Code use external tools and data sources (issue trackers, DBs, SaaS APIs).

### 13.1 Add / list / remove MCP servers

```bash
claude mcp add --transport http notion https://mcp.notion.com/mcp
claude mcp list
claude mcp get notion
claude mcp remove notion
```

### 13.2 Scopes

- `--scope local` (default): only you, this project
- `--scope project`: shared via `.mcp.json`
- `--scope user`: you, all projects

Docs: https://code.claude.com/docs/en/mcp

### 13.3 Use MCP resources and prompts

- `@server:resource://...` to reference resources
- `/mcp__servername__promptname` to run MCP prompts as commands

Docs: https://code.claude.com/docs/en/mcp

---

## 14) Common workflows (copy/paste prompts)

These are proven prompt shapes from the official docs.

### 14.1 Explore → plan → implement

1) Explore

- “give me an overview of this codebase”
- “find the files that handle user authentication”

2) Plan

- “I need to refactor auth to use OAuth2. Create a migration plan.”

3) Implement + verify

- “implement the plan, run tests, and fix failures”

Docs: https://code.claude.com/docs/en/common-workflows and https://code.claude.com/docs/en/best-practices

### 14.2 Create a PR

- “create a pr”
- or use a skill like `/commit-push-pr` if available in your setup

Docs: https://code.claude.com/docs/en/common-workflows

---

## 15) Troubleshooting quick index

- `claude doctor` first.
- Windows native CLI requires Git Bash; set `CLAUDE_CODE_GIT_BASH_PATH` if not detected.
- If `claude` launches Desktop instead of CLI, update Desktop / fix PATH.
- Search/`@` suggestions broken: install `ripgrep`, set `USE_BUILTIN_RIPGREP=0`.
- Repeated permission prompts: configure `/permissions` and/or `permissions.allow` rules.

Docs: https://code.claude.com/docs/en/troubleshooting

---

## Appendix A — Quick command cheat sheet

### Start / resume

```bash
claude
claude "task"
claude --continue
claude --resume
```

### Safer sessions

```bash
claude --permission-mode plan
claude --permission-mode acceptEdits
```

### Print / scripting

```bash
claude -p "prompt" --output-format json
```

### Worktrees

```bash
claude --worktree
# or manual git worktree add ... then run claude
```

### MCP

```bash
claude mcp add --transport http <name> <url>
claude mcp list
```

---

## Appendix B — “Good defaults” starter configs

### B.1 Minimal `CLAUDE.md` template (project root)

```md
# Project workflow
- Build: `npm run build`
- Test: `npm test`
- Lint: `npm run lint`

# Code conventions
- Use TypeScript strict mode
- Prefer functional components for React

# PR etiquette
- Keep PRs small
- Update changelog when user-facing behavior changes
```

### B.2 Minimal `.claude/settings.json` template

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [
      "Bash(git status *)",
      "Bash(git diff *)",
      "Bash(npm test *)"
    ],
    "deny": [
      "Read(./.env)",
      "Read(./secrets/**)"
    ]
  }
}
```

Docs: https://code.claude.com/docs/en/settings and https://code.claude.com/docs/en/permissions
