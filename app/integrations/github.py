from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

from .http_client import get_httpx_client, request_json


@dataclass(frozen=True)
class GitHubConfig:
    token: str
    api_base: str = "https://api.github.com"


def _load_github_config() -> Optional[GitHubConfig]:
    tok = os.getenv("GITHUB_TOKEN")
    if not tok:
        return None
    return GitHubConfig(token=tok, api_base=os.getenv("GITHUB_API_BASE", "https://api.github.com"))


def _auth_headers(cfg: GitHubConfig) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {cfg.token}",
        "Accept": "application/vnd.github+json",
    }


async def get_repo(
    owner: str,
    repo: str,
) -> Optional[Dict[str, Any]]:
    cfg = _load_github_config()
    if not cfg:
        return None

    async with get_httpx_client(base_url=cfg.api_base) as client:
        return await request_json(
            client, "GET", f"/repos/{owner}/{repo}", headers=_auth_headers(cfg)
        )


# DEAD (currently unused): helper for checking if an issue exists, never called
async def find_issue_by_title(
    owner: str,
    repo: str,
    title: str,
) -> Optional[int]:
    cfg = _load_github_config()
    if not cfg:
        return None

    async with get_httpx_client(base_url=cfg.api_base) as client:
        data = await request_json(
            client,
            "GET",
            f"/repos/{owner}/{repo}/issues",
            headers=_auth_headers(cfg),
        )
        items = data.get("_") if isinstance(data.get("_"), list) else data.get("items")
        if not isinstance(items, list):
            return None
        for it in items:
            if isinstance(it, dict) and it.get("title") == title:
                num = it.get("number")
                if isinstance(num, int):
                    return num
        return None
