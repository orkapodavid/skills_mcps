# ChatGPT Codex CLI — Comprehensive Practical Guide (2026)

A practical, copy/paste playbook for **Codex CLI** (the `codex` command): OpenAI’s local coding agent that runs in your terminal, can read/modify files in a chosen workspace, and (optionally) run shell commands under a sandbox + approval model.

Use it when you want:

- **Repo-aware help** (explain architecture, find bugs, propose changes)
- **Agentic edits** with guardrails (sandbox + approvals)
- **Repeatable automation** (`codex exec` in scripts/CI, JSONL output, schemas)
- **Integrations** (IDE extension, GitHub Action, MCP servers)

---

## Sources (authoritative)

- OpenAI Developers — Codex CLI overview: https://developers.openai.com/codex/cli/
- OpenAI Developers — Codex CLI features: https://developers.openai.com/codex/cli/features/
- OpenAI Developers — Codex CLI command line options (full command/flag reference): https://developers.openai.com/codex/cli/reference/
- OpenAI Developers — Codex CLI slash commands: https://developers.openai.com/codex/cli/slash-commands
- OpenAI Developers — Authentication: https://developers.openai.com/codex/auth
- OpenAI Developers — Security (sandbox & approvals, managed config, requirements.toml): https://developers.openai.com/codex/security
- OpenAI Developers — Config basics: https://developers.openai.com/codex/config-basic
- OpenAI Developers — Advanced config: https://developers.openai.com/codex/config-advanced
- OpenAI Developers — Config reference (all keys, requirements.toml): https://developers.openai.com/codex/config-reference
- OpenAI Developers — Non-interactive mode (`codex exec`): https://developers.openai.com/codex/noninteractive
- OpenAI Developers — MCP (Model Context Protocol): https://developers.openai.com/codex/mcp
- OpenAI Developers — Rules (`.rules`, execpolicy): https://developers.openai.com/codex/rules
- OpenAI Developers — Windows setup: https://developers.openai.com/codex/windows
- OpenAI Developers — Codex GitHub Action: https://developers.openai.com/codex/github-action
- OpenAI Developers — Codex changelog (release notes): https://developers.openai.com/codex/changelog
- OpenAI GitHub — `openai/codex` README (install methods, binaries): https://github.com/openai/codex
- npm — `@openai/codex` package: https://www.npmjs.com/package/@openai/codex

---

## Mental model

Think of Codex CLI as three things glued together:

1. **A repo-aware chat UI (TUI)** that can read your workspace and maintain local session history.
2. **A controlled execution engine**:
   - **Sandbox mode** defines what it *can* do (read-only vs workspace-write vs full access).
   - **Approval policy** defines when it *must ask you*.
3. **A configuration + policy stack** that merges:
   - CLI flags (highest)
   - optional profiles
   - project config (trusted projects only)
   - user config
   - system/managed config (if present)
   - built-in defaults

This is why Codex can feel “stateful”: your **workspace**, **config**, **auth**, and **session history** all affect what happens when you type `codex`.

---

## Install & update

### Supported platforms (practical)

- **macOS**: supported
- **Linux**: supported
- **Windows**: experimental; best experience is **WSL** (see Windows section) 
  - Source: https://developers.openai.com/codex/cli/ and https://developers.openai.com/codex/windows

### Install (recommended paths)

| Method | Good for | Command(s) | Source |
|---|---|---|---|
| npm global | Cross-platform, fast updates | `npm i -g @openai/codex` | https://developers.openai.com/codex/cli/ |
| Homebrew cask (macOS) | macOS-native install | `brew install --cask codex` | https://github.com/openai/codex |
| GitHub release binary | No Node/npm, pinned version | Download + extract the correct tarball | https://github.com/openai/codex/releases/latest |

#### Install via npm

```bash
npm i -g @openai/codex
```

Run it:

```bash
codex
```

#### Install via Homebrew (macOS)

```bash
brew install --cask codex
```

#### Install from GitHub release binaries

From the GitHub README, typical assets include:

