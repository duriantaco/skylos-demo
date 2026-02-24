// web/src/utils/ids.ts
import crypto from "crypto";

export function newRequestId(): string {
  return crypto.randomUUID().replace(/-/g, "");
}

// UNUSED (demo)
export function slugify(s: string): string {
  return s.trim().toLowerCase().replace(/\s+/g, "-");
}

// UNUSED (demo)
export const DEFAULT_REQUEST_ID = "0000000000000000";
