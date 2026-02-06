# app/services/notes_services.py
from sqlalchemy.orm import Session

from app.db import crud
from app.schemas.notes import NoteCreate

def create_note(db: Session, payload: NoteCreate):
    return crud.create_note(db, payload)

def list_notes(db: Session):
    return crud.list_notes(db)

def search_notes(db: Session, q: str):
    q = q.strip()
    return crud.search_notes(db, q)

# UNUSED (demo): business helper never called
def _validate_title(title: str) -> None:  # UNUSED (demo)
    if not title.strip():
        raise ValueError("title empty")
