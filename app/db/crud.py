# app/db/crud.py
from sqlalchemy.orm import Session
from sqlalchemy import select, text

from app.db.models import Note
from app.schemas.notes import NoteCreate

# UNUSED (demo): constant not used
DEFAULT_PAGE_SIZE = 50  # UNUSED (demo)

def create_note(db: Session, payload: NoteCreate) -> Note:
    note = Note(title=payload.title, body=payload.body)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note

def list_notes(db: Session) -> list[Note]:
    stmt = select(Note).order_by(Note.id.desc())
    return list(db.execute(stmt).scalars().all())

def search_notes(db: Session, q: str) -> list[Note]:
    """
    Intentionally uses raw SQL (still safe-ish with params).
    You can later change this to a *bad* f-string SQL interpolation to demo Skylos.
    """
    sql = text("SELECT id, title, body FROM notes WHERE title LIKE :q OR body LIKE :q ORDER BY id DESC")
    rows = db.execute(sql, {"q": f"%{q}%"}).fetchall()
    return [Note(id=r[0], title=r[1], body=r[2]) for r in rows]

# UNUSED (demo): dead helper
def _row_to_dict(row) -> dict:  # UNUSED (demo)
    return {"id": row[0], "title": row[1], "body": row[2]}
