import { Note } from "./models";

const store: Note[] = [];
let nextId = 1;

export const SessionLocal = {
  getStore(): Note[] {
    return store;
  },
  nextId(): number {
    return nextId++;
  },
};

export function initDb(): void {
  store.length = 0;
  nextId = 1;
  console.log("Database initialized");
}

// UNUSED (demo): not used
export function _dropAll(): void {
  store.length = 0;
  nextId = 1;
}
