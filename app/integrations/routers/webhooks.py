from __future__ import annotations

import os
from fastapi import APIRouter, Request, HTTPException

from app.integrations.webhook_signing import verify_hmac_sha256
from app.integrations.metrics import record_request, record_latency_ms
import time


router = APIRouter(prefix="/integrations")


@router.post("/webhooks/demo")
async def demo_webhook(request: Request):

    t0 = time.time()
    record_request()

    secret = os.getenv("WEBHOOK_SECRET", "dev-secret")
    sig = request.headers.get("x-signature")

    body = await request.body()
    if not verify_hmac_sha256(secret=secret, body=body, signature=sig):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # pretend to do something with payload
    # (intentionally minimal for demo)
    record_latency_ms((time.time() - t0) * 1000.0)
    return {"ok": True}
