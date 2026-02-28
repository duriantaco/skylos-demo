from __future__ import annotations

import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class NotificationChannel(Enum):
    EMAIL = "email"
    SLACK = "slack"
    SMS = "sms"


MAX_BATCH_SIZE = 500  # UNUSED (demo)


def _dispatch_email(recipient: str, message: str) -> None:
    print(f"[email] To: {recipient} — {message}")


def _dispatch_slack(recipient: str, message: str) -> None:
    print(f"[slack] #{recipient}: {message}")


def _dispatch_sms(recipient: str, message: str) -> None:
    print(f"[sms] {recipient}: {message}")


def send_notification(channel: NotificationChannel, recipient: str, message: str) -> None:
    dispatcher = getattr(sys.modules[__name__], f"_dispatch_{channel.value}", None)
    if dispatcher is None:
        raise ValueError(f"No dispatcher for channel: {channel.value}")
    dispatcher(recipient, message)


def send_bulk_notifications(notifications: list[dict[str, Any]]) -> int:  # UNUSED (demo)
    sent = 0
    for n in notifications[:MAX_BATCH_SIZE]:
        try:
            send_notification(
                NotificationChannel(n["channel"]),
                n["recipient"],
                n["message"],
            )
            sent += 1
        except Exception:
            pass
    return sent


def _render_template(template_name: str, context: dict[str, Any]) -> str:  # UNUSED (demo)
    template = f"<{template_name}>"
    for key, value in context.items():
        template = template.replace(f"{{{{{key}}}}}", str(value))
    return template


@dataclass
class NotificationLog:  # UNUSED (demo)
    channel: str = ""
    recipient: str = ""
    message: str = ""
    sent_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    status: str = "pending"


def schedule_notification(  # UNUSED (demo)
    channel: NotificationChannel,
    recipient: str,
    message: str,
    send_at: str = "",
) -> dict[str, Any]:
    return {
        "channel": channel.value,
        "recipient": recipient,
        "message": message,
        "send_at": send_at or datetime.utcnow().isoformat(),
        "status": "scheduled",
    }
