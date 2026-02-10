---
name: commit
description: Create a conventional commit with staged changes.
  Use after making code changes that are ready to commit.
context: fork
disable-model-invocation: true
allowed-tools: Read, Bash, Grep
---

Create a git commit with conventional commit format:

1. Run `git diff --staged` to review staged changes
2. Analyze what was changed and why
3. Write a conventional commit message:
   - Format: `type(scope): description`
   - Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `style`, `perf`
   - Scope: affected module or component
   - Description: imperative, lowercase, no period
4. Run `git commit -m "message"`

Examples:
- `feat(auth): add OAuth2 login flow`
- `fix(api): handle null response from payment gateway`
- `refactor(grid): extract factory pattern for AG Grid`
- `docs(readme): add setup instructions for Windows`
