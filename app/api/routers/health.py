# app/api/routers/health.py
from fastapi import APIRouter, Query

from app.core.feature_flags import is_enabled

router = APIRouter()

@router.get("/health")
def health():
    if is_enabled("v2_health"):
        return {"ok": True, "version": 2}
    return {"ok": True}

@router.get("/debug/read-file")
def read_file(path: str = Query(...)):
    # INTENTIONALLY BAD (demo): path traversal
    with open(path, "r", encoding="utf-8") as f:
        return {"data": f.read()[:500]}