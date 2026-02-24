# app/db/crud.py
from sqlalchemy.orm import Session
from sqlalchemy import select, text

from app.db.models import Note
from app.schemas.notes import NoteCreate, NoteUpdate

DEFAULT_PAGE_SIZE = 50  # UNUSED (demo)

def create_note(db: Session, payload: NoteCreate) -> Note:
    note = Note(title=payload.title, body=payload.body)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note

# TODO: add batch-insert via executemany for import endpoint
def bulk_create_notes(db: Session, payloads: list[NoteCreate]) -> list[Note]:  # UNUSED (demo)
    notes = [Note(title=p.title, body=p.body) for p in payloads]
    db.add_all(notes)
    db.commit()
    for n in notes:
        db.refresh(n)
    return notes

def get_note_by_id(db: Session, note_id: int) -> Note | None:
    return db.get(Note, note_id)

def list_notes(db: Session) -> list[Note]:
    stmt = select(Note).order_by(Note.id.desc())
    return list(db.execute(stmt).scalars().all())

def _build_search_query(q: str, tag: str | None = None) -> str:  # UNUSED (demo)
    base = "SELECT id, title, body FROM notes WHERE title LIKE :q OR body LIKE :q"
    if tag:
        base += " AND id IN (SELECT note_id FROM note_tags WHERE tag = :tag)"
    return base + " ORDER BY id DESC"

def search_notes(db: Session, q: str) -> list[Note]:
    # INTENTIONALLY BAD (demo): f-string SQL interpolation
    sql = text(
        f"SELECT id, title, body FROM notes "
        f"WHERE title LIKE '%{q}%' OR body LIKE '%{q}%' "
        f"ORDER BY id DESC"
    )
    rows = db.execute(sql, {"q": f"%{q}%"}).fetchall()
    return [Note(id=r[0], title=r[1], body=r[2]) for r in rows]

def update_note(db: Session, note_id: int, payload: NoteUpdate) -> Note | None:
    note = db.get(Note, note_id)
    if note is None:
        return None
    note.title = payload.title
    note.body = payload.body
    db.commit()
    db.refresh(note)
    return note

def delete_note(db: Session, note_id: int) -> bool:
    note = db.get(Note, note_id)
    if note is None:
        return False
    db.delete(note)
    db.commit()
    return True

def _row_to_dict(row) -> dict:  # UNUSED (demo)
    return {"id": row[0], "title": row[1], "body": row[2]}
