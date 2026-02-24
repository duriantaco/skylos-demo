// web/src/handlers/index.ts

export function handleCreate(payload: any): any {
  return { action: "created", data: payload };
}

export function handleUpdate(payload: any): any {
  return { action: "updated", data: payload };
}

export function handleDelete(payload: any): any {
  return { action: "deleted", data: payload };
}

const HANDLER_MAP: Record<string, Function> = {
  create: handleCreate,
  update: handleUpdate,
  delete: handleDelete,
};

export function dispatch(action: string, payload: any): any {
  const handler = HANDLER_MAP[action];
  if (!handler) {
    throw new Error(`Unknown action: ${action}`);
  }
  return handler(payload);
}
