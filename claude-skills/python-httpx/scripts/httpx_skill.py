import asyncio
import time
from typing import Any, Dict, Optional, Union, Callable, Iterable

import httpx

JsonType = Union[dict, list, str, int, float, bool, None]


def _default_timeout() -> httpx.Timeout:
    return httpx.Timeout(connect=5.0, read=30.0, write=30.0, pool=5.0)


def _default_limits() -> httpx.Limits:
    return httpx.Limits(max_connections=100, max_keepalive_connections=20)


def _should_retry(exc: BaseException, response: Optional[httpx.Response]) -> bool:
    if isinstance(exc, (httpx.TimeoutException, httpx.TransportError)):
        return True
    if response is not None and 500 <= response.status_code < 600:
        return True
    return False


def _sleep_backoff(attempt: int, base: float = 0.5, cap: float = 8.0) -> None:
    delay = min(cap, base * (2 ** (attempt - 1)))
    time.sleep(delay)


class HttpxSkill:
    """
    A thin convenience wrapper around httpx for LLM coders.
    - Provides sync + async helpers
    - Adds optional retry-with-backoff for transient errors
    - Centralizes client creation with sane defaults
    """

    def __init__(
        self,
        async_mode: bool = False,
        base_url: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[httpx.Timeout] = None,
        limits: Optional[httpx.Limits] = None,
        http2: bool = False,
        proxies: Optional[Union[str, Dict[str, str]]] = None,
        verify: Union[bool, str] = True,
        retries: int = 0,
        backoff_base: float = 0.5,
    ) -> None:
        self.async_mode = async_mode
        self.base_url = base_url
        self.headers = headers or {}
        self.timeout = timeout or _default_timeout()
        self.limits = limits or _default_limits()
        self.http2 = http2
        self.proxies = proxies
        self.verify = verify
        self.retries = max(0, retries)
        self.backoff_base = backoff_base

        if async_mode:
            self._client = httpx.AsyncClient(
                base_url=base_url,
                headers=self.headers,
                timeout=self.timeout,
                limits=self.limits,
                http2=http2,
                proxies=proxies,
                verify=verify,
            )
        else:
            self._client = httpx.Client(
                base_url=base_url,
                headers=self.headers,
                timeout=self.timeout,
                limits=self.limits,
                http2=http2,
                proxies=proxies,
                verify=verify,
            )

    # ---------- internal retry helper ----------
    def _request_with_retry(
        self,
        method: str,
        url: str,
        *,
        data: Optional[Union[bytes, dict]] = None,
        json: Optional[JsonType] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        files: Optional[Dict[str, Any]] = None,
        stream: Optional[Iterable[bytes]] = None,
    ) -> httpx.Response:
        attempt = 0
        last_exc: Optional[BaseException] = None
        last_resp: Optional[httpx.Response] = None
        while True:
            attempt += 1
            try:
                resp = self._client.request(
                    method,
                    url,
                    data=data,
                    json=json,
                    params=params,
                    headers=headers,
                    files=files,
                    content=stream,
                )
                last_resp = resp
                if self.retries and 500 <= resp.status_code < 600:
                    if attempt <= self.retries:
                        _sleep_backoff(attempt, self.backoff_base)
                        continue
                return resp
            except BaseException as exc:  # noqa: BLE001
                last_exc = exc
                if self.retries and _should_retry(exc, last_resp):
                    if attempt <= self.retries:
                        _sleep_backoff(attempt, self.backoff_base)
                        continue
                raise

    async def _arequest_with_retry(
        self,
        method: str,
        url: str,
        *,
        data: Optional[Union[bytes, dict]] = None,
        json: Optional[JsonType] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        files: Optional[Dict[str, Any]] = None,
        stream: Optional[Iterable[bytes]] = None,
    ) -> httpx.Response:
        attempt = 0
        last_exc: Optional[BaseException] = None
        last_resp: Optional[httpx.Response] = None
        while True:
            attempt += 1
            try:
                resp = await self._client.request(
                    method,
                    url,
                    data=data,
                    json=json,
                    params=params,
                    headers=headers,
                    files=files,
                    content=stream,
                )
                last_resp = resp
                if self.retries and 500 <= resp.status_code < 600:
                    if attempt <= self.retries:
                        await asyncio.sleep(min(8.0, self.backoff_base * (2 ** (attempt - 1))))
                        continue
                return resp
            except BaseException as exc:  # noqa: BLE001
                last_exc = exc
                if self.retries and _should_retry(exc, last_resp):
                    if attempt <= self.retries:
                        await asyncio.sleep(min(8.0, self.backoff_base * (2 ** (attempt - 1))))
                        continue
                raise

    # ---------- public sync API ----------
    def get(self, url: str, **kwargs: Any) -> httpx.Response:
        return self._request_with_retry("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> httpx.Response:
        return self._request_with_retry("POST", url, **kwargs)

    def put(self, url: str, **kwargs: Any) -> httpx.Response:
        return self._request_with_retry("PUT", url, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> httpx.Response:
        return self._request_with_retry("DELETE", url, **kwargs)

    def stream_download(self, url: str, path: str, chunk_size: int = 65536) -> None:
        with self._client.stream("GET", url) as r:
            r.raise_for_status()
            with open(path, "wb") as f:
                for chunk in r.iter_bytes(chunk_size=chunk_size):
                    f.write(chunk)

    def upload_file(
        self,
        url: str,
        file_path: str,
        field_name: str = "file",
        content_type: Optional[str] = None,
        extra_fields: Optional[Dict[str, Any]] = None,
    ) -> httpx.Response:
        extra_fields = extra_fields or {}
        with open(file_path, "rb") as fp:
            files = {field_name: (file_path, fp, content_type)}
            return self.post(url, files=files, data=extra_fields)

    # ---------- public async API ----------
    async def aget(self, url: str, **kwargs: Any) -> httpx.Response:
        return await self._arequest_with_retry("GET", url, **kwargs)

    async def apost(self, url: str, **kwargs: Any) -> httpx.Response:
        return await self._arequest_with_retry("POST", url, **kwargs)

    async def aput(self, url: str, **kwargs: Any) -> httpx.Response:
        return await self._arequest_with_retry("PUT", url, **kwargs)

    async def adelete(self, url: str, **kwargs: Any) -> httpx.Response:
        return await self._arequest_with_retry("DELETE", url, **kwargs)

    async def astream_download(self, url: str, path: str, chunk_size: int = 65536) -> None:
        async with self._client.stream("GET", url) as r:
            r.raise_for_status()
            with open(path, "wb") as f:
                async for chunk in r.aiter_bytes(chunk_size=chunk_size):
                    f.write(chunk)

    async def aupload_file(
        self,
        url: str,
        file_path: str,
        field_name: str = "file",
        content_type: Optional[str] = None,
        extra_fields: Optional[Dict[str, Any]] = None,
    ) -> httpx.Response:
        extra_fields = extra_fields or {}
        with open(file_path, "rb") as fp:
            files = {field_name: (file_path, fp, content_type)}
            return await self.apost(url, files=files, data=extra_fields)

    # ---------- cleanup ----------
    def close(self) -> None:
        if isinstance(self._client, httpx.Client):
            self._client.close()

    async def aclose(self) -> None:
        if isinstance(self._client, httpx.AsyncClient):
            await self._client.aclose()

    # Context manager helpers
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.aclose()
