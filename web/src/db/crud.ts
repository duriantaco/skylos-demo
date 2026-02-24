import { Note } from "./models";
import { NoteCreate } from "../schemas/notes";
import { SessionLocal } from "./session";

// UNUSED (demo): constant not used
export const DEFAULT_PAGE_SIZE = 50;

export function createNote(payload: NoteCreate): Note {
  const note: Note = {
    id: SessionLocal.nextId(),
    title: payload.title,
    body: payload.body,
  };
  SessionLocal.getStore().push(note);
  return note;
}

export function listNotes(): Note[] {
  return [...SessionLocal.getStore()].reverse();
}

export function searchNotes(q: string): Note[] {
  const lower = q.toLowerCase();
  return SessionLocal.getStore().filter(
    (n) =>
      n.title.toLowerCase().includes(lower) ||
      n.body.toLowerCase().includes(lower)
  );
}

// UNUSED (demo): dead helper
export function _rowToObject(row: any[]): Record<string, any> {
  return { id: row[0], title: row[1], body: row[2] };
}
