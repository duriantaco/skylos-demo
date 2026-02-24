from __future__ import annotations

import time
import uuid
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


def generate_correlation_id() -> str:  # UNUSED (demo)
    return str(uuid.uuid4())


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start = time.time()
        response = await call_next(request)
        duration_ms = (time.time() - start) * 1000
        print(f"[http] {request.method} {request.url.path} {response.status_code} {duration_ms:.0f}ms")
        return response


class CorrelationIdMiddleware(BaseHTTPMiddleware):  # UNUSED (demo)
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        correlation_id = request.headers.get("X-Correlation-ID", generate_correlation_id())
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):  # UNUSED (demo)
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self._max = max_requests
        self._window = window_seconds
        self._counters: dict[str, list[float]] = {}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        ip = request.client.host if request.client else "unknown"
        now = time.time()
        hits = self._counters.setdefault(ip, [])
        hits[:] = [t for t in hits if now - t < self._window]
        if len(hits) >= self._max:
            return Response("Rate limited", status_code=429)
        hits.append(now)
        return await call_next(request)
