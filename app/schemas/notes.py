# app/schemas/notes.py
from pydantic import BaseModel, Field

class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    body: str = Field(min_length=1, max_length=10_000)

class NoteOut(BaseModel):
    id: int
    title: str
    body: str

# UNUSED (demo): never used schema
class NoteInternal(BaseModel):  # UNUSED (demo)
    title_norm: str
