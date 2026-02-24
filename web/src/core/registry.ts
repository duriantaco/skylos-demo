const _REGISTRY: Record<string, new () => RegisteredHandler> = {};

export function RegisterHandler(name: string) {
  return function <T extends new (...args: any[]) => RegisteredHandler>(constructor: T) {
    _REGISTRY[name] = constructor;
    return constructor;
  };
}

export abstract class RegisteredHandler {
  abstract execute(): void;
}

@RegisterHandler("email")
export class EmailHandler extends RegisteredHandler {
  execute(): void {
    console.log("Sending email notification...");
  }
}

@RegisterHandler("slack")
export class SlackAlertHandler extends RegisteredHandler {
  execute(): void {
    console.log("Posting alert to Slack...");
  }
}

export function getHandler(name: string): RegisteredHandler {
  const cls = _REGISTRY[name];
  if (!cls) {
    throw new Error(`No handler registered for: ${name}`);
  }
  return new cls();
}