- macOS arm64: `codex-aarch64-apple-darwin.tar.gz`
- macOS x86_64: `codex-x86_64-apple-darwin.tar.gz`
- Linux x86_64 musl: `codex-x86_64-unknown-linux-musl.tar.gz`
- Linux arm64 musl: `codex-aarch64-unknown-linux-musl.tar.gz`

Source: https://github.com/openai/codex

Example (Linux x86_64):

```bash
# Replace URL with the exact asset URL from the release page.
# This is a template; do not copy/paste without updating the URL.
URL="https://github.com/openai/codex/releases/download/<TAG>/codex-x86_64-unknown-linux-musl.tar.gz"

curl -L "$URL" -o codex.tar.gz
mkdir -p ~/.local/bin

# Inspect contents (usually a single binary with a platform-specific name)
tar -tzf codex.tar.gz

# Extract, rename to 'codex', and add to PATH
tar -xzf codex.tar.gz
# Example name; adjust to the extracted filename
mv codex-x86_64-unknown-linux-musl ~/.local/bin/codex
chmod +x ~/.local/bin/codex

~/.local/bin/codex --help
```

> Undocumented / unclear: The official docs don’t publish a single canonical “binary install” snippet because asset names and tags vary by release. Use the GitHub release page and adapt the template above.

### Update

#### Update with npm

```bash
npm i -g @openai/codex@latest
```

Source: https://developers.openai.com/codex/cli/

#### Update with Homebrew (macOS)

```bash
brew update
brew upgrade --cask codex
```

