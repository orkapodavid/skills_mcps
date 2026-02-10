# Multi-Agent Workflows — Claude Code

Comprehensive guide covering **both** multi-agent approaches in Claude Code: **Subagents** (in-session helpers) and **Agent Teams** (parallel session orchestration).

> **Official Docs**:
> - [Subagents](https://docs.anthropic.com/en/docs/claude-code/sub-agents)
> - [Agent Teams](https://docs.anthropic.com/en/docs/claude-code/agent-teams)

---

## Table of Contents

1. [Choosing Your Multi-Agent Approach](#1-choosing-your-multi-agent-approach)
2. [Subagents — In-Session Delegation](#2-subagents--in-session-delegation)
3. [Agent Teams — Parallel Session Orchestration](#3-agent-teams--parallel-session-orchestration)
4. [Step-by-Step: Your First Subagent](#4-step-by-step-your-first-subagent)
5. [Step-by-Step: Your First Agent Team](#5-step-by-step-your-first-agent-team)
6. [Delegate Mode](#6-delegate-mode)
7. [Communication & Task Management](#7-communication--task-management)
8. [Quality Gates with Hooks](#8-quality-gates-with-hooks)
9. [Use Case Examples](#9-use-case-examples)
10. [Best Practices](#10-best-practices)
11. [Troubleshooting](#11-troubleshooting)
12. [Current Limitations](#12-current-limitations)

---

## 1. Choosing Your Multi-Agent Approach

Claude Code offers **two** multi-agent systems. Choose based on your needs:

| Feature | Subagents | Agent Teams |
|---|---|---|
| **Relationship** | Parent–child (report back to main) | Peer-to-peer (teammates communicate directly) |
| **Context** | Share parent's context window | Each gets its own independent context |
| **Communication** | Report → parent only | Message each other directly + shared task list |
| **Parallelism** | Background tasks possible | True parallel sessions |
| **Coordination** | Main conversation orchestrates | Lead agent or delegate mode orchestrates |
| **MCP access** | Yes (foreground only) | Yes |
| **Complexity** | Simple delegation | Complex multi-step coordination |
| **Status** | Stable | Experimental (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`) |

### When to Use Which

| Scenario | Use |
|---|---|
| Run tests and report results | **Subagent** |
| Quick file search / code exploration | **Subagent** (built-in Explore) |
| Research + implement in parallel | **Agent Team** |
| Multi-module refactoring | **Agent Team** |
| Competing debugging hypotheses | **Agent Team** |
| Cross-layer changes (frontend + backend + tests) | **Agent Team** |
| Self-contained, isolated task | **Subagent** |
| Tasks that need inter-agent debate | **Agent Team** |

---

## 2. Subagents — In-Session Delegation

Subagents are helper agents **within** your main Claude Code session. They run a task and report back.

### Built-in Subagents

| Name | Model | Tools | Purpose |
|---|---|---|---|
| **Explore** | Haiku (fast) | Read-only (Glob, Grep, Read) | File discovery, codebase exploration |
| **Plan** | Inherited | Read-only | Research for planning |
| **General-purpose** | Inherited | All tools | Complex operations, code mods |

### How Subagents Run

| Mode | Trigger | Behavior |
|---|---|---|
| **Foreground** | Default | Blocks main conversation; permission prompts pass through |
| **Background** | "Run in background" or `Ctrl+B` | Runs concurrently; MCP tools unavailable; auto-denies unapproved permissions |

### Creating Custom Subagents

**Location**: `.claude/agents/<name>.md` (project) or `%USERPROFILE%\.claude\agents\<name>.md` (global)

```markdown
---
name: code-reviewer
description: Reviews code for quality and best practices
tools: Read, Grep, Glob, Bash
model: inherit
memory: project
---

You are a senior code reviewer. When invoked:
1. Run `git diff` to see recent changes
2. Review for quality, security, and best practices
3. Report findings by priority: Critical > Warning > Suggestion
```

> [!TIP]
> See [subagents-guide.md](./subagents-guide.md) for the full frontmatter reference, permission modes, and 4 ready-to-use agent templates.

---

## 3. Agent Teams — Parallel Session Orchestration

Agent Teams let you orchestrate **multiple Claude Code sessions** working in parallel. Each teammate has its own context window, can communicate with other teammates directly, and shares a task list.

### Architecture

```
┌─────────────────────────────────────────────────┐
│                   LEAD SESSION                   │
│  (creates team, assigns tasks, coordinates)      │
├────────────┬────────────┬───────────────────────┤
│            │            │                       │
│ Teammate A │ Teammate B │ Teammate C            │
│ (frontend) │ (backend)  │ (tests)               │
│            │            │                       │
│ Own context│ Own context│ Own context            │
│ Own tools  │ Own tools  │ Own tools              │
└────────────┴────────────┴───────────────────────┘
         │            │            │
         └────────────┴────────────┘
             Shared Task List
          Direct Messaging Between
               All Members
```

### Key Concepts

- **Lead**: The session that creates the team. Acts as coordinator.
- **Teammates**: Independent Claude Code sessions spawned by the lead.
- **Shared task list**: All agents see task status and can claim available work. Toggle with `Ctrl+T`.
- **Direct messaging**: Teammates can message each other, not just the lead.
- **Idle notifications**: When a teammate finishes, it automatically notifies the lead.

### Files Created

| Path | Purpose |
|---|---|
| `~/.claude/teams/{team-name}/config.json` | Team configuration and members |
| `~/.claude/tasks/{team-name}/` | Shared task list |

---

## 4. Step-by-Step: Your First Subagent

### Step 1: Create the Agent File

```powershell
New-Item -ItemType Directory -Force ".claude\agents"
```

Create `.claude/agents/researcher.md`:

```markdown
---
name: researcher
description: Deep codebase researcher. Use when you need comprehensive
  understanding of a module, pattern, or feature.
tools: Read, Grep, Glob
model: haiku
---

When researching:
1. Use Glob to find relevant files
2. Use Grep to search for patterns and references
3. Read key files thoroughly
4. Map dependencies and relationships
5. Report findings with specific file references
```

### Step 2: Start Claude Code

```powershell
cd C:\path\to\your\project
claude
```

### Step 3: Invoke the Subagent

**Automatic** (Claude detects from task + description):
```
Research how the authentication module works and map all its dependencies
```

**Explicit**:
```
Use the researcher subagent to analyze the payment processing module
```

### Step 4: View Results

The subagent runs, and its findings are reported back to your main session.

### Step 5: Verify with `/agents`

```
/agents
```

Lists all available subagents (built-in + custom).

---

## 5. Step-by-Step: Your First Agent Team

### Step 1: Enable Agent Teams (Experimental)

**Option A: Environment variable (session)**:

```powershell
$env:CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS = "1"
```

**Option B: Persistent (user-level)**:

```powershell
[System.Environment]::SetEnvironmentVariable('CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS', '1', 'User')
```

**Option C: In `settings.json`**:

Add to `%USERPROFILE%\.claude\settings.json` or `.claude/settings.json`:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

### Step 2: Choose a Display Mode

| Mode | How | Requirements |
|---|---|---|
| **In-process** (default) | All teammates in one terminal | None (works everywhere) |
| **Split panes** | Each teammate in its own pane | `tmux` (install via WSL or scoop) |

Set display mode:

```json
{
  "teammateMode": "in-process"
}
```

Or via CLI flag:

```powershell
claude --teammate-mode in-process
```

> [!NOTE]
> Split-pane mode requires `tmux` or iTerm2. On Windows, use **in-process mode** (default) or run via WSL for tmux support.

### Step 3: Start Claude Code and Request a Team

```powershell
claude
```

Then prompt:

```
Create an agent team to build a REST API for user management.
Spawn 3 teammates:
- One for the API routes and controllers
- One for the database models and migrations
- One for the test suite

Use Sonnet for each teammate.
```

### Step 4: Monitor Your Team

**In-process mode controls**:

| Key | Action |
|---|---|
| `Shift+Up` / `Shift+Down` | Cycle through teammates |
| `Enter` | View a teammate's full session |
| `Escape` | Interrupt a teammate's current turn |
| `Ctrl+T` | Toggle the shared task list |
| Type while teammate selected | Send them a direct message |

### Step 5: Interact with Teammates

**Message a specific teammate**:
```
Tell the API teammate to add rate limiting to all endpoints
```

**Broadcast to all teammates**:
```
Broadcast: We're using PostgreSQL, not SQLite. Update your implementations.
```

**Assign a task**:
```
Assign the "write integration tests" task to the testing teammate
```

### Step 6: Wait for Completion

```
Wait for your teammates to complete their tasks before proceeding
```

### Step 7: Clean Up

```
Clean up the team
```

This shuts down all teammates and removes the team configuration.

---

## 6. Delegate Mode

Delegate mode restricts the **lead** to coordination-only. The lead acts as a **project manager** — assigning tasks, reviewing plans, and approving work — but cannot write code directly.

### Enable Delegate Mode

**Toggle with keyboard**: Press `Shift+Tab` during a session.

**Via prompt**:
```
Switch to delegate mode
```

### How It Works

```
┌─────────────────────────────┐
│        LEAD (Delegate)      │
│  ✅ Assign tasks            │
│  ✅ Review plans            │
│  ✅ Approve/reject work     │
│  ✅ Send messages           │
│  ❌ Write code directly     │
│  ❌ Run tools directly      │
└──────────┬──────────────────┘
           │ delegates to
    ┌──────┴──────┐
    │ Teammates   │
    │ (do the     │
    │  actual     │
    │  work)      │
    └─────────────┘
```

### When to Use

- Large projects where you want oversight without the lead doing work itself
- When you want to ensure clear task ownership
- Reviews and approvals before merging work

### Require Plan Approval

```
Spawn an architect teammate to refactor the authentication module.
Require plan approval before they make any changes.
```

The teammate will present a plan and wait for you to approve before proceeding.

---

## 7. Communication & Task Management

### Communication Between Agents

| Method | Scope | Notes |
|---|---|---|
| **Message** | One specific teammate | Direct, targeted |
| **Broadcast** | All teammates | Use sparingly — costs scale with team size |
| **Task list** | All agents | Shared view of task status |
| **Idle notification** | Auto → Lead | Teammate notifies lead when finished |

### Task Assignment Strategies

| Strategy | How It Works |
|---|---|
| **Lead assigns** | Tell the lead which task to give to which teammate |
| **Self-claim** | Teammates auto-pick the next unassigned, unblocked task |
| **Hybrid** | Lead assigns critical tasks, teammates self-claim the rest |

### Keyboard Shortcuts (In-Process Mode)

| Shortcut | Action |
|---|---|
| `Shift+Up/Down` | Select teammate |
| `Enter` | View teammate session |
| `Escape` | Interrupt teammate |
| `Ctrl+T` | Toggle task list |
| `Ctrl+B` | Background current task |
| `Shift+Tab` | Toggle delegate mode |

---

## 8. Quality Gates with Hooks

Agent teams support specialized hooks for quality control:

### TeammateIdle Hook

Runs when a teammate is about to go idle. Exit code `2` sends feedback and keeps them working.

```json
{
  "hooks": {
    "TeammateIdle": [
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/check-idle.sh"
          }
        ]
      }
    ]
  }
}
```

### TaskCompleted Hook

Runs when a task is marked complete. Exit code `2` prevents completion and sends feedback.

```json
{
  "hooks": {
    "TaskCompleted": [
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/verify-task.sh"
          }
        ]
      }
    ]
  }
}
```

### Example: Verify Tests Pass Before Task Completion

`.claude/hooks/verify-task.sh`:

```bash
#!/bin/bash
# Run tests to verify task quality
cd "$CLAUDE_PROJECT_DIR"
npm test 2>&1
if [ $? -ne 0 ]; then
  echo "Tests are failing. Please fix before marking task complete."
  exit 2  # Exit code 2 = send feedback, keep working
fi
exit 0  # Exit code 0 = allow completion
```

---

## 9. Use Case Examples

### 9.1 Parallel Code Review

```
Create an agent team to review PR #142. Spawn three reviewers:
- One focused on security implications
- One checking performance impact
- One validating test coverage
Have them each review and report findings.
```

### 9.2 Competing Debugging Hypotheses

```
Users report the app exits after one message instead of staying connected.
Spawn 5 agent teammates to investigate different hypotheses.
Have them talk to each other to try to disprove each other's theories,
like a scientific debate.
Update the findings doc with whatever consensus emerges.
```

### 9.3 Full-Stack Feature Development

```
Create an agent team to implement the user settings page:
- Teammate 1: Build the React frontend components
- Teammate 2: Implement the API endpoints and database models
- Teammate 3: Write end-to-end tests
- Teammate 4: Update documentation

Assign each teammate their module. They should not modify each other's files.
Wait for all teammates to complete before merging.
```

### 9.4 Research Phase → Implementation Phase

```
Phase 1: Create a research team (3 teammates) to each investigate:
- Teammate A: How the current auth module works
- Teammate B: What OAuth2 libraries are available on npm
- Teammate C: How our competitors implement OAuth login

Have them share findings through messages.

Phase 2: After research, clean up the research team. Then create an
implementation team based on the research findings.
```

### 9.5 Isolate Test Execution (Subagent)

```
Use a subagent to run the full test suite in the background.
Report only the failing tests with their error messages.
```

### 9.6 Sequential Pipeline (Subagent Chain)

```
Use the code-reviewer subagent to find issues in the auth module.
Then use the debugger subagent to fix the critical issues found.
Finally use the test-runner to verify the fixes pass.
```

---

## 10. Best Practices

### Give teammates enough context

Each teammate starts with a fresh context window. Include all relevant context in their spawn prompt — file paths, architecture decisions, constraints.

```
# ❌ Too vague
Spawn a teammate to fix the auth bug.

# ✅ Specific and contextual
Spawn a security reviewer teammate with the prompt:
"Review the authentication module at src/auth/ for security vulnerabilities.
Focus on token handling, session management, and input validation.
The app uses JWT tokens stored in httpOnly cookies.
Report any issues with severity ratings."
```

### Size tasks appropriately

| Size | Result |
|---|---|
| ❌ Too small | Coordination overhead exceeds the benefit |
| ❌ Too large | Teammates work too long without check-ins |
| ✅ Just right | Self-contained units with clear deliverables (a function, a test file, a review) |

### Avoid file conflicts

Assign **different files** to different teammates. If two teammates edit the same file, you'll get merge conflicts.

```
# ✅ Good: clear ownership
Teammate A owns: src/api/routes.ts, src/api/middleware.ts
Teammate B owns: src/models/user.ts, src/models/session.ts
Teammate C owns: tests/api.test.ts, tests/models.test.ts

# ❌ Bad: overlapping files
Both Teammate A and B editing src/index.ts
```

### Start with research, then implement

Use the first phase for research and review (read-only). Only move to implementation after understanding the codebase.

### Wait for teammates to finish

Explicitly tell the lead to wait:

```
Wait for your teammates to complete their tasks before proceeding
```

### Monitor and steer

Check in on teammates periodically. If one is stuck or going in the wrong direction, message them directly with course corrections.

---

## 11. Troubleshooting

### Subagent Issues

| Problem | Solution |
|---|---|
| Subagent not triggering | Make `description` more specific about when to use |
| Subagent triggers too often | Add `disable-model-invocation: true` |
| MCP tools not available | MCP only works in **foreground** mode |
| Background task denied | Pre-approve permissions in `settings.json` |

### Agent Team Issues

| Problem | Solution |
|---|---|
| **Teammates not appearing** | Press `Shift+Down` to cycle. Check if task warranted a team. |
| **Too many permission prompts** | Configure broader permissions in `settings.json` |
| **Teammates stopping on errors** | Message them with instructions, or spawn replacements |
| **Lead shuts down early** | Explicitly tell lead to wait for teammates to finish |
| **Task status appears stuck** | Check if work is done; manually update or nudge teammate |
| **Orphaned tmux sessions** | Run `tmux ls` and `tmux kill-session -t <name>` to clean up |

### Windows-Specific Notes

- **In-process mode** works in all terminals (recommended for Windows)
- **Split-pane mode** requires `tmux` — use WSL or install via `scoop install tmux`
- Split-pane mode is **not supported** in: VS Code integrated terminal, Windows Terminal, Ghostty

---

## 12. Current Limitations

> [!WARNING]
> Agent Teams is **experimental**. Enable with `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`.

| Limitation | Details |
|---|---|
| No session resumption | `/resume` and `/rewind` don't restore in-process teammates |
| Task status can lag | Teammates may forget to mark tasks complete; nudge manually |
| Slow shutdown | Teammates finish current operation before stopping |
| One team per session | Clean up current team before starting a new one |
| No nested teams | Teammates cannot spawn their own teams |
| Lead is fixed | Cannot promote teammate to lead or transfer leadership |
| Permissions set at spawn | All teammates start with lead's permission mode |
| Split panes need tmux/iTerm2 | Use in-process mode on Windows |

---

## Quick Reference

### Subagent Commands

```
/agents                    # List and manage subagents
/statusline                # Show active subagent status
```

### Agent Team Prompts

```
Create an agent team...     # Start a team
Clean up the team           # Shut down all teammates
Wait for teammates...       # Block until teammates finish
Broadcast: <message>        # Message all teammates
```

### Agent Team Keyboard Shortcuts

| Key | Action |
|---|---|
| `Shift+Up/Down` | Select teammate |
| `Enter` | View teammate session |
| `Escape` | Interrupt teammate |
| `Ctrl+T` | Toggle task list |
| `Ctrl+B` | Background task |
| `Shift+Tab` | Toggle delegate mode |

### Related Guides

| Guide | Link |
|---|---|
| Subagent deep dive | [subagents-guide.md](./subagents-guide.md) |
| Skills system | [skills-guide.md](./skills-guide.md) |
| MCP configuration | [mcp-setup-guide.md](./mcp-setup-guide.md) |
| Main setup guide | [README.md](./README.md) |
