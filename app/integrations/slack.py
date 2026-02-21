from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from .http_client import get_httpx_client, request_json


@dataclass(frozen=True)
class SlackConfig:
    webhook_url: str
    channel: Optional[str] = None
    username: str = "Skylos"
    icon_emoji: str = ":shield:"


def _load_slack_config() -> Optional[SlackConfig]:
    url = os.getenv("SLACK_WEBHOOK_URL")
    if not url:
        return None
    return SlackConfig(
        webhook_url=url,
        channel=os.getenv("SLACK_CHANNEL"),
        username=os.getenv("SLACK_USERNAME", "Skylos"),
        icon_emoji=os.getenv("SLACK_ICON", ":shield:"),
    )


def _build_payload(
    text: str, cfg: SlackConfig, extra: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {"text": text, "username": cfg.username, "icon_emoji": cfg.icon_emoji}
    if cfg.channel:
        payload["channel"] = cfg.channel
    if extra:
        payload.update(extra)
    return payload


async def send_slack_message(text: str, *, extra: Optional[Dict[str, Any]] = None) -> bool:
    cfg = _load_slack_config()
    if not cfg:
        return False

    async with get_httpx_client() as client:
        payload = _build_payload(text, cfg, extra=extra)
        await request_json(client, "POST", cfg.webhook_url, json=payload)
        return True


# DEAD (currently unused): richer blocks builder (common in real repos), not used by send_slack_message
def build_finding_blocks(
    title: str,
    *,
    severity: str,
    file_path: str,
    line: int,
    rule_id: str,
) -> Dict[str, Any]:
    return {
        "blocks": [
            {"type": "header", "text": {"type": "plain_text", "text": title}},
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Severity:*\n{severity}"},
                    {"type": "mrkdwn", "text": f"*Rule:*\n{rule_id}"},
                    {"type": "mrkdwn", "text": f"*File:*\n{file_path}:{line}"},
                ],
            },
        ]
    }
