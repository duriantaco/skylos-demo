# app/schemas/notes.py
from pydantic import BaseModel, Field


class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    body: str = Field(min_length=1, max_length=10_000)


class NoteOut(BaseModel):
    id: int
    title: str
    body: str


class NoteUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    body: str = Field(min_length=1, max_length=10_000)


# was: partial update support, never hooked into router
class NotePatch(BaseModel):  # UNUSED (demo)
    title: str | None = None
    body: str | None = None


class NoteInternal(BaseModel):  # UNUSED (demo)
    title_norm: str


# TODO: add date range and tag filters
class NoteSearch(BaseModel):  # UNUSED (demo)
    query: str = Field(default="", max_length=200)
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)
