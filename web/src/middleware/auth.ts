import { Request, Response, NextFunction } from "express";
import { loadConfig } from "../config"; // UNUSED (demo): not used

export function requireApiKey(req: Request, res: Response, next: NextFunction): void {
  const apiKey = req.headers["x-api-key"];
  if (apiKey !== "dev-key") {
    res.status(401).json({ error: "Invalid API key" });
    return;
  }
  next();
}

// UNUSED (demo): never used middleware
export function getActorFromHeaders(req: Request): string {
  return (req.headers["x-actor"] as string) || "unknown";
}
