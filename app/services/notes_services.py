# app/services/notes_services.py
from sqlalchemy.orm import Session

from app.db import crud
from app.schemas.notes import NoteCreate
from app.core.decorators import retry, log_execution
from app.core.events import EventBus


@retry(max_attempts=2, delay=0.05)
@log_execution
def create_note(db: Session, payload: NoteCreate):
    result = crud.create_note(db, payload)
    EventBus.emit("note_created", title=payload.title)
    return result

def list_notes(db: Session):
    return crud.list_notes(db)

def search_notes(db: Session, q: str):
    q = q.strip()
    return crud.search_notes(db, q)

def normalize_and_score_query(q: str, *, mode: str = "default") -> int:
    # INTENTIONALLY BAD (demo): complexity + nesting
    score = 0
    if q:
        if len(q) > 3:
            if " " in q:
                score += 2
            else:
                score += 1
            if q.islower():
                score += 1
            if q.isalpha():
                score += 1
        else:
            if q.isdigit():
                score -= 1
            else:
                score += 0
    if mode == "strict":
        if score > 2:
            score += 5
    return score

# UNUSED (demo): business helper never called
def _validate_title(title: str) -> None:  # UNUSED (demo)
    if not title.strip():
        raise ValueError("title empty")
