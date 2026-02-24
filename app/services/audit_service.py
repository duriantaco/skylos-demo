from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


AUDIT_RETENTION_DAYS = 90  # UNUSED (demo)


@dataclass
class AuditEntry:
    action: str = ""
    entity_type: str = ""
    entity_id: int = 0
    actor: str = "system"
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


# NOTE: swap to DB-backed via AuditLog model later
_audit_store: list[AuditEntry] = []


def log_action(
    action: str,
    entity_type: str,
    entity_id: int,
    actor: str = "system",
) -> AuditEntry:
    entry = AuditEntry(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        actor=actor,
    )
    _audit_store.append(entry)
    print(f"[audit] {actor} {action} {entity_type}#{entity_id}")
    return entry


def query_audit_log(  # UNUSED (demo)
    entity_type: str = "",
    entity_id: int | None = None,
    limit: int = 50,
) -> list[AuditEntry]:
    results = _audit_store
    if entity_type:
        results = [e for e in results if e.entity_type == entity_type]
    if entity_id is not None:
        results = [e for e in results if e.entity_id == entity_id]
    return results[-limit:]


def _redact_sensitive_fields(  # UNUSED (demo)
    entry: dict[str, Any],
    sensitive_keys: tuple[str, ...] = ("password", "token", "secret"),
) -> dict[str, Any]:
    # TODO: make the redaction list configurable via Settings
    return {
        k: "***" if k in sensitive_keys else v
        for k, v in entry.items()
    }


# TODO: wire into /admin/audit/export once admin auth is ready
def export_audit_csv(entries: list[AuditEntry]) -> str:  # UNUSED (demo)
    header = "action,entity_type,entity_id,actor,timestamp"
    lines = [header]
    for e in entries:
        lines.append(f"{e.action},{e.entity_type},{e.entity_id},{e.actor},{e.timestamp}")
    return "\n".join(lines)
