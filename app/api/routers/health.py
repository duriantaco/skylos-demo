# app/api/routers/health.py
from fastapi import APIRouter, Query

router = APIRouter()

@router.get("/health")
def health():
    return {"ok": True}

@router.get("/debug/read-file")
def read_file(path: str = Query(...)):
    # INTENTIONALLY BAD (demo): path traversal
    with open(path, "r", encoding="utf-8") as f:
        return {"data": f.read()[:500]}