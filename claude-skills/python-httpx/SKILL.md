---
name: Python Httpx Skill
description: This skill should be used when the user asks to "use httpx", "make http requests with python", "write python httpx code", "download files with httpx", or "perform async http requests".
version: 0.1.0
---

# Python Httpx Skill

This skill provides a helper module and best practices for performing HTTP requests in Python using the `httpx` library. It covers synchronous and asynchronous usage, efficient file downloads, and error handling.

## Usage

### Using the Helper Script

To simplify `httpx` usage with safe defaults (timeouts, retries), use the provided helper script `scripts/httpx_skill.py`.

```python
from scripts.httpx_skill import HttpxSkill

# Sync
skill = HttpxSkill()
resp = skill.get("https://example.com")

# Async
import asyncio
async def main():
    skill = HttpxSkill(async_mode=True)
    resp = await skill.aget("https://example.com")
asyncio.run(main())
```

### Prompting for Httpx Code

When writing code directly, adhere to the patterns defined in `references/prompt_snippets.md` to ensure reliability and safety.

## Resources

### References

- **`references/cheatsheet.md`**: concise patterns and pitfalls for using `httpx`.
- **`references/prompt_snippets.md`**: standard prompts to steer coding behavior for correct `httpx` implementation.

### Scripts

- **`scripts/httpx_skill.py`**: A helper class wrapping `httpx.Client` and `httpx.AsyncClient` with sane defaults for timeouts and retries.

### Examples

The `examples/` directory contains runnable recipes for common tasks:
- Sync and Async basic requests
- Streaming file downloads
- File uploads
- Retry logic
- OAuth2 integration

## Best Practices

- Always set timeouts (the helper class does this by default).
- Use `raise_for_status()` to handle HTTP errors explicitly.
- Reuse client instances for connection pooling (especially in async).
- Use `stream_download` for large files to avoid memory issues.

### External Documentation
- [Official httpx Documentation](https://www.python-httpx.org/)
- [httpx Quickstart](https://www.python-httpx.org/quickstart/)
- [Timeouts](https://www.python-httpx.org/advanced/timeouts/)
- [Clients/Sessions](https://www.python-httpx.org/advanced/clients/)
- [HTTP/2](https://www.python-httpx.org/http2/)
- [Proxies](https://www.python-httpx.org/advanced/proxies/)
- [Auth Integration](https://www.python-httpx.org/advanced/authentication/)
- [Authlib (OAuth)](https://docs.authlib.org/en/latest/client/httpx.html)
