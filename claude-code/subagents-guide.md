# Subagents & Multi-Agent Workflows — Claude Code

Detailed guide for creating and orchestrating subagents in Claude Code on Windows.

> **Docs**: [docs.anthropic.com/.../sub-agents](https://docs.anthropic.com/en/docs/claude-code/sub-agents)

---

## Built-in Subagents

Claude Code ships with three built-in subagents:

| Subagent | Model | Tools | Best For |
|---|---|---|---|
| **Explore** | Haiku (fast, cheap) | Read-only (Glob, Grep, Read) | File discovery, code search, codebase exploration |
| **Plan** | Inherited from main | Read-only | Codebase research for planning |
| **General-purpose** | Inherited from main | All tools | Complex research, multi-step operations, code mods |

Check active subagents with `/statusline`.

---

## Creating Custom Subagents

### Method 1: Interactive Wizard

```
/agents
```

- View all available subagents
- Create new ones with guided setup or AI generation
- Edit existing subagent configuration
- Delete custom subagents

### Method 2: Manual File Creation

Create a Markdown file with YAML frontmatter:

#### User-level (available in all projects)

```
%USERPROFILE%\.claude\agents\<agent-name>.md
```

#### Project-level (shared with team via git)

```
.claude\agents\<agent-name>.md
```

### Method 3: CLI Flag (ephemeral)

```powershell
claude --agents '{ "code-reviewer": { "description": "Reviews code for quality", "prompt": "You are a code reviewer...", "tools": ["Read", "Grep", "Glob", "Bash"], "model": "sonnet" } }'
```

---

## Subagent File Format

```markdown
---
name: agent-name
description: What this agent does. Claude uses this to decide when to delegate.
tools: Read, Grep, Glob, Bash
disallowedTools: Write, Edit
model: sonnet
permissionMode: default
memory: user
maxTurns: 20
skills:
  - api-conventions
  - error-handling
---

Your system prompt / instructions here.
Be specific about what the agent should do when invoked.
```

### Frontmatter Reference

| Field | Type | Values / Notes |
|---|---|---|
| `name` | string | Agent identifier |
| `description` | string | **Critical** — Claude uses this to decide when to delegate |
| `tools` | list | See [Available Tools](#available-tools) |
| `disallowedTools` | list | Explicitly blocked tools |
| `model` | enum | `sonnet`, `opus`, `haiku`, `inherit` (default: `inherit`) |
| `permissionMode` | enum | See [Permission Modes](#permission-modes) |
| `skills` | list | Skill names to preload into the subagent |
| `mcpServers` | object | MCP server config (same format as `.mcp.json`) |
| `hooks` | object | Lifecycle hooks |
| `memory` | enum | `user`, `project`, `local` — enables persistent memory |
| `maxTurns` | number | Maximum conversation turns |

---

## Available Tools

| Tool | Purpose |
|---|---|
| `Read` | Read file contents |
| `Write` | Create/overwrite files |
| `Edit` | Edit existing files |
| `Bash` | Execute shell commands |
| `Grep` | Search file contents |
| `Glob` | Find files by pattern |
| `Task` | Spawn sub-subagents |
| `Task(name1, name2)` | Restrict which subagents can be spawned |

---

## Permission Modes

| Mode | Behavior |
|---|---|
| `default` | Normal permission prompts |
| `acceptEdits` | Auto-accept file edits, prompt for other actions |
| `dontAsk` | Auto-accept most actions |
| `delegate` | Used for agent teams |
| `bypassPermissions` | Skip all permission checks (use carefully) |
| `plan` | Read-only mode |

---

## Persistent Memory

Add `memory` to an agent to let it build up knowledge over time:

```markdown
---
name: code-reviewer
description: Reviews code for quality and best practices
memory: user
---

As you review code, update your agent memory with patterns,
conventions, and recurring issues you discover.
```

Memory is stored as `MEMORY.md` files:

| Scope | Location |
|---|---|
| `user` | `%USERPROFILE%\.claude\agent-memory\<name>\` |
| `project` | `.claude\agent-memory\<name>\` |
| `local` | `.claude\agent-memory-local\<name>\` |

---

## Running Subagents

### Automatic Delegation

Claude automatically delegates based on the `description` field:

```
Fix the failing unit tests
```

If a subagent's description matches, Claude routes the task.

### Explicit Delegation

```
Use the code-reviewer subagent to review my recent changes
Use the debugger subagent to fix the error in auth.py
```

### Foreground vs Background

| Mode | How | Behavior |
|---|---|---|
| **Foreground** | Default | Blocks main conversation. Permission prompts pass through. |
| **Background** | Say "run in background" or `Ctrl+B` | Runs concurrently. Auto-denies unapproved permissions. |

> [!NOTE]
> Background subagents **cannot** use MCP tools or ask clarifying questions.

To disable background tasks:

```powershell
$env:CLAUDE_CODE_DISABLE_BACKGROUND_TASKS = "1"
```

---

## Common Multi-Agent Patterns

### Pattern 1: Isolate High-Volume Operations

```
Use a subagent to run the test suite and report only failing tests with errors
```

Keeps verbose test output out of your main context window.

### Pattern 2: Parallel Research

```
Research the authentication, database, and API modules in parallel using separate subagents
```

Each subagent gets its own context window, preventing cross-contamination.

### Pattern 3: Chain Subagents

```
Use the code-reviewer to find performance issues, then use the optimizer to fix them
```

Sequential pipeline: reviewer → optimizer.

### Pattern 4: Coordinator Agent

```markdown
---
name: coordinator
description: Coordinates work across specialized agents
tools: Task(worker, researcher), Read, Bash
---

You are a project coordinator. Delegate:
- Research tasks to the `researcher` subagent
- Implementation tasks to the `worker` subagent
Synthesize results and present a summary.
```

### When to Use Subagents vs Main Conversation

| Use Main Conversation | Use Subagents |
|---|---|
| Frequent back-and-forth | Self-contained tasks |
| Multiple phases sharing context | Verbose output you don't need |
| Quick, targeted changes | Enforced tool restrictions |
| Latency matters | Parallel work |

---

## Example Subagents

### Code Reviewer

**File**: `.claude/agents/code-reviewer.md`

```markdown
---
name: code-reviewer
description: Expert code review specialist. Proactively reviews code for quality, security, and maintainability. Use immediately after writing or modifying code.
tools: Read, Grep, Glob, Bash
model: inherit
---

You are a senior code reviewer ensuring high standards.

When invoked:
1. Run `git diff` to see recent changes
2. Focus on modified files
3. Begin review immediately

Review checklist:
- Code is clear and readable
- Functions and variables are well-named
- No duplicated code
- Proper error handling
- No exposed secrets or API keys
- Input validation implemented
- Good test coverage
- Performance considerations addressed

Provide feedback organized by priority:
- **Critical issues** (must fix)
- **Warnings** (should fix)
- **Suggestions** (consider improving)

Include specific examples of how to fix issues.
```

### Debugger

**File**: `.claude/agents/debugger.md`

```markdown
---
name: debugger
description: Debugging specialist for errors, test failures, and unexpected behavior. Use proactively when encountering any issues.
tools: Read, Edit, Bash, Grep, Glob
---

You are an expert debugger specializing in root cause analysis.

When invoked:
1. Capture error message and stack trace
2. Identify reproduction steps
3. Isolate the failure location
4. Implement minimal fix
5. Verify solution works

For each issue, provide:
- Root cause explanation
- Evidence supporting the diagnosis
- Specific code fix
- Testing approach
- Prevention recommendations

Focus on fixing the underlying issue, not the symptoms.
```

### Security Auditor (Read-Only)

**File**: `.claude/agents/security-auditor.md`

```markdown
---
name: security-auditor
description: Security audit specialist. Reviews code for vulnerabilities, secret exposure, and security best practices.
tools: Read, Grep, Glob
disallowedTools: Write, Edit, Bash
model: opus
---

You are a security auditor. Scan the codebase for:
- Hardcoded secrets, API keys, passwords
- SQL injection vulnerabilities
- XSS vulnerabilities
- Insecure dependencies
- Missing input validation
- Improper error handling that leaks info

Report findings with severity (Critical/High/Medium/Low) and remediation steps.
```

### Test Runner

**File**: `.claude/agents/test-runner.md`

```markdown
---
name: test-runner
description: Runs test suites and reports results. Use when you need to verify code changes work correctly.
tools: Read, Bash, Grep
model: haiku
---

You are a test execution specialist.

When invoked:
1. Identify the test framework (pytest, jest, etc.)
2. Run the full test suite or specified tests
3. Parse results
4. Report:
   - Total tests, passed, failed, skipped
   - Failed test details with error messages
   - Suggested fixes for failures
```

---

## Preloading Skills into Subagents

```markdown
---
name: api-developer
description: Implement API endpoints following team conventions
skills:
  - api-conventions
  - error-handling-patterns
---

Implement API endpoints. Follow the conventions and patterns
from the preloaded skills.
```

Skills listed in `skills:` are loaded into the subagent's context at startup.

---

## MCP Servers in Subagents

Give a subagent its own MCP servers:

```markdown
---
name: data-analyst
description: Queries databases and analyzes data
tools: Read, Bash
mcpServers:
  postgres:
    command: npx
    args: ["-y", "@anthropic-ai/mcp-server-postgres"]
    env:
      POSTGRES_CONNECTION_STRING: "${POSTGRES_CONNECTION_STRING}"
---
```

> [!IMPORTANT]
> MCP servers in subagents are **not** available in background mode.
