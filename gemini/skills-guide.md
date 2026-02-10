# Gemini CLI — Skills & Custom Commands Guide

Detailed guide for creating reusable agent skills and custom commands in Gemini CLI.

> **Main guide**: [README.md](./README.md)
> **Official reference**: [Custom Commands](https://geminicli.com/docs/cli/custom-commands) · [Agent Skills](https://geminicli.com/docs/skills)

---

## Table of Contents

1. [Overview](#1-overview)
2. [Custom Commands (TOML)](#2-custom-commands-toml)
3. [Agent Skills (SKILL.md)](#3-agent-skills-skillmd)
4. [Extensions — Bundling It All](#4-extensions--bundling-it-all)
5. [Comparison: Skills vs Commands vs Extensions](#5-comparison-skills-vs-commands-vs-extensions)
6. [Templates & Examples](#6-templates--examples)

---

## 1. Overview

Gemini CLI has three layers of customization for reusable agent behaviors:

| Layer | Format | Purpose | Invocation |
|---|---|---|---|
| **Custom Commands** | `.toml` files | Reusable prompt shortcuts | `/command-name` |
| **Agent Skills** | `SKILL.md` directories | Specialized expertise packages | Auto-activated or `/skills` |
| **Extensions** | `gemini-extension.json` bundle | Distributable packages of commands, skills, MCP servers | `gemini extensions install` |

---

## 2. Custom Commands (TOML)

Custom commands let you save frequently used prompts as `/slash-command` shortcuts.

### Directory Locations

| Scope | Path | Precedence |
|---|---|---|
| **Global** (all projects) | `~/.gemini/commands/` | Lower |
| **Project** (team-shared) | `.gemini/commands/` | Higher (overrides global) |

> [!TIP]
> Project commands override global commands with the same name, allowing project-specific versions.

### Naming & Namespacing

The command name is derived from the file path. Subdirectories create **namespaced** commands using `:` as a separator:

| File Path | Command |
|---|---|
| `~/.gemini/commands/test.toml` | `/test` |
| `.gemini/commands/git/commit.toml` | `/git:commit` |
| `.gemini/commands/db/migrate.toml` | `/db:migrate` |

### TOML File Format

```toml
# Required
prompt = "Your prompt text here"

# Optional
description = "Brief description shown in /help menu"
```

Multi-line prompts use triple-quoted strings:

```toml
description = "Review code in the current directory"
prompt = """
Review all modified files in this project.
Focus on:
1. Code quality and best practices
2. Security vulnerabilities
3. Performance issues

Provide a summary with severity ratings.
"""
```

### Handling Arguments — `{{args}}`

The `{{args}}` placeholder injects user-provided arguments:

```toml
# .gemini/commands/explain.toml
description = "Explain a concept in the codebase"
prompt = "Explain the following concept from this codebase: {{args}}"
```

**Usage:** `/explain dependency injection`

### Executing Shell Commands — `!{...}`

Embed live shell output into prompts:

```toml
# .gemini/commands/git/commit.toml
description = "Generate a commit message from staged changes"
prompt = """
Please generate a Conventional Commit message based on the following git diff:

```diff
!{git diff --staged}
```
"""
```

> [!IMPORTANT]
> Shell commands show a confirmation dialog before execution. Arguments inside `!{...}` are auto-escaped for security.

### Injecting File Content — `@{...}`

Embed file contents directly into prompts:

```toml
# .gemini/commands/review-config.toml
description = "Review the project configuration"
prompt = """
Review this configuration file and suggest improvements:

```
@{./config.yaml}
```
"""
```

### Combined Example — Full Workflow Command

```toml
# .gemini/commands/pr-review.toml
description = "Review a PR with full context"
prompt = """
You are a senior code reviewer. Review the following changes:

## Git Diff
```diff
!{git diff main...HEAD}
```

## Project Guidelines
@{./CONTRIBUTING.md}

## Instructions
- Focus on {{args}}
- Rate issues by severity: Critical, Warning, Suggestion
- Provide inline code suggestions for fixes
"""
```

**Usage:** `/pr-review security and performance`

---

## 3. Agent Skills (SKILL.md)

> [!NOTE]
> Agent Skills are an **experimental** feature. Enable via `experimental.skills` in settings or through the `/settings` interactive UI.

Skills are self-contained directories that package instructions, scripts, and assets into specialized AI capabilities.

### Directory Locations

| Scope | Path |
|---|---|
| **Workspace** (project-specific) | `.gemini/skills/` |
| **User** (personal, all projects) | `~/.gemini/skills/` |
| **Extension-bundled** | Inside an installed extension |

### Skill Directory Structure

```
my-skill/
├── SKILL.md           # Core instructions (required)
├── scripts/           # Executable scripts (optional)
│   ├── lint.sh
│   └── deploy.py
├── references/        # Static documentation (optional)
│   ├── api-spec.yaml
│   └── coding-standards.md
└── assets/            # Templates & resources (optional)
    ├── component-template.tsx
    └── config-boilerplate.json
```

### SKILL.md Format

```markdown
---
name: security-auditor
description: Performs security audits on code changes, identifying vulnerabilities and suggesting mitigations.
---

You are a security expert. When activated:

1. Scan all modified files for security vulnerabilities
2. Check for common issues:
   - SQL injection
   - XSS vulnerabilities
   - Hardcoded credentials
   - Insecure dependencies
3. Reference the OWASP Top 10 guidelines
4. Provide remediation suggestions with code examples

Use the scripts in `scripts/` for automated scanning.
Refer to `references/` for project-specific security policies.
```

### SKILL.md Frontmatter Fields

| Field | Required | Purpose |
|---|---|---|
| `name` | ✅ | Unique identifier for the skill |
| `description` | ✅ | Gemini uses this to decide when to activate the skill |

### How Skills Work

1. **Discovery**: Gemini CLI scans skill directories on startup
2. **Activation**: The model reads skill descriptions and activates relevant ones based on context
3. **Context**: When activated, Gemini receives a tree view of the entire skill directory
4. **Execution**: The model follows SKILL.md instructions and can use bundled scripts/references

### Managing Skills

| Command | Purpose |
|---|---|
| `/skills` | List, enable, disable, and reload skills |
| `/skills list` | Show all discovered skills |
| `/skills enable <name>` | Activate a specific skill |
| `/skills disable <name>` | Deactivate a specific skill |
| `/skills reload` | Reload skills from disk |

### Example Skills

#### Deploy Skill

```
deploy-app/
├── SKILL.md
├── scripts/
│   ├── pre-deploy-checks.sh
│   └── deploy.sh
└── references/
    └── deployment-guide.md
```

```markdown
---
name: deploy-app
description: Deploy the application to production with pre-flight checks and rollback capability.
---

Follow this deployment process:

1. Run pre-deployment checks: `scripts/pre-deploy-checks.sh`
2. Review the deployment guide in `references/deployment-guide.md`
3. Execute deployment: `scripts/deploy.sh`
4. Verify deployment health
5. If issues detected, initiate rollback
```

#### Code Review Skill

```
code-reviewer/
├── SKILL.md
├── references/
│   └── style-guide.md
└── assets/
    └── review-template.md
```

```markdown
---
name: code-reviewer
description: Expert code review with project-specific standards and structured feedback.
---

When reviewing code:

1. Read the style guide from `references/style-guide.md`
2. Use the template from `assets/review-template.md` for output format
3. Check for:
   - Code quality and readability
   - Security vulnerabilities
   - Performance issues
   - Test coverage
4. Rate each finding: Critical / Warning / Suggestion
```

---

## 4. Extensions — Bundling It All

Extensions package commands, skills, MCP servers, and context into distributable bundles.

### Extension Structure

```
my-extension/
├── gemini-extension.json    # Manifest (required)
├── GEMINI.md                # Extension-specific context
├── commands/                # Custom slash commands
│   ├── review.toml
│   └── deploy.toml
├── skills/                  # Agent skills
│   └── security-auditor/
│       └── SKILL.md
└── hooks/                   # Lifecycle hooks
    └── pre-commit.sh
```

### `gemini-extension.json` Manifest

```json
{
  "name": "my-dev-toolkit",
  "version": "1.0.0",
  "description": "Development toolkit with review, deploy, and security skills",
  "contextFileName": "GEMINI.md",
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  },
  "excludeTools": []
}
```

### Manifest Fields

| Field | Type | Purpose |
|---|---|---|
| `name` | string | Unique extension identifier |
| `version` | string | Semantic version |
| `description` | string | What the extension does |
| `contextFileName` | string | Context file to load (e.g., `GEMINI.md`) |
| `mcpServers` | object | MCP server configurations |
| `excludeTools` | string[] | Built-in tools to disable |

### Installing / Managing Extensions

```powershell
# Install from GitHub
gemini extensions install https://github.com/user/my-extension

# Install from local path
gemini extensions install --path=C:\path\to\my-extension

# List installed extensions
gemini extensions list

# In-session
/extensions list
```

### Notable Community Extensions

| Extension | Purpose |
|---|---|
| **Maestro** | Multi-agent orchestration with 12 specialized subagents |
| **agent-creator** | Generate custom agents via conversation |
| **workspace** | Enhanced workspace management |

> [!TIP]
> Browse the [Extensions Gallery](https://geminicli.com/extensions/browse/) for more community extensions.

---

## 5. Comparison: Skills vs Commands vs Extensions

| Feature | Custom Commands | Agent Skills | Extensions |
|---|---|---|---|
| **Format** | `.toml` file | `SKILL.md` directory | `gemini-extension.json` bundle |
| **Complexity** | Single prompt | Multi-file with scripts/assets | Full package |
| **Invocation** | `/command-name` | Auto-activated by context | Auto-loaded on install |
| **Arguments** | `{{args}}`, `!{...}`, `@{...}` | N/A (context-driven) | N/A |
| **Shareable** | Copy `.toml` file | Copy directory | `gemini extensions install` |
| **MCP support** | No | No | Yes |
| **Shell execution** | Yes (`!{...}`) | Yes (via scripts/) | Yes (via commands/skills) |
| **Experimental** | No (stable) | Yes | No (stable) |

### Comparison with Claude Code

| Feature | Gemini CLI | Claude Code |
|---|---|---|
| **Reusable prompts** | Custom Commands (`.toml`) | Skills (`SKILL.md`) |
| **Specialized agents** | Agent Skills + Extensions | Subagents (`.claude/agents/*.md`) |
| **Context file** | `GEMINI.md` | `CLAUDE.md` |
| **Package format** | Extensions (`gemini-extension.json`) | Skills (YAML frontmatter) |
| **Install mechanism** | `gemini extensions install <url>` | Manual file creation |
| **Namespacing** | `/git:commit` (subdirectory `:`) | `/skill-name` (flat) |

---

## 6. Templates & Examples

### Starter Custom Commands

#### `/review` — Code Review

```toml
# .gemini/commands/review.toml
description = "Review recent code changes"
prompt = """
Review the following code changes for quality, security, and best practices:

```diff
!{git diff HEAD~1}
```

Provide feedback organized by severity:
- **Critical** (must fix before merge)
- **Warning** (should fix)
- **Suggestion** (nice to have)
"""
```

#### `/test` — Generate Tests

```toml
# .gemini/commands/test.toml
description = "Generate tests for a file"
prompt = """
Generate comprehensive unit tests for the following file: {{args}}

Requirements:
- Use the project's existing test framework
- Cover edge cases and error handling
- Include both positive and negative test cases
- Add descriptive test names
"""
```

#### `/doc` — Generate Documentation

```toml
# .gemini/commands/doc.toml
description = "Generate documentation for a module"
prompt = """
Generate comprehensive documentation for: {{args}}

Include:
- Module overview and purpose
- Public API reference
- Usage examples
- Configuration options (if applicable)
"""
```

#### `/fix` — Bug Fix

```toml
# .gemini/commands/fix.toml
description = "Fix a described bug"
prompt = """
Fix the following bug: {{args}}

Steps:
1. Locate the relevant code
2. Identify the root cause
3. Implement the fix
4. Verify with a test
"""
```

### Starter Agent Skills

#### Security Auditor

```
~/.gemini/skills/security-auditor/SKILL.md
```

```markdown
---
name: security-auditor
description: Performs automated security audits on code, checking for OWASP Top 10 vulnerabilities and insecure patterns.
---

When activated, perform a security audit:

1. Scan for hardcoded secrets and credentials
2. Check for SQL injection vulnerabilities
3. Identify XSS attack vectors
4. Review authentication and authorization logic
5. Check dependency versions for known CVEs
6. Provide remediation steps for each finding

Output format:
- **CRITICAL**: Immediate action required
- **HIGH**: Fix before next release
- **MEDIUM**: Plan to address
- **LOW**: Consider improving
```

#### Reflex Developer

```
~/.gemini/skills/reflex-dev/SKILL.md
```

```markdown
---
name: reflex-dev
description: Expert in Reflex Python web framework development, state management, and component patterns.
---

You are a Reflex framework expert. When helping with Reflex code:

1. Follow Reflex conventions for state management
2. Use `rx.State` subclasses with proper event handlers
3. Implement proper type hints on all state variables
4. Use `rx.cond` for conditional rendering
5. Follow component composition patterns

Refer to `references/` for Reflex API documentation.
```

---

## Quick Reference Links

| Resource | URL |
|---|---|
| Custom Commands Docs | [geminicli.com/docs/cli/custom-commands](https://geminicli.com/docs/cli/custom-commands) |
| Agent Skills Docs | [geminicli.com/docs/skills](https://geminicli.com/docs/skills) |
| Extensions Guide | [geminicli.com/docs/extensions](https://geminicli.com/docs/extensions) |
| Writing Extensions | [geminicli.com/docs/extensions/writing-extensions](https://geminicli.com/docs/extensions/writing-extensions) |
| Extensions Gallery | [geminicli.com/extensions/browse](https://geminicli.com/extensions/browse/) |
| Extensions Reference | [geminicli.com/docs/extensions/reference](https://geminicli.com/docs/extensions/reference) |
