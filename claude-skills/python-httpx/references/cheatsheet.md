# httpx Cheat Sheet (agent-oriented)

- Prefer client instances for connection pooling:
  
  ```python
  import httpx
  with httpx.Client(http2=True, timeout=httpx.Timeout(10.0)) as client:
      r = client.get("https://api.example.com")
  ```

- Async client for concurrency:
  
  ```python
  async with httpx.AsyncClient(http2=True, timeout=10.0) as client:
      r = await client.get(url)
  ```

- Timeouts (connect/read/write/pool):
  
  ```python
  timeout = httpx.Timeout(connect=5.0, read=15.0, write=15.0, pool=5.0)
  client = httpx.Client(timeout=timeout)
  ```

- Limits (connections & keep-alive):
  
  ```python
  limits = httpx.Limits(max_connections=100, max_keepalive_connections=20)
  client = httpx.Client(limits=limits)
  ```

- Retries: httpx has no global built-in policy; use manual retry/backoff around transient errors (examples provided) or a transport with retries if applicable.

- HTTP/2:
  
  ```python
  client = httpx.Client(http2=True)
  ```

- Proxies:
  
  ```python
  httpx.get(url, proxies={"http": proxy_url, "https": proxy_url})
  ```

- Auth:
  - Basic: `auth=("user", "pass")`
  - Bearer: `headers={"Authorization": f"Bearer {token}"}`
  - OAuth2: see `examples/auth_oauth2.py` (Authlib)

- Cookies and sessions:
  
  ```python
  client = httpx.Client(cookies={"sid": "..."})
  ```

- Streaming download to disk:
  
  ```python
  with client.stream("GET", url) as r:
      r.raise_for_status()
      with open(path, "wb") as f:
          for chunk in r.iter_bytes():
              f.write(chunk)
  ```

- File upload:
  
  ```python
  files = {"file": ("name.txt", open("name.txt", "rb"), "text/plain")}
  r = client.post(url, files=files)
  ```

- Raise on HTTP errors:
  
  ```python
  r.raise_for_status()
  ```

Tips:
- Always set timeouts explicitly for long-running I/O.
- Centralize headers/base_url in a Client.
- Handle `httpx.TimeoutException`, `httpx.TransportError`, and optionally `httpx.HTTPStatusError` for 5xx.