Source: Homebrew behavior; Codex cask reference is in the GitHub README (https://github.com/openai/codex).

#### Track changes

- Codex release notes: https://developers.openai.com/codex/changelog
- GitHub releases: https://github.com/openai/codex/releases

### Uninstall

| Install method | Uninstall | Notes |
|---|---|---|
| npm global | `npm rm -g @openai/codex` | Removes the CLI binary wrapper installed by npm. |
| Homebrew cask | `brew uninstall --cask codex` | Removes the cask-managed install. |
| GitHub binary | Delete the extracted binary | E.g., `rm ~/.local/bin/codex` |

Local state cleanup (optional):

```bash
rm -rf ~/.codex
```

> Why this matters: `~/.codex` can include **auth tokens** (`auth.json` in file mode), session transcripts, and logs. Treat it like sensitive application state.

Source for CODEX_HOME default: https://developers.openai.com/codex/config-advanced#config-and-state-locations

---

## Authenticate

Codex supports two OpenAI sign-in methods:

1. **Sign in with ChatGPT** (OAuth) — uses your ChatGPT plan/workspace permissions.
2. **Sign in with an API key** — usage billed on OpenAI Platform API pricing.

Source: https://developers.openai.com/codex/auth

### How the CLI chooses credentials

- If no valid session is available, the CLI defaults to **ChatGPT login** when using OpenAI models.
- Credentials are cached and shared between CLI and IDE extension.

Source: https://developers.openai.com/codex/auth#openai-authentication and #login-caching

### Login commands (CLI)

The CLI has a dedicated `login` command:

```bash
codex login
```

From the command reference: `codex login` opens a browser for ChatGPT OAuth by default.

Source: https://developers.openai.com/codex/cli/reference#codex-login

#### Device code flow (headless-friendly)

```bash
codex login --device-auth
```

Source: https://developers.openai.com/codex/cli/reference#codex-login and https://developers.openai.com/codex/auth#preferred-device-code-authentication-beta

#### API key login (piped over stdin)

From the CLI reference, `--with-api-key` reads an API key from stdin.

```bash
printenv OPENAI_API_KEY | codex login --with-api-key
```

Source: https://developers.openai.com/codex/cli/reference#codex-login

> Note: OpenAI’s Codex docs recommend **API key auth for programmatic Codex workflows** (CI/CD) and warn against exposing execution in untrusted/publicly triggerable environments.
> Source: https://developers.openai.com/codex/auth#sign-in-with-an-api-key

### Check login status

```bash
codex login status
```

It exits `0` when credentials are present (useful in automation).

Source: https://developers.openai.com/codex/cli/reference#codex-login

### Logout

```bash
codex logout
```

Source: https://developers.openai.com/codex/cli/reference#codex-logout

### Where credentials are stored

Codex can cache credentials in:

- `~/.codex/auth.json` (plaintext file-based storage)
- Your OS credential store (keychain/keyring)

Source: https://developers.openai.com/codex/auth#login-caching

Control storage with `cli_auth_credentials_store`:

```toml
# file | keyring | auto
cli_auth_credentials_store = "keyring"
```

Source: https://developers.openai.com/codex/auth#credential-storage and config key reference: https://developers.openai.com/codex/config-reference

> Why this matters: If you use file-based storage, `~/.codex/auth.json` contains access tokens. Treat it like a password (don’t commit, paste, or share). (https://developers.openai.com/codex/auth#credential-storage)

### Switching workspaces / restricting accounts (managed environments)

Admins can restrict authentication mode and workspace:

```toml
forced_login_method = "chatgpt" # or "api"
forced_chatgpt_workspace_id = "00000000-0000-0000-0000-000000000000"
```

If active credentials don’t match restrictions, Codex logs out and exits.

Source: https://developers.openai.com/codex/auth#enforce-a-login-method-or-workspace and config reference keys.

---

## Core usage modes

### 1) Interactive mode (TUI)

Launch:

```bash
codex
```

- Full-screen terminal UI
- You can provide an initial prompt:

```bash
codex "Explain this codebase to me"
```

Source: https://developers.openai.com/codex/cli/features#running-in-interactive-mode

**Resuming:**

```bash
codex resume
codex resume --last
codex resume --all
```

Source: https://developers.openai.com/codex/cli/features#resuming-conversations and https://developers.openai.com/codex/cli/reference#codex-resume

### 2) One-shot prompt (still interactive UI, but starts working immediately)

```bash
codex "Find the flaky tests and explain why"
```

Source: https://developers.openai.com/codex/cli/features#running-with-an-input-prompt

### 3) Non-interactive / headless mode (scripts & CI)

Use `codex exec`:

```bash
codex exec "summarize the repo structure and list the top 5 risky areas"
```

Behavior:

- Progress streams to **stderr**
- Final message prints to **stdout**

Source: https://developers.openai.com/codex/noninteractive#basic-usage

---

## Essential commands & flags

This section is intentionally “smallest set you’ll actually use”, with pointers to the full reference.

### Command overview

Codex CLI command catalog (stable/experimental) lives here:

- https://developers.openai.com/codex/cli/reference#command-overview

Common commands:

| Command | Purpose | Typical use |
|---|---|---|
| `codex` | Start interactive session | everyday work |
| `codex exec` (`codex e`) | Run non-interactively | CI, scripts |
| `codex login` / `logout` | Manage auth | first-run, CI |
| `codex resume` / `fork` | Continue or branch a session | long tasks |
| `codex features` | Toggle feature flags | enable experiments |
| `codex completion` | Shell completions | speed |
| `codex mcp` | Manage MCP servers | add tools/context |
| `codex sandbox` | Run commands inside sandbox | verify policies |
| `codex execpolicy` | Evaluate rules files | validate `.rules` |

Source: https://developers.openai.com/codex/cli/reference

### Global flags (high-value)

From the CLI reference (global flags):

| Flag | Values | What it does | Source |
|---|---|---|---|
| `--cd`, `-C` | `path` | Sets working directory/workspace root | https://developers.openai.com/codex/cli/reference#global-flags |
| `--model`, `-m` | model slug | Override model (e.g. `gpt-5.3-codex`) | https://developers.openai.com/codex/cli/reference#global-flags |
| `--sandbox`, `-s` | `read-only` \| `workspace-write` \| `danger-full-access` | Sandbox policy for commands | https://developers.openai.com/codex/cli/reference#global-flags |
| `--ask-for-approval`, `-a` | `untrusted` \| `on-failure` \| `on-request` \| `never` | When Codex pauses for approval | https://developers.openai.com/codex/cli/reference#global-flags |
| `--full-auto` | boolean | Shortcut for `--ask-for-approval on-request` + `--sandbox workspace-write` | https://developers.openai.com/codex/cli/reference#global-flags |
| `--add-dir` | repeatable path | Add writable roots beyond workspace | https://developers.openai.com/codex/cli/reference#global-flags |
| `--config`, `-c` | `key=value` | One-off config override (parses as JSON if possible) | https://developers.openai.com/codex/cli/reference#global-flags |
| `--profile`, `-p` | string | Load profile from `~/.codex/config.toml` | https://developers.openai.com/codex/cli/reference#global-flags |
| `--search` | boolean | Enable live web search for that run | https://developers.openai.com/codex/cli/reference#global-flags |
| `--yolo` / `--dangerously-bypass-approvals-and-sandbox` | boolean | No sandbox, no approvals (danger) | https://developers.openai.com/codex/cli/reference#global-flags |
| `--image`, `-i` | `path[,path...]` | Attach images to the initial prompt | https://developers.openai.com/codex/cli/reference#global-flags |

### `codex exec` flags (automation essentials)

| Flag | What it does | Source |
|---|---|---|
| `--json` | Emit JSON Lines events to stdout | https://developers.openai.com/codex/cli/reference#codex-exec |
| `--output-last-message`, `-o` | Write final assistant message to a file | https://developers.openai.com/codex/cli/reference#codex-exec |
| `--output-schema` | Enforce final response to match a JSON Schema | https://developers.openai.com/codex/cli/reference#codex-exec and https://developers.openai.com/codex/noninteractive#create-structured-outputs-with-a-schema |
| `--ephemeral` | Don’t persist rollout/session files to disk | https://developers.openai.com/codex/cli/reference#codex-exec and https://developers.openai.com/codex/noninteractive#basic-usage |
| `--skip-git-repo-check` | Allow running outside a Git repo | https://developers.openai.com/codex/cli/reference#codex-exec and https://developers.openai.com/codex/noninteractive#git-repository-required |
| `PROMPT` as `-` | Read prompt from stdin | https://developers.openai.com/codex/cli/reference#codex-exec |

Example: machine-readable run + capture final message

```bash
codex exec --json "summarize the repo structure" | jq .
```

```bash
codex exec --json "summarize the repo structure" -o ./final.txt
```

Source: https://developers.openai.com/codex/noninteractive#make-output-machine-readable

---

## Configuration & where files live

### Configuration layers (precedence)

From highest precedence to lowest:

1. CLI flags and `--config` overrides
2. Profile values (from `--profile`)
3. Project config files `.codex/config.toml` (trusted projects only), ordered from project root down to cwd (closest wins)
4. User config `~/.codex/config.toml`
5. System config `/etc/codex/config.toml` (Unix)
6. Built-in defaults

Source: https://developers.openai.com/codex/config-basic#configuration-precedence

### Key paths (macOS/Linux)

| Purpose | Path | Source |
|---|---|---|
| Codex home (default) | `~/.codex` | https://developers.openai.com/codex/config-advanced#config-and-state-locations |
| User config | `~/.codex/config.toml` | https://developers.openai.com/codex/config-basic |
| Project config | `.codex/config.toml` (inside repo; trusted only) | https://developers.openai.com/codex/config-basic |
| Auth cache (file mode) | `~/.codex/auth.json` | https://developers.openai.com/codex/auth#login-caching |
| Logs default dir | `$CODEX_HOME/log` (unless `log_dir` overrides) | https://developers.openai.com/codex/config-reference (`log_dir`) |
| Example TUI log name | `codex-tui.log` in `log_dir` | https://developers.openai.com/codex/config-basic (`log_dir` example) |
| System config | `/etc/codex/config.toml` | https://developers.openai.com/codex/config-basic#configuration-precedence |
| Managed defaults | `/etc/codex/managed_config.toml` | https://developers.openai.com/codex/security#managed-defaults-managed_configtoml |
| Admin requirements | `/etc/codex/requirements.toml` | https://developers.openai.com/codex/security#admin-enforced-requirements-requirementstoml |
| Rules (user layer) | `~/.codex/rules/default.rules` | https://developers.openai.com/codex/rules#create-a-rules-file |

### Windows-specific paths

| Purpose | Path | Source |
|---|---|---|
| Managed defaults (Windows/non-Unix) | `~/.codex/managed_config.toml` | https://developers.openai.com/codex/security#managed-defaults-managed_configtoml |

> Practical note: On Windows, prefer running Codex in **WSL** so config paths are the Linux ones (e.g. `/home/<user>/.codex`).

Source: https://developers.openai.com/codex/windows

### Common config keys (what you actually edit)

From Config basics + reference:

| Key | Meaning | Example | Source |
|---|---|---|---|
| `model` | default model | `model = "gpt-5.2"` | https://developers.openai.com/codex/config-basic |
| `approval_policy` | when approvals happen | `approval_policy = "on-request"` | https://developers.openai.com/codex/config-basic |
| `sandbox_mode` | sandbox policy | `sandbox_mode = "workspace-write"` | https://developers.openai.com/codex/config-basic |
| `web_search` | `disabled`/`cached`/`live` | `web_search = "cached"` | https://developers.openai.com/codex/config-basic |
| `log_dir` | log output directory | `log_dir = "/abs/path"` | https://developers.openai.com/codex/config-basic |
| `[features]` | feature flags | `features.unified_exec = true` | https://developers.openai.com/codex/config-basic |

### Feature flags (quick map)

Codex exposes feature flags in `[features]` (some stable, some experimental). A few notable ones from Config basics:

| Feature | Default | Maturity | What it affects | Source |
|---|---:|---|---|---|
| `collaboration_modes` | true | Stable | Enables collaboration modes (e.g. plan mode) | https://developers.openai.com/codex/config-basic |
| `unified_exec` | false | Beta | Unified PTY-backed exec tool (affects `/ps`, background terminals) | https://developers.openai.com/codex/config-basic |
| `shell_snapshot` | false | Beta | Snapshot environment to speed repeated commands | https://developers.openai.com/codex/config-basic |
| `apps` | false | Experimental | ChatGPT Apps/connectors support | https://developers.openai.com/codex/config-basic |
| `use_linux_sandbox_bwrap` | false | Experimental | Alternative Linux sandbox pipeline | https://developers.openai.com/codex/config-basic |

Enable via CLI:

```bash
codex --enable unified_exec
```

Source: https://developers.openai.com/codex/cli/reference#global-flags and https://developers.openai.com/codex/config-basic#enabling-features

---

## Output formats / JSON / automation patterns

### Human output (default)

- In interactive mode: TUI renders transcript.
- In non-interactive mode (`codex exec`): final assistant message prints to stdout; progress goes to stderr.

Source: https://developers.openai.com/codex/noninteractive#basic-usage

### JSON Lines stream (`codex exec --json`)

Use JSONL when you want to:

- track progress events
- extract tool usage
- make CI logs machine-parseable

```bash
codex exec --json "summarize the repo" | jq .
```

Source: https://developers.openai.com/codex/noninteractive#make-output-machine-readable

### Write final output to a file

```bash
codex exec --json "generate release notes" -o ./release-notes.md
```

Source: `--output-last-message` in https://developers.openai.com/codex/cli/reference#codex-exec

### Enforce a schema (stable automation)

1) Create a JSON Schema file (example):

```json
{
  "type": "object",
  "properties": {
    "project_name": {"type": "string"},
    "programming_languages": {
      "type": "array",
      "items": {"type": "string"}
    }
  },
  "required": ["project_name", "programming_languages"],
  "additionalProperties": false
}
```

2) Run:

