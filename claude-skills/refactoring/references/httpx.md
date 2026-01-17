# HTTPX Migration Guide

Replace `requests` with `httpx` for async capabilities and HTTP/2 support.

## Connection Pooling

**Crucial**: Reuse `httpx.AsyncClient` to utilize connection pooling. Creating a client for every request destroys performance.

**Optimized Pattern:**
```python
async with httpx.AsyncClient(http2=True) as client:
    tasks = [client.get(url) for url in urls]
    await asyncio.gather(*tasks)
```

## Key Differences from Requests

| Feature | Requests | HTTPX | Action |
| :--- | :--- | :--- | :--- |
| Redirects | Follows automatically | Manual | Set `follow_redirects=True`. |
| Timeouts | No default | 5 seconds | Configure explicitly if needed. |
| Encoding | ISO-8859-1 default | UTF-8 default | Check legacy assumptions. |
| Errors | `requests.exceptions` | `httpx.RequestError` | Update `try/except` blocks. |

## Prefect Integration

Do not pass `httpx.AsyncClient` between tasks if they might run on different workers/threads. Create the client within the flow or task context manager.
