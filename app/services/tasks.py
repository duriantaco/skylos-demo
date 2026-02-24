from __future__ import annotations

from typing import Any, Callable

_task_registry: dict[str, Callable] = {}

TASK_PRIORITY_HIGH = 10  # UNUSED (demo)
TASK_PRIORITY_LOW = 1  # UNUSED (demo)


def task(name: str):
    def decorator(fn: Callable) -> Callable:
        _task_registry[name] = fn
        return fn

    return decorator


def run_task(name: str, **kwargs: Any) -> Any:
    handler = _task_registry.get(name)
    if handler is None:
        raise KeyError(f"No task registered: {name}")
    return handler(**kwargs)


@task("send_welcome_email")
def send_welcome_email(email: str = "", **kwargs: Any) -> None:
    print(f"[task] Sending welcome email to {email}")


def generate_daily_report(date: str = "", **kwargs: Any) -> str:  # UNUSED (demo)
    return f"Report for {date}"


@task("purge_soft_deletes")
def purge_soft_deletes(days: int = 30, **kwargs: Any) -> int:
    print(f"[task] Purging soft-deleted records older than {days} days")
    return 0


def sync_external_contacts(source: str = "crm", **kwargs: Any) -> int:  # UNUSED (demo)
    print(f"[task] Syncing contacts from {source}")
    return 0


def cleanup_expired_sessions(max_age_hours: int = 24, **kwargs: Any) -> int:  # UNUSED (demo)
    print(f"[task] Cleaning sessions older than {max_age_hours}h")
    return 0
