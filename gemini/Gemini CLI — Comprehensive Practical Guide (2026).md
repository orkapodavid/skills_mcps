# Gemini CLI — Comprehensive Practical Guide (2026)

Gemini CLI is Google’s open‑source, terminal-first AI agent for working with Gemini models. It combines a chat-style REPL with tool use (file reads/writes, running shell commands, web fetch/search, and MCP servers) so it can *act* on your project—not just answer questions.

This guide is a consolidated, practical playbook: install → auth → daily usage → safe automation → power-user workflows → troubleshooting.

---

## Sources (official / primary)

* Gemini CLI documentation (official): https://geminicli.com/docs/
* Install / execution / release channels: https://geminicli.com/docs/get-started/installation/
* Authentication setup: https://geminicli.com/docs/get-started/authentication/
* CLI command & flag cheatsheet: https://geminicli.com/docs/cli/cli-reference/
* Command reference (slash commands, `@`, `!`): https://geminicli.com/docs/reference/commands/
* Configuration reference (settings files, env vars, precedence): https://geminicli.com/docs/reference/configuration/
* Sandboxing: https://geminicli.com/docs/cli/sandbox/
* Trusted folders (safe mode): https://geminicli.com/docs/cli/trusted-folders/
* Custom commands (.toml): https://geminicli.com/docs/cli/custom-commands/
* IDE integration: https://geminicli.com/docs/ide-integration/
* Troubleshooting + exit codes: https://geminicli.com/docs/resources/troubleshooting/
* Uninstall: https://geminicli.com/docs/cli/uninstall/
* Google Cloud doc (Gemini for Google Cloud): https://docs.cloud.google.com/gemini/docs/codeassist/gemini-cli
* GitHub Action integration: https://github.com/google-github-actions/run-gemini-cli

> Notes on sourcing: This guide prefers `geminicli.com` and Google Cloud documentation. GitHub is used only where the official docs route you there (e.g., action repo).

---

## Mental model (how Gemini CLI actually works)

Think of Gemini CLI as three layers:

1. **Conversation engine (REPL / one-shot / resumed sessions)**
   * You can chat interactively (`gemini`) or run a single prompt and exit (`gemini "…"`).
   * Sessions can be resumed later (`--resume latest`, `/chat save`, etc.).

2. **Context engine (what the model can “see”)**
   * Your prompt.
   * Optional stdin (piped input).
   * Files/directories you reference explicitly (`@path/to/file` in chat, or `@{...}` / `@...` patterns in custom commands).
   * Project “memory” (default file `GEMINI.md`) loaded hierarchically and sent with every prompt; configurable via `context.fileName` in `settings.json`.

