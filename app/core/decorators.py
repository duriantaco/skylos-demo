from __future__ import annotations

import functools
import time
import warnings
from typing import Any, Callable


def retry(max_attempts: int = 3, delay: float = 0.1):

    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exc = None
            for attempt in range(max_attempts):
                try:
                    return fn(*args, **kwargs)
                except Exception as exc:
                    last_exc = exc
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
            raise last_exc

        return wrapper

    return decorator


# TODO: wire into schema validation layer once Pydantic models stabilize
def validate_input(schema: dict) -> Callable:  # UNUSED (demo)
    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            for key, expected_type in schema.items():
                val = kwargs.get(key)
                if val is not None and not isinstance(val, expected_type):
                    raise TypeError(f"{key} must be {expected_type.__name__}")
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def log_execution(fn: Callable) -> Callable:
    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        print(f"[exec] {fn.__name__} called")
        result = fn(*args, **kwargs)
        print(f"[exec] {fn.__name__} returned")
        return result

    return wrapper


# NOTE: handy for phasing out old service helpers
def deprecate(reason: str = "deprecated") -> Callable:  # UNUSED (demo)
    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            warnings.warn(
                f"{fn.__name__} is deprecated: {reason}",
                DeprecationWarning,
                stacklevel=2,
            )
            return fn(*args, **kwargs)

        return wrapper

    return decorator
