// web/src/services/noteService.ts
import { createNote, listNotes, searchNotes } from "../db/crud";
import { NoteCreate } from "../schemas/notes";
import { Note } from "../db/models";

export function createNoteService(payload: NoteCreate): Note {
  return createNote(payload);
}

export function listNotesService(): Note[] {
  return listNotes();
}

export function searchNotesService(q: string): Note[] {
  return searchNotes(q.trim());
}

// UNUSED (demo): business helper never called
export function _validateTitle(title: string): void {
  if (!title.trim()) {
    throw new Error("title empty");
  }
}
