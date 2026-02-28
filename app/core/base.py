from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class NoteRepository(ABC):
    @abstractmethod
    def create(self, data: dict[str, Any]) -> dict[str, Any]: ...

    @abstractmethod
    def find_by_id(self, note_id: str) -> dict[str, Any] | None: ...

    @abstractmethod
    def list_all(self) -> list[dict[str, Any]]: ...


class SqlNoteRepository(NoteRepository):
    def __init__(self, session: Any = None):
        self._session = session

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        return {"id": "sql-1", **data}

    def find_by_id(self, note_id: str) -> dict[str, Any] | None:
        return {"id": note_id, "title": "SQL note"}

    def list_all(self) -> list[dict[str, Any]]:
        return []


# TODO: swap in when Mongo Atlas cluster is provisioned
class MongoNoteRepository(NoteRepository):  # UNUSED (demo)
    def __init__(self, connection_uri: str = "mongodb://localhost:27017"):
        self._uri = connection_uri

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        return {"id": "mongo-1", **data}

    def find_by_id(self, note_id: str) -> dict[str, Any] | None:
        return {"id": note_id, "title": "Mongo note"}

    def list_all(self) -> list[dict[str, Any]]:
        return []


class Notifier(ABC):
    @abstractmethod
    def send(self, message: str) -> None: ...


class SlackNotifier(Notifier):
    def send(self, message: str) -> None:
        print(f"[slack] {message}")


class PagerDutyNotifier(Notifier):  # UNUSED (demo)
    def __init__(self, routing_key: str = ""):
        self._routing_key = routing_key

    def send(self, message: str) -> None:
        print(f"[pagerduty] {message}")