```bash
codex exec "Extract project metadata" \
  --output-schema ./schema.json \
  -o ./project-metadata.json
```

Source: https://developers.openai.com/codex/noninteractive#create-structured-outputs-with-a-schema

### Exit codes (what’s confirmed)

- Some commands explicitly mention **non-zero exits on failure**, e.g. `codex apply` exits non-zero if `git apply` fails.

Source: https://developers.openai.com/codex/cli/reference#codex-apply

> Undocumented / unclear: The docs do not publish a single “exit code contract table” for all commands. For automation, treat any non-zero exit as failure and parse JSONL for `error` items when using `--json`.

---

## Safety / permissions model

Codex’s safety is mainly a combination of:

- **Sandbox mode** (technical capability limits)
- **Approval policy** (human-in-the-loop prompts)
- Optional **rules** (`.rules`) controlling commands outside the sandbox
- Optional **managed requirements** (`requirements.toml`) constraining user choices

Primary source: https://developers.openai.com/codex/security

### Sandbox modes

| Sandbox | What it usually means | Source |
|---|---|---|
| `read-only` | Can read files; edits/commands require approval | https://developers.openai.com/codex/security#common-sandbox-and-approval-combinations |
| `workspace-write` | Can edit within workspace; network off by default | https://developers.openai.com/codex/security |
| `danger-full-access` | Broad filesystem/network; use only in isolated environments | https://developers.openai.com/codex/security |

