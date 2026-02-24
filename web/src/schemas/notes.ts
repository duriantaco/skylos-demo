// web/src/schemas/notes.ts

export interface NoteCreate {
  title: string;
  body: string;
}

export interface NoteOut {
  id: number;
  title: string;
  body: string;
}

// UNUSED (demo): never used schema
export interface NoteInternal {
  titleNorm: string;
}
