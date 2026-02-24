// web/src/routes/notes.ts
import { Router, Request, Response } from "express";
import { URL } from "url"; // UNUSED (demo)
import { requireApiKey } from "../middleware/auth";
import { createNoteService, listNotesService, searchNotesService } from "../services/noteService";

export const notesRouter = Router();

notesRouter.post("/notes", requireApiKey, (req: Request, res: Response) => {
  const note = createNoteService(req.body);
  res.status(201).json(note);
});

notesRouter.get("/notes", requireApiKey, (_req: Request, res: Response) => {
  res.json(listNotesService());
});

notesRouter.get("/notes/search", requireApiKey, (req: Request, res: Response) => {
  const q = req.query.q as string;
  if (!q || q.length < 1 || q.length > 200) {
    res.status(400).json({ error: "Invalid query" });
    return;
  }
  res.json(searchNotesService(q));
});

// UNUSED (demo): unused endpoint helper
export function _normalizeQuery(q: string): string {
  return q.trim().toLowerCase();
}