On local machines, Codex uses OS-enforced sandboxing:

- macOS: Seatbelt policies (`sandbox-exec`)
- Linux: Landlock + seccomp (optional bubblewrap pipeline)
- Windows: WSL uses Linux sandbox; native Windows sandbox is experimental

Source: https://developers.openai.com/codex/security#os-level-sandbox

### Approval policies

Approval policies map to when Codex pauses for confirmation:

- `untrusted`, `on-failure`, `on-request`, `never`

Source: https://developers.openai.com/codex/cli/reference#global-flags and config keys in https://developers.openai.com/codex/config-reference

### Common “good” combinations

| Intent | Command | Why | Source |
|---|---|---|---|
| Default safe-ish local work | `codex` | Auto preset depends on repo trust/version control; network off by default | https://developers.openai.com/codex/security#defaults-and-recommendations |
| Let it edit, ask before risky steps | `codex --sandbox workspace-write --ask-for-approval untrusted` | Edits OK, but commands outside trusted set prompt | https://developers.openai.com/codex/security#common-sandbox-and-approval-combinations |
| CI read-only analysis | `codex exec --sandbox read-only --ask-for-approval never "..."` | No prompts, no edits | https://developers.openai.com/codex/security#common-sandbox-and-approval-combinations |
| “YOLO” (avoid) | `codex --yolo` | No sandbox, no approvals | https://developers.openai.com/codex/cli/reference#global-flags |

