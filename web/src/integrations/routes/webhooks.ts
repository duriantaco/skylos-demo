import { Router, Request, Response } from "express";
import { verifyHmacSha256 } from "../webhookSigning";
import { recordRequest, recordLatencyMs } from "../metrics";

export const webhooksRouter = Router();

export function demoWebhook(req: Request, res: Response): void {
  const t0 = Date.now();
  recordRequest();

  const secret = process.env.WEBHOOK_SECRET || "dev-secret";
  const sig = req.headers["x-signature"] as string | undefined;
  const body = Buffer.from(JSON.stringify(req.body));

  if (!verifyHmacSha256(secret, body, sig)) {
    res.status(401).json({ error: "Invalid signature" });
    return;
  }

  recordLatencyMs(Date.now() - t0);
  res.json({ ok: true });
}

webhooksRouter.post("/integrations/webhooks/demo", demoWebhook);
