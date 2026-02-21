from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

import httpx


@dataclass(frozen=True)
class HttpRetryPolicy:
    max_attempts: int = 3
    base_backoff_s: float = 0.2
    max_backoff_s: float = 2.0
    retry_on_status: tuple[int, ...] = (429, 500, 502, 503, 504)

    def backoff(self, attempt_idx: int) -> float:
        # attempt_idx starts at 0
        t = min(self.max_backoff_s, self.base_backoff_s * (2**attempt_idx))
        return t


_DEFAULT_TIMEOUT = httpx.Timeout(connect=2.0, read=6.0, write=6.0, pool=6.0)

# DEAD (currently unused): unused constant
DEFAULT_HEADERS: Dict[str, str] = {"User-Agent": "skylos-demo/0.1"}


def get_httpx_client(
    *,
    base_url: Optional[str] = None,
    timeout: httpx.Timeout = _DEFAULT_TIMEOUT,
) -> httpx.AsyncClient:
    verify_ssl = os.getenv("HTTP_VERIFY_SSL", "true").lower() != "false"

    headers = {
        "User-Agent": os.getenv("APP_USER_AGENT", "skylos-demo/0.1"),
        "Accept": "application/json",
    }

    return httpx.AsyncClient(
        base_url=base_url or "",
        timeout=timeout,
        headers=headers,
        verify=verify_ssl,
        follow_redirects=True,
    )


async def request_json(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    *,
    json: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    retry: Optional[HttpRetryPolicy] = None,
) -> Dict[str, Any]:
    policy = retry or HttpRetryPolicy()

    last_exc: Optional[Exception] = None
    for attempt in range(policy.max_attempts):
        try:
            resp = await client.request(method, url, json=json, headers=headers)
            if resp.status_code in policy.retry_on_status:
                time.sleep(policy.backoff(attempt))
                continue
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, dict):
                return data
            return {"_": data}
        except Exception as e:
            last_exc = e
            time.sleep(policy.backoff(attempt))

    # if we got here, all attempts failed
    raise RuntimeError(f"request_json failed after {policy.max_attempts} attempts") from last_exc


# DEAD (currently unused): dead helper for text responses, never called by other module
async def request_text(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    *,
    data: Optional[Dict[str, Any]] = None,
) -> str:
    resp = await client.request(method, url, data=data)
    resp.raise_for_status()
    return resp.text