### Network access

- **Default** for local CLI is network access **off**.
- You can enable outbound network in workspace-write mode:

```toml
[sandbox_workspace_write]
network_access = true
```

Source: https://developers.openai.com/codex/security#network-access-elevated-risk

> Why this matters: Network access increases exposure to prompt injection and data exfiltration risks. Treat web content as untrusted even in cached search mode.

### Web search modes (cached vs live)

Codex web search is a first-party tool with a “cached” default:

- `web_search = "cached"` (default): uses an OpenAI-maintained index (reduces exposure to arbitrary live content)
- `web_search = "live"` or `--search`: fetches current pages
- `web_search = "disabled"`: removes the tool

Source: https://developers.openai.com/codex/cli/features#web-search and https://developers.openai.com/codex/config-basic#web-search-mode

### Prevent accidental secret leakage

Use multiple layers:

1. **Keep network off** unless needed (`network_access = false` default)
2. **Restrict env vars passed to subprocesses** via `shell_environment_policy`

Example (allow only PATH + HOME):

```toml
[shell_environment_policy]
include_only = ["PATH", "HOME"]
```

Source: https://developers.openai.com/codex/config-basic#command-environment and config reference keys.

3. **Use rules** to forbid or prompt on risky commands outside sandbox

Example: forbid destructive removes outside sandbox:

```python
# ~/.codex/rules/default.rules
prefix_rule(
  pattern = ["rm"],
  decision = "forbidden",
  justification = "Avoid destructive deletes; prefer git clean -fd or review first."
)
```

Rules docs: https://developers.openai.com/codex/rules

4. **Treat auth files as secrets** (`~/.codex/auth.json` in file mode)

Auth docs: https://developers.openai.com/codex/auth#credential-storage

---

## Common workflows (copy/paste)

### Quick repo explanation

```bash
codex "Give me a high-level overview of this repo: major modules, entrypoints, and how to run tests."
```

Tip: if you want to start from a different directory without `cd`:

```bash
codex --cd /path/to/repo "Explain how this repo is structured"
```

