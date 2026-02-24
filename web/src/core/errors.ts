// was: helper for 404 responses, replaced by inline throw in routes
export function notFound(entity: string): Error { // UNUSED (demo)
  const err = new Error(`${entity} not found`);
  (err as any).statusCode = 404;
  return err;
}

// UNUSED (demo): not used anywhere
export class DemoError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "DemoError";
  }
}
