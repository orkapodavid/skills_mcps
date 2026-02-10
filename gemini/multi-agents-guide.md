# Gemini CLI — Multi-Agent & Orchestration Guide

Detailed guide for setting up multi-agent workflows in Gemini CLI, including master-worker orchestration, the Maestro extension, and custom agent architectures.

> **Main guide**: [README.md](./README.md) · **Skills guide**: [skills-guide.md](./skills-guide.md)
> **Official reference**: [Extensions](https://geminicli.com/docs/extensions) · [Custom Commands](https://geminicli.com/docs/cli/custom-commands)

---

## Table of Contents

1. [Overview](#1-overview)
2. [Multi-Agent Architecture Patterns](#2-multi-agent-architecture-patterns)
3. [Building a Custom Agent System](#3-building-a-custom-agent-system)
4. [The Maestro Extension](#4-the-maestro-extension)
5. [Filesystem-as-State Pattern](#5-filesystem-as-state-pattern)
6. [Agent Development Kit (ADK)](#6-agent-development-kit-adk)
7. [Comparison with Claude Code](#7-comparison-with-claude-code)
8. [Templates & Examples](#8-templates--examples)

---

## 1. Overview

Gemini CLI supports multi-agent workflows through a combination of custom commands, extensions, and orchestration patterns. Unlike Claude Code's built-in subagent system, Gemini CLI achieves multi-agent behavior through:

1. **Custom commands** that launch specialized `gemini` instances
2. **Extensions** that bundle orchestration logic (e.g., Maestro)
3. **Filesystem-as-state** for coordination between agents
4. **MCP servers** for external tool delegation

```
┌──────────────────────────────────┐
│         Orchestrator             │
│     (Master/Coordinator)         │
│  ┌───────────────────────────┐   │
│  │  Custom Command / GEMINI.md│  │
│  └───────────┬───────────────┘   │
│              │                   │
│   ┌──────────┼──────────┐       │
│   ▼          ▼          ▼       │
│ ┌─────┐ ┌──────┐ ┌─────────┐   │
│ │Coder│ │Review│ │Debugger │   │
│ └──┬──┘ └──┬───┘ └────┬────┘   │
│    │       │          │         │
│    ▼       ▼          ▼         │
│   Filesystem / Task Queue        │
└──────────────────────────────────┘
```

---

## 2. Multi-Agent Architecture Patterns

### Pattern 1: Orchestrator-Workers (Master-Worker)

A central orchestrator breaks tasks into subtasks and delegates to specialized workers:

```
Orchestrator (Master)
├── Analyzes complex request
├── Decomposes into subtasks
├── Assigns workers
│
├── Worker A (Architecture) ──► Output A
├── Worker B (Coding)       ──► Output B
├── Worker C (Testing)      ──► Output C
│
└── Synthesizer combines outputs ──► Final Result
```

**Key characteristics:**
- Dynamic task decomposition
- Specialized expertise per worker
- Parallel execution of independent subtasks
- Central synthesis of results

### Pattern 2: Pipeline (Sequential)

Agents process tasks in a fixed order:

```
Input ──► Agent A (Plan) ──► Agent B (Code) ──► Agent C (Review) ──► Output
```

**Best for:** Well-defined workflows with clear phase dependencies.

### Pattern 3: Supervisor-Hierarchy

A top-level supervisor delegates to mid-level coordinators, who manage workers:

```
Supervisor
├── Frontend Coordinator
│   ├── UI Agent
│   └── Styling Agent
└── Backend Coordinator
    ├── API Agent
    └── Database Agent
```

**Best for:** Large projects with distinct subsystems.

### Pattern 4: Peer-to-Peer

Agents communicate through shared state without a central coordinator:

```
Agent A ──► Filesystem ◄── Agent B
               ▲
               │
           Agent C
```

**Best for:** Loosely coupled tasks, concurrent independent work.

---

## 3. Building a Custom Agent System

### Step 1: Create the Agent Extension

```
my-agent-team/
├── gemini-extension.json
├── GEMINI.md                    # Master orchestrator context
├── commands/
│   ├── orchestrate.toml         # Main orchestration command
│   ├── agents/
│   │   ├── architect.toml       # Architecture agent
│   │   ├── coder.toml           # Coding agent
│   │   ├── reviewer.toml        # Review agent
│   │   └── debugger.toml        # Debug agent
│   └── workflow/
│       ├── plan.toml            # Planning phase
│       ├── implement.toml       # Implementation phase
│       └── verify.toml          # Verification phase
├── skills/
│   └── code-standards/
│       └── SKILL.md
└── .gemini-tasks/               # Filesystem-as-state directory
    ├── plan.md
    ├── tasks/
    └── logs/
```

### Step 2: Define the Master Orchestrator

**`GEMINI.md`** (Master context):

```markdown
# Multi-Agent Orchestrator

You are the master orchestrator for a multi-agent development team.

## Your Agents
- **Architect** (`/agents:architect`): System design and architecture decisions
- **Coder** (`/agents:coder`): Feature implementation following clean code principles
- **Reviewer** (`/agents:reviewer`): Code review with security and quality focus
- **Debugger** (`/agents:debugger`): Root cause analysis and bug fixing

## Workflow
1. Analyze the user's request
2. Break it into subtasks
3. Write task assignments to `.gemini-tasks/tasks/`
4. Delegate to appropriate agents via commands
5. Synthesize results from `.gemini-tasks/logs/`
6. Present final output to the user

## Coordination Rules
- Always plan before coding
- Review after every implementation
- Log all decisions to `.gemini-tasks/logs/`
- Use `.gemini-tasks/plan.md` for the current plan
```

### Step 3: Define Worker Agents

**`commands/agents/architect.toml`**:

```toml
description = "Architecture agent — designs system structure and interfaces"
prompt = """
You are the Architecture Agent. Your role is system design.

## Current Task
Read the task from `.gemini-tasks/tasks/` and design the solution.

## Instructions
1. Read the project structure
2. Analyze existing patterns
3. Design the architecture for: {{args}}
4. Write your design to `.gemini-tasks/logs/architecture-output.md`

## Constraints
- Follow existing patterns in the codebase
- Prefer composition over inheritance
- Document all interface contracts
"""
```

**`commands/agents/coder.toml`**:

```toml
description = "Coding agent — implements features following architecture designs"
prompt = """
You are the Coding Agent. Your role is implementation.

## Architecture Input
Read the architecture design from `.gemini-tasks/logs/architecture-output.md`

## Instructions
1. Follow the architecture design exactly
2. Implement: {{args}}
3. Write clean, well-documented code
4. Add inline comments for complex logic
5. Log your changes to `.gemini-tasks/logs/coding-output.md`

## Standards
- Follow SOLID principles
- Add type hints to all functions
- Keep functions under 30 lines
"""
```

**`commands/agents/reviewer.toml`**:

```toml
description = "Review agent — code quality, security, and best practices"
prompt = """
You are the Code Review Agent.

## Review Target
!{git diff HEAD~1}

## Instructions
1. Review all changes for quality and security
2. Check against the project's coding standards
3. Look for:
   - Security vulnerabilities
   - Performance issues
   - Missing tests
   - Documentation gaps
4. Write review findings to `.gemini-tasks/logs/review-output.md`

## Output Format
Rate each finding: CRITICAL / WARNING / SUGGESTION
"""
```

**`commands/agents/debugger.toml`**:

```toml
description = "Debug agent — root cause analysis and bug fixing"
prompt = """
You are the Debug Agent. Your role is root cause analysis.

## Bug Report
{{args}}

## Debugging Process
1. Reproduce the issue mentally from the description
2. Trace the code path that could cause this behavior
3. Identify the root cause
4. Propose a fix with minimal code changes
5. Write analysis to `.gemini-tasks/logs/debug-output.md`

## Techniques
- Check recent changes: `!{git log --oneline -10}`
- Search for related code patterns
- Analyze error logs and stack traces
"""
```

### Step 4: Create Workflow Commands

**`commands/workflow/plan.toml`**:

```toml
description = "Planning phase — analyze requirements and create a task plan"
prompt = """
## Planning Phase

Analyze the following requirement: {{args}}

1. Break it into discrete, actionable subtasks
2. Identify dependencies between subtasks
3. Assign each subtask to an agent (architect, coder, reviewer, debugger)
4. Estimate complexity (low/medium/high)

Write the plan to `.gemini-tasks/plan.md` in this format:

```markdown
# Task Plan: [Title]

## Subtasks
- [ ] [Task 1] — Agent: architect — Complexity: medium
- [ ] [Task 2] — Agent: coder — Depends on: Task 1
- [ ] [Task 3] — Agent: reviewer — Depends on: Task 2
```
"""
```

### Step 5: The Orchestration Command

**`commands/orchestrate.toml`**:

```toml
description = "Run a full multi-agent workflow for a complex task"
prompt = """
You are the Master Orchestrator. Execute the following workflow:

## User Request
{{args}}

## Execution Steps
1. **Plan**: Use `/workflow:plan` to create a task plan
2. **Design**: Use `/agents:architect` for architecture decisions
3. **Implement**: Use `/agents:coder` for each coding subtask
4. **Review**: Use `/agents:reviewer` to validate changes
5. **Fix**: If review finds issues, use `/agents:debugger`

## Coordination
- Read task status from `.gemini-tasks/plan.md`
- Mark completed tasks with [x]
- Log all outputs to `.gemini-tasks/logs/`
- Synthesize final results for the user

## Output
Provide a summary of:
- What was accomplished
- Files changed
- Any remaining issues or TODOs
"""
```

---

## 4. The Maestro Extension

**Maestro** is a popular community extension that adds structured multi-agent workflows to Gemini CLI.

### Installation

```powershell
gemini extensions install https://github.com/gemini-cli-extensions/maestro
```

### Architecture

Maestro coordinates **12 specialized subagents** through explicit phases:

| Subagent | Specialty |
|---|---|
| **Model Architect** | System design, interfaces, data models |
| **Coder** | Feature implementation, clean code, SOLID |
| **Debugger** | Root cause analysis, log analysis, execution tracing |
| **Security** | Vulnerability scanning, threat modeling |
| **Performance** | Profiling, optimization, benchmarking |
| **Tester** | Test generation, coverage analysis |
| **Documenter** | API docs, user guides, changelogs |
| **Reviewer** | Code quality, best practices |
| **DevOps** | CI/CD, deployment, infrastructure |
| **Refactorer** | Code cleanup, pattern application |
| **DBA** | Database design, query optimization |
| **Frontend** | UI/UX, component design, accessibility |

### How Maestro Works

```
1. Task Input
      │
      ▼
2. Design Phase ──► Architect subagent
      │
      ▼
3. Planning Phase ──► Orchestrator breaks into subtasks
      │
      ▼
4. Team Assembly ──► Selects relevant subagents
      │
      ▼
5. Execution Phase ──► Parallel/sequential subtask execution
      │
      ▼
6. Synthesis ──► Combine outputs, review quality
      │
      ▼
7. Final Output
```

### Key Features

- **Phased execution**: Design → Plan → Execute → Review
- **State persistence**: All session state saved as YAML/Markdown on disk
- **Resumable sessions**: Pick up where you left off
- **Auditable**: Full log trail of all agent decisions
- **Team assembly**: Dynamically selects agents based on task requirements

---

## 5. Filesystem-as-State Pattern

A core architectural philosophy for multi-agent Gemini CLI workflows uses the **filesystem as the state management layer**.

### Directory Structure

```
.gemini-tasks/
├── plan.md                 # Current task plan with checklist
├── config.yaml             # Workflow configuration
├── queue/                  # Task queue
│   ├── 001-design.md       # Pending task
│   ├── 002-implement.md    # Pending task
│   └── 003-review.md       # Pending task
├── active/                 # Currently running tasks
│   └── 002-implement.md    # Moved here when started
├── done/                   # Completed tasks
│   └── 001-design.md       # Moved here when finished
└── logs/                   # Agent outputs
    ├── architect-output.md
    ├── coder-output.md
    └── review-output.md
```

### How It Works

1. **Orchestrator** reads `queue/` for pending tasks
2. Moves a task to `active/` and spawns a worker agent
3. Worker reads task file, performs work, writes output to `logs/`
4. Orchestrator moves task from `active/` to `done/`
5. Repeat until `queue/` is empty

### Benefits

| Benefit | Description |
|---|---|
| **Stateless agents** | Each agent is a fresh instance, no shared memory |
| **Resumable** | If interrupted, restart by checking `active/` and `queue/` |
| **Auditable** | Complete history in `done/` and `logs/` |
| **Debuggable** | Inspect any agent's output in `logs/` |
| **Parallel-safe** | Multiple agents can work on independent tasks |

---

## 6. Agent Development Kit (ADK)

For production-grade multi-agent systems, Google's **Agent Development Kit (ADK)** provides a Python framework:

### Key Features

- Hierarchical agent composition
- Dynamic orchestration (sequential, parallel, loop)
- Coordinator/dispatcher patterns
- Integration with Google Cloud and Gemini models
- Built-in state management

### ADK vs Gemini CLI Agents

| Feature | Gemini CLI Agents | ADK |
|---|---|---|
| **Language** | TOML/Markdown prompts | Python code |
| **Complexity** | Simple to moderate | Production-grade |
| **State** | Filesystem-based | Programmatic |
| **Deployment** | Local terminal | Cloud-deployable |
| **Orchestration** | Custom commands/extensions | Built-in patterns |
| **Best for** | Developer workflows | Enterprise applications |

> [!TIP]
> Use Gemini CLI agents for personal/team development workflows. Use ADK when building production multi-agent applications.

---

## 7. Comparison with Claude Code

| Feature | Gemini CLI | Claude Code |
|---|---|---|
| **Built-in subagents** | None (extension-based) | Explore, Plan, General-purpose |
| **Custom agents** | Custom Commands + Extensions | `.claude/agents/*.md` files |
| **Agent definition** | TOML commands + GEMINI.md | Markdown with YAML frontmatter |
| **Orchestration** | Maestro extension / custom | Built-in task delegation |
| **Background agents** | Not built-in | `Ctrl+B` to background |
| **Foreground/background** | Single instance | Foreground + concurrent background |
| **Agent permissions** | Extension-level | Per-agent `permissionMode` field |
| **Agent tools** | All tools (global) | Per-agent `tools` field |
| **Agent model** | Extension/session model | Per-agent `model` field |
| **Agent memory** | GEMINI.md / filesystem | `memory: user\|project\|local` |
| **Multi-agent pattern** | Filesystem-as-state | Native `Task()` tool delegation |
| **State management** | Filesystem (YAML/MD) | In-memory session state |
| **Session resume** | Checkpointing + filesystem | Session history |

### Architecture Comparison

```
Claude Code Multi-Agent:                    Gemini CLI Multi-Agent:
┌────────────────────┐                     ┌─────────────────────┐
│   Main Claude      │                     │  Gemini Orchestrator│
│   (orchestrates)   │                     │  (GEMINI.md)        │
│                    │                     │                     │
│  Task(worker) ─────┤                     │  /agents:coder ─────┤
│  Task(reviewer) ───┤                     │  /agents:reviewer ──┤
│  Task(explorer) ───┤                     │  /agents:debugger ──┤
│                    │                     │                     │
│  Built-in or       │                     │  Filesystem-as-State│
│  custom agents     │                     │  (.gemini-tasks/)   │
└────────────────────┘                     └─────────────────────┘
```

---

## 8. Templates & Examples

### Minimal Multi-Agent Setup

Create these files in your project:

#### 1. Orchestrator Context

```markdown
<!-- .gemini/GEMINI.md (add to existing) -->

## Agent Team
When the user asks for complex tasks, use these agents:
- `/agents:plan` — Break task into subtasks
- `/agents:code` — Implement changes
- `/agents:review` — Review code quality
```

#### 2. Planning Agent

```toml
# .gemini/commands/agents/plan.toml
description = "Plan a complex task by breaking it into subtasks"
prompt = """
Break this task into actionable subtasks: {{args}}

For each subtask, specify:
1. Description
2. Files to modify
3. Dependencies on other subtasks
4. Estimated complexity (low/medium/high)
"""
```

#### 3. Coding Agent

```toml
# .gemini/commands/agents/code.toml
description = "Implement a specific coding task"
prompt = """
Implement the following task: {{args}}

Rules:
- Follow existing code patterns
- Add type hints
- Write docstrings
- Keep changes minimal and focused
"""
```

#### 4. Review Agent

```toml
# .gemini/commands/agents/review.toml
description = "Review recent changes for quality"
prompt = """
Review recent changes:

```diff
!{git diff}
```

Check for:
- Correctness and logic errors
- Security issues
- Performance concerns
- Test coverage
- Documentation

Output: Findings by severity (Critical/Warning/Suggestion)
"""
```

### Usage

```
# Start a Gemini session
gemini

# Plan a feature
> /agents:plan Add user authentication with JWT tokens

# Implement
> /agents:code Implement JWT token generation and validation

# Review
> /agents:review

# Or orchestrate the full workflow
> /orchestrate Add user authentication with JWT tokens
```

---

## Quick Reference Links

| Resource | URL |
|---|---|
| Custom Commands | [geminicli.com/docs/cli/custom-commands](https://geminicli.com/docs/cli/custom-commands) |
| Agent Skills | [geminicli.com/docs/skills](https://geminicli.com/docs/skills) |
| Extensions Guide | [geminicli.com/docs/extensions](https://geminicli.com/docs/extensions) |
| Writing Extensions | [geminicli.com/docs/extensions/writing-extensions](https://geminicli.com/docs/extensions/writing-extensions) |
| Extensions Gallery | [geminicli.com/extensions/browse](https://geminicli.com/extensions/browse/) |
| Agent Development Kit | [google.github.io/adk-docs](https://google.github.io/adk-docs/) |
| GitHub CLI Action | [github.com/google-github-actions/run-gemini-cli](https://github.com/google-github-actions/run-gemini-cli) |