Source: `--cd` global flag in https://developers.openai.com/codex/cli/reference#global-flags

### Targeted bugfix (safe defaults)

```bash
codex --sandbox workspace-write --ask-for-approval on-request \
  "Reproduce the failing test, identify the minimal fix, implement it, and stop."
```

(Equivalent preset: `--full-auto`)

Source: `--full-auto` definition in https://developers.openai.com/codex/cli/reference#global-flags

### Non-interactive code review in CI (read-only)

```bash
codex exec --sandbox read-only --ask-for-approval never \
  "Review the changes in this branch and list: 1) correctness risks, 2) missing tests, 3) security issues."
```

Source: non-interactive docs + security combinations

### Make a CI step produce JSON

```bash
codex exec --json --sandbox read-only --ask-for-approval never \
  "Extract: package manager, test command, and primary language" \
  -o ./codex-result.json
```

Then parse (example):

```bash
cat ./codex-result.json
```

### Use a schema for stable downstream parsing

```bash
codex exec "Classify repo" \
  --output-schema ./schema.json \
  -o ./classification.json
```

Source: https://developers.openai.com/codex/noninteractive#create-structured-outputs-with-a-schema

### Shell completions

```bash
eval "$(codex completion zsh)"
```

Source: https://developers.openai.com/codex/cli/features#shell-completions

### Manage feature flags

```bash
codex features list
codex features enable unified_exec
codex features disable shell_snapshot
```

Source: https://developers.openai.com/codex/cli/features#feature-flags

### Add an MCP server (Context7 example)

```bash
codex mcp add context7 -- npx -y @upstash/context7-mcp
```

Source: https://developers.openai.com/codex/mcp#add-an-mcp-server

Then verify in the TUI:

- Run `/mcp` inside an interactive session

Source: https://developers.openai.com/codex/mcp#terminal-ui-tui

---

## Troubleshooting (quick index)

Jump points:

