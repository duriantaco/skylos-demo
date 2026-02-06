from __future__ import annotations

import os
from fastapi import FastAPI

from app.integrations.routers.webhooks import router as webhooks_router
from app.integrations.slack import send_slack_message
from app.integrations.github import get_repo
from app.integrations.metrics import record_request
import flask # UNUSED (demo)
import sys

def init_integrations(app: FastAPI) -> None:
    app.include_router(webhooks_router, tags=["integrations"])

    @app.on_event("startup")
    async def _integrations_startup() -> None:
        record_request()

        if os.getenv("SLACK_WEBHOOK_URL"):
            await send_slack_message("Skylos demo API started")

        owner = os.getenv("DEMO_GH_OWNER")
        repo = os.getenv("DEMO_GH_REPO")
        if owner and repo:
            await get_repo(owner, repo)
