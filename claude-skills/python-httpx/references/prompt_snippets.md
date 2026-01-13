# Prompt snippets for LLM coders

- Safe GET (sync):
  
  You are writing Python with httpx. Use `HttpxSkill.get` with a timeout and handle exceptions. Do not retry on 4xx. Retry transient errors up to 3 times with exponential backoff.

- Safe GET (async):
  
  Use `HttpxSkill.aget` in an async function with `asyncio.run`. Reuse the same skill instance across calls. Set `http2=True` only when server supports it.

- Streaming download:
  
  Use `HttpxSkill.stream_download(url, path)` and verify `r.raise_for_status()` before writing. Write chunks to disk inside the context manager.

- File upload:
  
  Use `HttpxSkill.upload_file(url, path, field_name="file", content_type=...)` with a `files` dict and close any opened file handles.

- OAuth2 (optional):
  
  If using Authlib, create `AsyncOAuth2Client` or `OAuth2Session` and pass `auth` or `headers` to the skill methods. Store tokens securely; don’t print secrets.

- Proxies and HTTP/2:
  
  Use proxies only if required. Enabling HTTP/2 may improve performance; validate compatibility. Don’t mix proxies that break HTTP/2 unless necessary.
