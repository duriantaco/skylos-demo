# app/api/routers/notes.py
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_api_key
from app.schemas.notes import NoteCreate, NoteOut
from app.services.notes_services import create_note, list_notes, search_notes
from app.integrations.http_client import get_httpx_client
from app.core.cache import cached
from app.core.pagination import PageParams, paginate

# UNUSED (demo): unused import
from datetime import datetime  # UNUSED (demo)

router = APIRouter(prefix="/notes")

@router.post("", response_model=NoteOut, dependencies=[Depends(require_api_key)])
def create(payload: NoteCreate, db: Session = Depends(get_db)):
    return create_note(db, payload)

@router.get("", response_model=list[NoteOut], dependencies=[Depends(require_api_key)])
@cached("notes", ttl=60)
def list_all(db: Session = Depends(get_db), page: int = 1, size: int = 20):
    all_notes = list_notes(db)
    result = paginate(all_notes, PageParams(page=page, size=size))
    return result.items

@router.get("/search", response_model=list[NoteOut], dependencies=[Depends(require_api_key)])
def search(
    q: str = Query(min_length=1, max_length=200),
    db: Session = Depends(get_db),
):
    return search_notes(db, q)

@router.post("/fetch")
async def fetch_url(url: str = Body(embed=True)):
    # INTENTIONALLY BAD (demo): untrusted URL -> internal fetch
    async with get_httpx_client() as client:
        r = await client.get(url)
        return {"status": r.status_code, "text": r.text[:200]}
    
# UNUSED (demo): unused endpoint helper
def _normalize_query(q: str) -> str:  # UNUSED (demo)
    return q.strip().lower()