- **Auth/login issues** → [Auth troubleshooting](#auth-troubleshooting)
- **Permissions/sandbox denials** → [Sandbox and approvals](#sandbox-and-approvals) + [Rules](#rules-and-execpolicy)
- **CI/headless pain** → [Non-interactive mode pitfalls](#non-interactive-mode-pitfalls)
- **Windows issues** → [Windows notes](#windows-notes)

### Auth troubleshooting

**Symptom: browser login fails / remote environment**

- Use device code auth:

```bash
codex login --device-auth
```

Source: https://developers.openai.com/codex/auth#preferred-device-code-authentication-beta

**Symptom: can’t receive localhost callback**

- Use SSH port forwarding:

```bash
ssh -L 1455:localhost:1455 user@remote
```

Then run `codex login` in that SSH session.

Source: https://developers.openai.com/codex/auth#fallback-forward-the-localhost-callback-over-ssh

**Symptom: need headless login without browser**

- Authenticate on a machine with a browser and copy `auth.json`:

```bash
ssh user@remote 'mkdir -p ~/.codex && cat > ~/.codex/auth.json' < ~/.codex/auth.json
```

Source: https://developers.openai.com/codex/auth#fallback-authenticate-locally-and-copy-your-auth-cache

**Symptom: token storage concerns**

- Use OS keyring instead of file cache:

```toml
cli_auth_credentials_store = "keyring"
```

Source: https://developers.openai.com/codex/auth#credential-storage

### Sandbox and approvals

**Symptom: Codex refuses to run a command / requests approval unexpectedly**

- Check current policy and writable roots:
  - In TUI: `/status`
  - Or set explicitly on launch:

```bash
codex --sandbox workspace-write --ask-for-approval on-request
```

Sources:

- `/status`: https://developers.openai.com/codex/cli/slash-commands#inspect-the-session-with-status
- policy flags: https://developers.openai.com/codex/cli/reference#global-flags

**Symptom: need network for installs/tests**

- Enable network inside workspace-write sandbox:

```toml
[sandbox_workspace_write]
network_access = true
```

Source: https://developers.openai.com/codex/security#network-access-elevated-risk

> Why this matters: enabling network increases the blast radius of prompt injection and accidental secret exfiltration.

### Rules and execpolicy

**Symptom: Codex keeps prompting for the same safe command outside sandbox**

- Add a rule to allow it (carefully):
  - Place `.rules` under a Codex rules directory (user layer example shown below)

Source: https://developers.openai.com/codex/rules#create-a-rules-file

**Test your rules:**

```bash
codex execpolicy check --pretty \
  --rules ~/.codex/rules/default.rules \
  -- gh pr view 7888 --json title,body,comments
```

Source: https://developers.openai.com/codex/rules#test-a-rule-file

### Non-interactive mode pitfalls

**Symptom: `codex exec` fails outside a Git repo**

- Run inside a Git repo, or explicitly override:

```bash
codex exec --skip-git-repo-check "..."
```

Source: https://developers.openai.com/codex/noninteractive#git-repository-required

**Symptom: you need zero local state written**

```bash
codex exec --ephemeral "..."
```

Source: https://developers.openai.com/codex/noninteractive#basic-usage

**Symptom: want to keep CI logs readable**

- Prefer JSONL + `jq` filters, or suppress reasoning events:

```toml
hide_agent_reasoning = true
```

Source: config key in https://developers.openai.com/codex/config-reference and discussion in advanced config.

### Windows notes

- Prefer WSL2 and keep repos under `~/code/...` inside Linux filesystem (avoid `/mnt/c/...` for performance).
- Install Node.js inside WSL and then install Codex with npm.

Source: https://developers.openai.com/codex/windows#windows-subsystem-for-linux

---

## Appendix: cheat sheet

### Everyday interactive usage

```bash
codex
codex "Explain this repo"
codex --cd /path/to/repo
codex resume --last
```

### Safer presets

```bash
# Allow edits in workspace; ask before risky actions
codex --sandbox workspace-write --ask-for-approval on-request

# Read-only exploration
codex --sandbox read-only --ask-for-approval on-request
```

### Automation

```bash
codex exec "Generate release notes" | tee RELEASE_NOTES.md
codex exec --json "Summarize the repo" | jq .
codex exec --ephemeral "Triage issues"
```

### Auth

```bash
codex login
codex login --device-auth
printenv OPENAI_API_KEY | codex login --with-api-key
codex login status
codex logout
```

### MCP

```bash
codex mcp list
codex mcp add context7 -- npx -y @upstash/context7-mcp
codex mcp remove context7
```

(Full command details: https://developers.openai.com/codex/cli/reference#codex-mcp)

---

## Appendix: “good defaults” starter config templates

These templates assume Codex config files exist and are honored (they do), and are based on the documented keys.

### 1) Personal default: safe-ish local coding

File: `~/.codex/config.toml`

```toml
# ~/.codex/config.toml
model = "gpt-5.3-codex"
approval_policy = "on-request"
sandbox_mode = "workspace-write"
web_search = "cached"

# Keep network off by default; opt-in per project when needed.
[sandbox_workspace_write]
network_access = false

# Reduce secret leakage risk when Codex runs subprocesses.
[shell_environment_policy]
include_only = ["PATH", "HOME"]

# Optional: reduce noisy output in CI logs when you reuse this config.
hide_agent_reasoning = true
```

Sources:

- keys + examples: https://developers.openai.com/codex/config-basic
- key definitions: https://developers.openai.com/codex/config-reference
- security defaults: https://developers.openai.com/codex/security

### 2) Project-local overrides (trusted repos only)

File: `.codex/config.toml` in your repo

```toml
# .codex/config.toml
# Opt in to live web search for this project only
web_search = "live"

# Allow network access in this repo when needed for installs/tests
[sandbox_workspace_write]
network_access = true
```

Source: project config behavior + trust gating: https://developers.openai.com/codex/config-basic

### 3) Add a named profile for “deep review”

```toml
# ~/.codex/config.toml
[profiles.deep-review]
model = "gpt-5-pro"
model_reasoning_effort = "high"
approval_policy = "on-request"
sandbox_mode = "read-only"
```

Run:

```bash
codex --profile deep-review
```

Source: https://developers.openai.com/codex/config-advanced#profiles
