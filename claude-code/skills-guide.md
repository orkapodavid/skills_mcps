# Skills System — Claude Code

Detailed guide for creating, configuring, and sharing skills that extend Claude's capabilities.

> **Docs**: [docs.anthropic.com/.../skills](https://docs.anthropic.com/en/docs/claude-code/skills)

---

## What Are Skills?

Skills are **reusable instruction packages** stored as `SKILL.md` files. They can:

- Define workflows triggered by `/slash-commands`
- Inject conventions Claude follows automatically
- Execute as isolated subagent tasks
- Include templates, examples, and helper scripts

---

## Where Skills Live

| Scope | Path | Discovery |
|---|---|---|
| **User** | `%USERPROFILE%\.claude\skills\<name>\SKILL.md` | All projects |
| **Project** | `.claude\skills\<name>\SKILL.md` | Current project, git-tracked |
| **Nested** | `packages\frontend\.claude\skills\<name>\SKILL.md` | Auto-discovered from subdirs |
| **Plugin** | `<plugin>\skills\<name>\SKILL.md` | Via installed plugin |

> [!TIP]
> Claude auto-discovers skills in `.claude/skills/` directories, including nested subdirectories.

### Loading Skills from Additional Directories

Use `--add-dir` to include skills from external directories:

```powershell
claude --add-dir C:\Users\orkap\Desktop\Programming\skills_mcps\claude-skills
```

Or set the env var for CLAUDE.md discovery from additional dirs:

```powershell
$env:CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD = "1"
```

---

## Creating Your First Skill

### Step 1: Create the Directory

```powershell
# User-level skill (available everywhere)
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\skills\explain-code"

# OR project-level skill (shared with team)
New-Item -ItemType Directory -Force ".claude\skills\explain-code"
```

### Step 2: Write SKILL.md

```markdown
---
name: explain-code
description: Explains code with visual diagrams and analogies. Use when
  explaining how code works, teaching about a codebase, or when the user
  asks "how does this work?"
---

When explaining code, always include:

1. **Start with an analogy**: Compare the code to something from everyday life
2. **Draw a diagram**: Use ASCII art to show the flow or relationships
3. **Walk through the code**: Explain step-by-step what happens
4. **Highlight a gotcha**: What's a common mistake or misconception?

Keep explanations conversational.
```

### Step 3: Test It

In a Claude Code session:

```
How does this code work?
```

Or use the slash command directly:

```
/explain-code src/auth/login.py
```

---

## SKILL.md Format

### Frontmatter Reference

```yaml
---
name: skill-name                    # Required. Also the /slash-command name
description: What this skill does   # Required. Claude reads this for auto-invocation
argument-hint: "[filename] [format]" # Optional. Hint for slash command args
disable-model-invocation: true      # Optional. Only invoked via /name, never auto
user-invocable: false               # Optional. Hide from / menu
allowed-tools: Read, Grep, Bash     # Optional. Restrict tool access
model: sonnet                       # Optional. Override model
context: fork                       # Optional. Run in isolated subagent
agent: Explore                      # Optional. Specify subagent type for fork
hooks:                              # Optional. Lifecycle hooks
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/check.sh"
---
```

### Body Content Types

**1. Convention / Guidelines** — Claude follows these automatically:

```markdown
---
name: api-conventions
description: API design patterns for this codebase
---

When writing API endpoints:
- Use RESTful naming conventions
- Return consistent error formats
- Include request validation
```

**2. Slash Command Workflow** — triggered by `/name`:

```markdown
---
name: deploy
description: Deploy the application to production
context: fork
disable-model-invocation: true
---

Deploy the application:
1. Run the test suite: `uv run pytest`
2. Build the application: `uv run build`
3. Push to the deployment target
```

**3. Template-Based** — Claude fills in a template:

```markdown
---
name: create-component
description: Generate a new React component
argument-hint: "[ComponentName]"
---

Create a new component named $ARGUMENTS using this template:

See [template.tsx](template.tsx) for the component structure.
See [examples/](examples/) for reference implementations.
```

---

## Skill Directory Structure

```
my-skill/
├── SKILL.md              # Main instructions (required)
├── reference.md          # Detailed API docs (loaded when needed)
├── template.md           # Template for Claude to fill in
├── examples/
│   └── sample.md         # Example output
└── scripts/
    └── helper.py         # Script Claude can execute
```

> [!IMPORTANT]
> Only `SKILL.md` is auto-loaded. Supporting files are loaded on-demand when
> Claude follows the links in SKILL.md. Reference them with relative links:
> `See [reference.md](reference.md) for details.`

---

## String Substitutions

Use these variables in SKILL.md body:

| Variable | Value |
|---|---|
| `$ARGUMENTS` | Full argument string from `/skill-name args here` |
| `$ARGUMENTS[0]`, `$0` | First argument |
| `$ARGUMENTS[1]`, `$1` | Second argument |
| `${CLAUDE_SESSION_ID}` | Current session ID |

### Example

```markdown
---
name: fix-issue
description: Fix a GitHub issue
argument-hint: "[issue-number]"
---

Fix GitHub issue #$ARGUMENTS:
1. Read the issue details
2. Identify affected code
3. Implement the fix
4. Write tests
5. Create a commit referencing #$ARGUMENTS
```

---

## Dynamic Context Injection

Prefix a command with `!` to execute it before Claude sees the prompt:

```markdown
---
name: pr-summary
description: Summarize changes in a pull request
context: fork
agent: Explore
allowed-tools: Bash(gh *)
---

## Pull Request Context
- PR diff: !`gh pr diff`
- PR comments: !`gh pr view --comments`
- Changed files: !`gh pr diff --name-only`

## Your Task
Summarize this pull request concisely.
```

The `!` commands execute immediately, and their output replaces the placeholder before Claude starts.

---

## Running Skills in Subagents

Add `context: fork` to run a skill in an isolated subagent:

```markdown
---
name: deep-research
description: Research a topic thoroughly
context: fork
agent: Explore
---

Research $ARGUMENTS thoroughly:
1. Find relevant files using Glob and Grep
2. Read and analyze the code
3. Summarize findings with specific file references
```

- `context: fork` — creates an isolated context
- `agent` — the execution environment (`Explore`, `Plan`, `general-purpose`, or a custom agent name)

### Preloading Skills into Subagents

From a subagent's frontmatter:

```markdown
---
name: api-developer
description: Implement API endpoints
skills:
  - api-conventions
  - error-handling-patterns
---
```

---

## Restricting Skill Access

### Limit tool access within a skill

```yaml
allowed-tools: Read, Grep, Bash(npm run *)
```

### Prevent auto-invocation (slash-command only)

```yaml
disable-model-invocation: true
```

### Hide from slash-command menu

```yaml
user-invocable: false
```

### Deny specific skills via permissions

In `settings.json`:

```json
{
  "permissions": {
    "deny": ["Skill(deploy *)"]
  }
}
```

---

## Practical Skill Examples

### Git Commit with Conventional Format

**File**: `.claude/skills/commit/SKILL.md`

```markdown
---
name: commit
description: Create a conventional commit with staged changes
context: fork
disable-model-invocation: true
---

Create a git commit:
1. Run `git diff --staged` to see changes
2. Analyze the changes
3. Write a conventional commit message:
   - Format: `type(scope): description`
   - Types: feat, fix, refactor, docs, test, chore
4. Run `git commit -m "message"`
```

### Code Documentation Generator

**File**: `.claude/skills/document/SKILL.md`

```markdown
---
name: document
description: Generate documentation for a file or module
argument-hint: "[filepath]"
---

Generate comprehensive documentation for `$ARGUMENTS`:
1. Read the file
2. Identify all public classes, functions, and constants
3. Write docstrings following Google style
4. Add type hints if missing
5. Create a summary at the top of the file
```

### Test Writer

**File**: `.claude/skills/write-tests/SKILL.md`

```markdown
---
name: write-tests
description: Write comprehensive tests for a module
argument-hint: "[filepath]"
allowed-tools: Read, Write, Bash, Grep
---

Write tests for `$ARGUMENTS`:
1. Read the source file
2. Identify all testable functions and edge cases
3. Create test file at `tests/test_<basename>.py`
4. Use pytest with:
   - Fixtures for setup/teardown
   - Parametrize for multiple inputs
   - Mock external dependencies
5. Run `uv run pytest tests/test_<basename>.py -v` to verify
```

### Database Migration Creator

**File**: `.claude/skills/create-migration/SKILL.md`

```markdown
---
name: create-migration
description: Create an Alembic database migration
argument-hint: "[description]"
context: fork
disable-model-invocation: true
---

Create a new Alembic migration for: $ARGUMENTS

1. Review current models in `app/models/`
2. Run `uv run alembic revision --autogenerate -m "$ARGUMENTS"`
3. Review the generated migration file
4. Verify upgrade and downgrade functions are correct
5. Run `uv run alembic upgrade head` to test
```

---

## Troubleshooting

### Skill Not Triggering

- Verify `description` clearly states **when** to use the skill
- Check that the skill is in a valid location
- Run `/compact` to free up context window space
- Try explicit invocation: `/skill-name`

### Skill Triggers Too Often

- Add `disable-model-invocation: true` to limit to slash commands only
- Make the `description` more specific about trigger conditions
- Add `user-invocable: false` to hide it completely from auto-discovery

### Claude Doesn't See All Skills

- Skills are loaded lazily; only summaries are in context initially
- Claude Code limits how many skills it loads at once
- Use more descriptive `description` fields so Claude picks the right one
