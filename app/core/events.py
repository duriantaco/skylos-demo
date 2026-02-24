from __future__ import annotations

from typing import Any, Callable

EVENT_NOTE_ARCHIVED = "note_archived"  # UNUSED (demo)


class EventBus:
    _listeners: dict[str, list[Callable]] = {}

    @classmethod
    def on(cls, event_name: str):
        def decorator(fn: Callable) -> Callable:
            cls._listeners.setdefault(event_name, []).append(fn)
            return fn

        return decorator

    @classmethod
    def emit(cls, event_name: str, **kwargs: Any) -> None:
        for handler in cls._listeners.get(event_name, []):
            handler(**kwargs)


@EventBus.on("note_created")
def on_note_created_log(**kwargs: Any) -> None:
    title = kwargs.get("title", "")
    print(f"[event] note_created: {title}")


@EventBus.on("note_deleted")
def on_note_deleted_cleanup(**kwargs: Any) -> None:  # UNUSED (demo)
    note_id = kwargs.get("note_id")
    print(f"[cleanup] Deleted note: {note_id}")


@EventBus.on("note_created")
def on_note_created_notify(**kwargs: Any) -> None:
    title = kwargs.get("title", "")
    print(f"[notify] New note: {title}")


@EventBus.on("user_signed_up")
def on_user_signed_up_welcome(**kwargs: Any) -> None:  # UNUSED (demo)
    email = kwargs.get("email", "")
    print(f"[welcome] New user: {email}")
