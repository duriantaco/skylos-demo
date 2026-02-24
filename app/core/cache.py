from __future__ import annotations

import functools
import time
from typing import Any


class InMemoryCache:
    def __init__(self, default_ttl: int = 300):
        self._store: dict[str, tuple[Any, float]] = {}
        self._default_ttl = default_ttl

    def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        value, expires = entry
        if time.time() > expires:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        self._store[key] = (value, time.time() + (ttl or self._default_ttl))

    def delete(self, key: str) -> None:
        self._store.pop(key, None)


# TODO: swap in when we move to multi-instance deployment
class RedisCache:  # UNUSED (demo)
    def __init__(self, url: str = "redis://localhost:6379/0"):
        self._url = url

    def get(self, key: str) -> Any | None:
        return None

    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        pass

    def delete(self, key: str) -> None:
        pass


_default_cache = InMemoryCache()


def cached(namespace: str, ttl: int = 120):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            cache_key = f"{namespace}:{fn.__name__}:{args}:{kwargs}"
            hit = _default_cache.get(cache_key)
            if hit is not None:
                return hit
            result = fn(*args, **kwargs)
            _default_cache.set(cache_key, result, ttl)
            return result

        return wrapper

    return decorator


# NOTE: useful for cache-busting after bulk writes
def invalidate_cache_for(namespace: str) -> None:  # UNUSED (demo)
    keys_to_delete = [
        k for k in _default_cache._store if k.startswith(f"{namespace}:")
    ]
    for k in keys_to_delete:
        _default_cache.delete(k)