3. **Tool engine (what the agent can do)**
   * Built-in tools (shell, file ops, web fetch/search, etc.).
   * Extension-provided tools.
   * MCP (Model Context Protocol) servers (local subprocess or remote SSE/HTTP). Google Cloud’s docs explicitly call out that Gemini CLI uses a ReAct loop and can use local/remote MCP servers. ([Cloud doc](https://docs.cloud.google.com/gemini/docs/codeassist/gemini-cli))

**Key implication:** Gemini CLI is *not* “just” an API client. It’s an agent runtime that can execute actions on your machine (or inside a sandbox). You should treat it like you’d treat any automation tool with access to your repo.

---

## Install, update, and uninstall

### Requirements (baseline)

From the official install doc:

* OS: macOS 15+, Windows 11 24H2+, Ubuntu 20.04+ (recommended)
* Node.js: 20+
* Shell: Bash or Zsh

Source: https://geminicli.com/docs/get-started/installation/

### Install (common paths)

#### Option A — npm (recommended default)

```bash
npm install -g @google/gemini-cli

# verify
gemini --version
```

Source: https://geminicli.com/docs/get-started/installation/

#### Option B — Homebrew (macOS/Linux)

```bash
brew install gemini-cli
```

Source: https://geminicli.com/docs/get-started/installation/

#### Option C — MacPorts (macOS)

```bash
sudo port install gemini-cli
```

Source: https://geminicli.com/docs/get-started/installation/

#### Option D — npx (no permanent install)

```bash
npx @google/gemini-cli
```

Source: https://geminicli.com/docs/get-started/installation/

#### Option E — restricted environments (Conda + npm)

```bash
conda create -y -n gemini_env -c conda-forge nodejs
conda activate gemini_env
npm install -g @google/gemini-cli
```

Source: https://geminicli.com/docs/get-started/installation/

### Update

There are two “update” concepts:

1. **Update the CLI package (npm/brew/etc.)**
2. **`gemini update` subcommand** (documented in the official cheatsheet)

Examples:

```bash
# npm: update to latest stable
npm install -g @google/gemini-cli@latest

# npm: preview channel
npm install -g @google/gemini-cli@preview

# npm: nightly channel
npm install -g @google/gemini-cli@nightly

# in-tool update command
gemini update
```

Sources:

* Release channels & tags: https://geminicli.com/docs/get-started/installation/
* `gemini update`: https://geminicli.com/docs/cli/cli-reference/

### Uninstall

Uninstall depends on how you installed:

```bash
# npm global install
npm uninstall -g @google/gemini-cli

# Homebrew
brew uninstall gemini-cli

# MacPorts
sudo port uninstall gemini-cli
```

If you used `npx`, clear the `_npx` cache (macOS/Linux example):

```bash
rm -rf "$(npm config get cache)/_npx"
```

Source: https://geminicli.com/docs/cli/uninstall/

---

## Authenticate (and switch identities/projects safely)

Gemini CLI supports multiple authentication tracks. Pick based on how you want to pay, what quotas you need, and whether you’re in a headless environment.

### Auth method chooser (fast mapping)

The official auth doc provides this mapping (abridged):

* **Login with Google** — best default for interactive local use.
* **Gemini API Key (AI Studio)** — good for scripting/headless; no browser required after env var is set.
* **Vertex AI** — for Google Cloud/enterprise workflows via ADC, service account key, or Google Cloud API key.

Source: https://geminicli.com/docs/get-started/authentication/

### Method 1 — Login with Google (interactive OAuth)

```bash
gemini
# choose: Login with Google
```

Notes:

* Requires a browser on a machine that can complete the sign-in flow. The CLI caches credentials locally for future sessions. (Source: https://geminicli.com/docs/get-started/authentication/)

### Method 2 — Gemini API key (AI Studio)

1) Create a key: https://aistudio.google.com/app/apikey

2) Export it:

```bash
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"

gemini
# choose: Use Gemini API key
```

Source: https://geminicli.com/docs/get-started/authentication/

**Operational advice (don’t leak your key):** Prefer a `.gemini/.env` file (project or user) instead of exporting in shell startup files if you share terminals or run many subprocesses.

The auth guide documents that Gemini CLI auto-loads the *first* `.env` file it finds while searching upward, and also checks `~/.gemini/.env` / `~/.env` (variables are not merged). (Source: https://geminicli.com/docs/get-started/authentication/)

### Method 3 — Vertex AI (Google Cloud)

Vertex AI use requires project & location:

```bash
export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
export GOOGLE_CLOUD_LOCATION="YOUR_PROJECT_LOCATION"  # e.g., us-central1
```

Then choose one auth mechanism:

#### A) ADC via gcloud

```bash
# IMPORTANT: unset API-key based auth if present (per doc)
unset GOOGLE_API_KEY
unset GEMINI_API_KEY

# login for ADC
gcloud auth application-default login

gemini
# choose: Vertex AI
```

Source: https://geminicli.com/docs/get-started/authentication/

#### B) Service account key JSON

```bash
unset GOOGLE_API_KEY
unset GEMINI_API_KEY

export GOOGLE_APPLICATION_CREDENTIALS="/absolute/path/to/key.json"

gemini
# choose: Vertex AI
```

Source: https://geminicli.com/docs/get-started/authentication/

#### C) Google Cloud API key

```bash
export GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"

gemini
# choose: Vertex AI
```

Source: https://geminicli.com/docs/get-started/authentication/

### Setting / switching Google Cloud project

The auth doc notes many individual accounts don’t need a Cloud project, but organization / Workspace accounts often do, and the CLI checks `GOOGLE_CLOUD_PROJECT` first, then `GOOGLE_CLOUD_PROJECT_ID`. (Source: https://geminicli.com/docs/get-started/authentication/)

Practical pattern:

```bash
# project-local via .gemini/.env
mkdir -p .gemini
cat > .gemini/.env <<'EOF'
GOOGLE_CLOUD_PROJECT="my-project-id"
GOOGLE_CLOUD_LOCATION="us-central1"
EOF

# run from that project folder
gemini
```

### Headless environments

The auth doc states: headless mode will use cached credentials if present; otherwise you must authenticate via env vars (API key or Vertex AI vars). (Source: https://geminicli.com/docs/get-started/authentication/)

---

## Core usage modes (interactive vs non-interactive)

### Mode A — Interactive REPL (default)

```bash
gemini
```

Use this when you want:

* multi-turn planning + execution
* approvals for tool use
* session checkpointing/resume
* rich UI (and IDE integration)

Source: https://geminicli.com/docs/cli/cli-reference/

### Mode B — One-shot (positional prompt)

```bash
gemini "Explain this repository in 10 bullets."
```

This is the recommended non-interactive interface: supply a positional query and the CLI runs headless and exits. (Source: https://geminicli.com/docs/cli/headless/)

### Mode C — “One-shot then continue interactively”

```bash
gemini -i "Scan the repo and tell me what to fix first."
```

Source: https://geminicli.com/docs/cli/cli-reference/

### Mode D — Pipe stdin (CLI as a processor)

```bash
cat ./logs.txt | gemini "Summarize errors and propose fixes."
```

Source: https://geminicli.com/docs/cli/cli-reference/

### Mode E — Resume a session

```bash
# resume most recent
gemini --resume latest

# resume most recent with a new prompt
gemini --resume latest "Continue where we left off."
```

Source: https://geminicli.com/docs/cli/cli-reference/

### Mode F — Sandbox mode (safer execution)

```bash
# enable sandboxing for this run
gemini --sandbox -i "Run unit tests and fix failures."
```

Source: https://geminicli.com/docs/cli/sandbox/ and https://geminicli.com/docs/cli/cli-reference/

---

## Essential commands & flags (what you actually use)

### The “big 8” CLI flags

From the official cheatsheet:

```bash
# help & version
gemini --help
gemini --version

# choose a model
gemini --model pro "…"
gemini -m flash "…"

# interactive start with prompt
gemini -i "…"

# resume prior session
gemini --resume latest

# include extra workspace directories (useful for mono-repos)
gemini --include-directories ../shared,../infra

# run in sandbox
 gemini --sandbox "…"

# output format for automation
gemini --output-format json "…"
gemini --output-format stream-json "…"
```

Source: https://geminicli.com/docs/cli/cli-reference/

### Approval modes (tool permissions)

The CLI supports an approval mode flag:

* `default` — prompt for approvals
* `auto_edit` — auto-approve edit tools while prompting for others
* `yolo` — auto-approve all actions (deprecated `--yolo` alias exists)

Source: https://geminicli.com/docs/cli/cli-reference/

Practical examples:

```bash
# safer default: approve edits automatically, still prompt for shell/web/etc.
gemini --approval-mode auto_edit -i "Refactor and format the codebase."

# high risk: approve everything (do this inside a sandbox)
gemini --approval-mode yolo --sandbox -i "Apply dependency updates and run tests."
```

### In-session “meta” commands (slash commands)

Gemini CLI supports built-in slash commands like `/chat`, `/memory`, `/model`, `/tools`, `/mcp`, `/settings`, etc. See the official command reference for the full list. (Source: https://geminicli.com/docs/reference/commands/)

A few that matter daily:

* `/help` or `/?` — discover commands
* `/model` — switch model during a session
* `/memory show` / `/memory refresh` — inspect/reload `GEMINI.md` memory
* `/chat save <tag>` / `/chat resume <tag>` — session checkpoints
* `/tools` — show tool descriptions (useful for safety)
* `/mcp` — MCP server status

Source: https://geminicli.com/docs/reference/commands/

### File inclusion vs shell passthrough (the `@` and `!` mental model)

From the command reference:

* `@path/to/file_or_dir` injects file content (with git-aware filtering)
* `!cmd` runs a shell command from inside the UI

Source: https://geminicli.com/docs/reference/commands/

Examples:

```text
@README.md Summarize the project.
@src/ Explain how this module works.

!git status
!npm test
```

**Safety reminder:** `!` commands have the same impact as running them directly in your terminal. (Source: https://geminicli.com/docs/reference/commands/)

---

## Configuration & where files live

### Configuration precedence (high-level)

Gemini CLI applies configuration with layered precedence. In practice, you should think:

* System defaults → user settings → project settings → env vars → CLI args

Source: https://geminicli.com/docs/reference/configuration/

### Settings files (locations)

The configuration reference documents four settings file locations:

* **User (global):** `~/.gemini/settings.json`
* **Project:** `.gemini/settings.json` (in project root)
* **System defaults:** OS-specific path (overridable via `GEMINI_CLI_SYSTEM_DEFAULTS_PATH`)
* **System overrides:** OS-specific path (overridable via `GEMINI_CLI_SYSTEM_SETTINGS_PATH`)

Source: https://geminicli.com/docs/reference/configuration/

### `.env` loading behavior (very important)

The configuration reference documents:

* `.env` discovery starts in the current directory and searches upward.
* If none is found, it checks `~/.env`.
* Some variables like `DEBUG` / `DEBUG_MODE` are excluded from *project* `.env` files by default (use `.gemini/.env` if you need them).

Source: https://geminicli.com/docs/reference/configuration/ and troubleshooting: https://geminicli.com/docs/resources/troubleshooting/

### Key directories and “state” files

Common paths referenced in official docs:

* User home state directory: `~/.gemini/` (can be relocated with `GEMINI_CLI_HOME`) (Source: https://geminicli.com/docs/reference/configuration/)
* Custom commands:
  * user: `~/.gemini/commands/`
  * project: `.gemini/commands/`
  (Source: https://geminicli.com/docs/cli/custom-commands/)
* Trusted folders registry: `~/.gemini/trustedFolders.json` (Source: https://geminicli.com/docs/cli/trusted-folders/)
* Shell history per project: `~/.gemini/tmp/<project_hash>/shell_history` (Source: https://geminicli.com/docs/reference/configuration/)

---

## Output formats, streaming, piping, and scripting

### `--output-format` values

The cheatsheet documents three output formats:

* `text` — default human-readable
* `json` — single JSON object response
* `stream-json` — newline-delimited JSON events (JSONL)

Source: https://geminicli.com/docs/cli/cli-reference/

### Headless JSON schema (what you can rely on)

The official headless reference describes:

* `--output-format json` returns an object containing `response`, `stats`, and optional `error`.
* `--output-format stream-json` emits event types like `init`, `message`, `tool_use`, `tool_result`, `error`, `result`.

Source: https://geminicli.com/docs/cli/headless/

### Practical automation patterns

#### Pattern 1 — one-shot JSON, parse with `jq`

```bash
gemini --output-format json "Summarize this repo" | jq -r '.response'
```

#### Pattern 2 — stream JSONL, tail for final result

```bash
gemini --output-format stream-json "Run tests and report failures" \
  | tee /tmp/gemini.events.jsonl \
  | jq -c 'select(.type=="result")'
```

> Caveat: The exact JSON fields inside each event may evolve; the headless doc only guarantees event *types* and high-level meaning. If you depend on event payload structure, pin a CLI version in CI.

#### Pattern 3 — safe, repeatable runs (pin version + config)

```bash
# pin CLI version via npm tag (stable)
npm install -g @google/gemini-cli@latest

# run from a repo with project config
cat > .gemini/settings.json <<'JSON'
{
  "general": { "defaultApprovalMode": "auto_edit" },
  "security": { "folderTrust": { "enabled": true } },
  "tools": { "sandbox": "docker" }
}
JSON

gemini --output-format json "Refactor src/ to reduce complexity" > out.json
```

Sources:

* Config format & locations: https://geminicli.com/docs/reference/configuration/
* Trusted folders: https://geminicli.com/docs/cli/trusted-folders/

---

## Permissions & safety playbook (avoid accidental leaks)

This is the section people skip—until something goes wrong.

### 1) Use trusted folders to prevent “drive-by config”

Trusted folders prevent Gemini CLI from loading project settings (`.gemini/settings.json`), `.env` files, MCP servers, and custom commands unless you explicitly trust the folder.

When a folder is untrusted, the CLI runs in a restricted safe mode and disables those capabilities. (Source: https://geminicli.com/docs/cli/trusted-folders/)

Enable it (user-level):

```json
{
  "security": {
    "folderTrust": {
      "enabled": true
    }
  }
}
```

Source: https://geminicli.com/docs/cli/trusted-folders/

### 2) Prefer sandboxing for any run that can mutate your system

Sandboxing isolates side-effecting operations from your host machine.

Enable sandboxing in order of precedence:

1. `--sandbox` flag
2. `GEMINI_SANDBOX` env var
3. `tools.sandbox` in `settings.json`

Source: https://geminicli.com/docs/cli/sandbox/

### 3) Control tool approvals (and avoid YOLO casually)

Use approval modes:

* `default` for maximal control
* `auto_edit` to reduce prompts while still requiring approval for shell/web
* `yolo` only for fully sandboxed / disposable environments

Source: https://geminicli.com/docs/cli/cli-reference/

### 4) Be deliberate about what goes into context

Risk factors:

* `@src/` can pull in sensitive files if your ignore rules aren’t strict.
* `cat .env | gemini` is basically “paste your secrets into a model”. Don’t.

Mitigations:

* Use `.gitignore` and `.geminiignore` (and keep secrets out of tracked files).
* Prefer referencing specific files instead of whole directories.

The command reference notes that `@` commands use git-aware filtering. (Source: https://geminicli.com/docs/reference/commands/)

### 5) Environment-variable redaction (tool execution)

The configuration reference documents that Gemini CLI automatically redacts potential secrets from environment variables when executing tools, with default redaction rules by name and by value pattern. (Source: https://geminicli.com/docs/reference/configuration/)

**Important:** redaction is “best effort.” Don’t assume it fully protects you.

---

## Integrations & extension points

### IDE integration (VS Code, Antigravity, VS Code forks)

Gemini CLI can integrate with supported IDEs to gain workspace context (recent files, cursor position, selection) and show diffs in the IDE’s native diff viewer.

Source: https://geminicli.com/docs/ide-integration/

Key commands:

* `/ide enable` / `/ide disable`
* `/ide status`
* `/ide install` (installs companion extension)

Source: https://geminicli.com/docs/reference/commands/ and IDE doc above.

### Extensions

Extensions can package prompts, MCP servers, custom commands, themes, hooks, sub-agents, and skills.

Source: https://geminicli.com/docs/extensions/

Common management:

```bash
gemini extensions list
gemini extensions install https://github.com/gemini-cli-extensions/workspace
gemini extensions update --all
```

Source: https://geminicli.com/docs/cli/cli-reference/

### MCP servers (bring your own tools)

MCP servers let Gemini CLI call tools exposed by local subprocesses or remote services.

Start by configuring `mcpServers` in settings, or use `gemini mcp add/list/remove`.

Sources:

* MCP server management commands: https://geminicli.com/docs/cli/cli-reference/
* MCP server docs: https://geminicli.com/docs/tools/mcp-server/

### GitHub Actions automation

Google provides a GitHub Action that invokes Gemini CLI for issue triage, PR review, and on-demand assistance (`@gemini-cli ...`).

Source: https://github.com/google-github-actions/run-gemini-cli

---

## Common workflows (copy/paste playbook)

### Workflow 1 — “Explain this codebase” (fast onboarding)

```bash
gemini "Read this repository and explain the architecture: modules, data flow, and key risks."
```

Add a specific file for sharper answers:

```bash
gemini "Explain this module and its public API" \
  --output-format text \
  "@src/index.ts"
```

> If you want deterministic-ish answers, use a lower-temperature model config via `settings.json` (see config reference). (Source: https://geminicli.com/docs/reference/configuration/)

### Workflow 2 — “Repo-wide grep + reasoning” (interactive)

```bash
gemini -i "Find where we parse JWTs and explain validation. Use ripgrep." 
```

In session:

```text
!rg -n "jwt" -S .
@src/auth/ Explain this directory.
```

Sources:

* `!` passthrough & `@` inclusion: https://geminicli.com/docs/reference/commands/

### Workflow 3 — “Safe refactor loop” (sandbox + auto-edit)

```bash
gemini --sandbox --approval-mode auto_edit -i \
  "Refactor src/ to remove duplication. Run tests after each change."
```

Sources:

* Sandbox: https://geminicli.com/docs/cli/sandbox/
* Approval modes: https://geminicli.com/docs/cli/cli-reference/

### Workflow 4 — “Repeatable PR review command” (custom command)

Create a project command `.gemini/commands/review.toml`:

```toml
# .gemini/commands/review.toml
description = "Review current git diff and suggest improvements"
prompt = """
You are a strict code reviewer.

Review this diff and return:
1) high-risk issues
2) correctness bugs
3) performance and security notes
4) a short, actionable checklist

Diff:
!{git diff}
"""
```

Reload without restarting:

```text
/commands reload
```

Run it:

```text
/review
```

Sources:

* Custom commands locations & TOML format: https://geminicli.com/docs/cli/custom-commands/
* `/commands reload`: https://geminicli.com/docs/reference/commands/

### Workflow 5 — CI-friendly lint summarizer (JSON output)

```bash
set -euo pipefail

npm test 2>&1 | gemini --output-format json "Summarize failures and list fixes" \
  | jq -r '.response'
```

Sources:

* Pipe usage: https://geminicli.com/docs/cli/cli-reference/
* JSON output format: https://geminicli.com/docs/cli/headless/

### Workflow 6 — “Multi-repo / mono-repo context”

```bash
gemini --include-directories ../shared,../infra -i \
  "Explain how these repos interact and where contracts are defined."
```

Source: https://geminicli.com/docs/cli/cli-reference/

---

## Troubleshooting quick index (symptom → fix)

### Auth & account issues

* **Org entitlement error when you’re using a personal account**
  * Symptom: entitlement required error.
  * Fix: unset `GOOGLE_CLOUD_PROJECT` / `GOOGLE_CLOUD_PROJECT_ID` if you’re not using org Code Assist; docs say these env vars can trigger subscription checks.
  * Source: https://geminicli.com/docs/resources/troubleshooting/

* **Location not supported**
  * Symptom: “not currently available in your location”.
  * Fix: check supported locations list.
  * Source: https://geminicli.com/docs/resources/troubleshooting/

* **Corporate TLS interception (`UNABLE_TO_GET_ISSUER_CERT_LOCALLY`)**
  * Fix: try `NODE_USE_SYSTEM_CA=1`, or set `NODE_EXTRA_CA_CERTS`.
  * Source: https://geminicli.com/docs/resources/troubleshooting/

### Runtime / install issues

* **`gemini: command not found`**
  * Fix: ensure npm global bin is on `PATH` or reinstall.
  * Source: https://geminicli.com/docs/resources/troubleshooting/

* **`MODULE_NOT_FOUND`** (from source/dev installs)
  * Fix: `npm install`, then `npm run build`.
  * Source: https://geminicli.com/docs/resources/troubleshooting/

### Sandbox issues

* **“Operation not permitted” / “Permission denied”**
  * Fix: loosen sandbox profile or mount required paths.
  * Source: https://geminicli.com/docs/resources/troubleshooting/ and https://geminicli.com/docs/cli/sandbox/

### CI/headless quirks

* **CLI refuses interactive mode in CI**
  * Cause: presence of env vars starting with `CI_` can cause non-interactive detection.
  * Fix: `env -u CI_TOKEN gemini` (example).
  * Source: https://geminicli.com/docs/resources/troubleshooting/

### Exit codes (automation)

From the official troubleshooting guide:

| Code | Meaning |
|---:|---|
| 41 | FatalAuthenticationError |
| 42 | FatalInputError |
| 44 | FatalSandboxError |
| 52 | FatalConfigError |
| 53 | FatalTurnLimitedError |

Source: https://geminicli.com/docs/resources/troubleshooting/

---

## Appendix A — Cheat sheet (condensed)

### Start & run

```bash
# interactive
gemini

# one-shot
gemini "explain this project"

# one-shot + keep going
gemini -i "start by explaining this project"

# pipe input
cat logs.txt | gemini "summarize errors"

# resume
gemini --resume latest
```

Source: https://geminicli.com/docs/cli/cli-reference/

### Must-know flags

```bash
# model selection
gemini -m pro "…"

# sandbox
gemini --sandbox "…"

# approval mode
gemini --approval-mode auto_edit -i "…"

# machine output
gemini --output-format json "…"
gemini --output-format stream-json "…"

# include extra directories
gemini --include-directories ../shared,../infra -i "…"
```

Source: https://geminicli.com/docs/cli/cli-reference/

### In-session power moves

```text
/help
/model
/tools
/memory show
/memory refresh
/mcp
/settings
/chat save <tag>
/chat resume <tag>
```

Source: https://geminicli.com/docs/reference/commands/

---

## Appendix B — “Good defaults” starter configs

Gemini CLI supports JSON settings files. The authoritative file locations and precedence are documented in the configuration reference. (Source: https://geminicli.com/docs/reference/configuration/)

### 1) User-level safe defaults (`~/.gemini/settings.json`)

Goal: safer-by-default interactive use.

```json
{
  "general": {
    "defaultApprovalMode": "auto_edit"
  },
  "security": {
    "folderTrust": {
      "enabled": true
    },
    "environmentVariableRedaction": {
      "enabled": true
    }
  },
  "ui": {
    "hideTips": false
  }
}
```

Why these choices (grounded in docs):

* Folder trust prevents untrusted repos from loading project `.gemini` config / `.env` / MCP servers / custom commands. (Source: https://geminicli.com/docs/cli/trusted-folders/)
* Env var redaction reduces accidental secret exposure to tools. (Source: https://geminicli.com/docs/reference/configuration/)
* `auto_edit` reduces prompt fatigue while still requiring approvals for riskier tools like shell commands. (Source: https://geminicli.com/docs/cli/cli-reference/)

### 2) Project-level “agent sandbox” defaults (`.gemini/settings.json`)

Goal: encourage safe execution when the agent is expected to run tools.

```json
{
  "tools": {
    "sandbox": "docker"
  },
  "context": {
    "fileName": ["GEMINI.md"]
  }
}
```

Sources:

* Sandboxing configuration: https://geminicli.com/docs/cli/sandbox/ and https://geminicli.com/docs/reference/configuration/
* Context file configuration: https://geminicli.com/docs/reference/configuration/

### 3) Automation-friendly defaults (project)

Goal: stable machine output and fewer surprises in CI.

```json
{
  "output": {
    "format": "json"
  },
  "general": {
    "defaultApprovalMode": "plan"
  }
}
```

Notes:

* `output.format` supports `text` or `json` (Source: https://geminicli.com/docs/reference/configuration/)
* `defaultApprovalMode` supports `default`, `auto_edit`, `plan` (Source: https://geminicli.com/docs/reference/configuration/)
* If you need tool execution in CI, prefer explicit `--sandbox` + explicit approval mode per run, and parse `--output-format` output. (Sources: https://geminicli.com/docs/cli/cli-reference/ and https://geminicli.com/docs/cli/headless/)

---

## If something is unclear or undocumented

This guide avoids guessing. If you find behavior that differs from the official docs:

1. Check your CLI version (`gemini --version`).
2. Check whether you’re in an untrusted folder safe mode (Trusted Folders).
3. Consult the official troubleshooting guide and open a GitHub issue if needed.

Sources:

* Troubleshooting: https://geminicli.com/docs/resources/troubleshooting/
* Trusted folders: https://geminicli.com/docs/cli/trusted-folders/
* Feedback / issues: https://github.com/google-gemini/gemini-cli/issues/new
