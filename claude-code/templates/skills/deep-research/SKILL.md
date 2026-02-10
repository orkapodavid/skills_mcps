---
name: deep-research
description: Research a topic thoroughly in the codebase.
  Use when you need comprehensive understanding of a module or feature.
argument-hint: "[topic or module name]"
context: fork
agent: Explore
---

Research `$ARGUMENTS` thoroughly:

1. **Find relevant files** using Glob and Grep
2. **Read key files** — focus on:
   - Main implementation files
   - Configuration and constants
   - Tests (to understand expected behavior)
   - Documentation and comments
3. **Map relationships** — how does this connect to other modules?
4. **Summarize findings**:
   - Architecture overview
   - Key classes/functions and their roles
   - Data flow
   - External dependencies
   - Potential issues or tech debt
   - File list with brief descriptions
