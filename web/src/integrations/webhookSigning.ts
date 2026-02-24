// web/src/integrations/webhookSigning.ts
import crypto from "crypto";

function safeStrEq(a: string, b: string): boolean {
  const bufA = Buffer.from(a, "utf-8");
  const bufB = Buffer.from(b, "utf-8");
  if (bufA.length !== bufB.length) 
    return false;
  return crypto.timingSafeEqual(bufA, bufB);
}

export function signHmacSha256(secret: string, body: Buffer): string {
  return crypto.createHmac("sha256", secret).update(body).digest("hex");
}

export function verifyHmacSha256(secret: string, body: Buffer, signature: string | undefined): boolean {
  if (!signature) 
    return false;
  const expected = signHmacSha256(secret, body);
  return safeStrEq(expected, signature);
}

// UNUSED (demo): alternative signature format, not referenced anywhere
export function verifyHmacSha256Prefixed(
  secret: string,
  body: Buffer,
  signature: string | undefined,
  prefix: string = "sha256="
): boolean {
  if (!signature || !signature.startsWith(prefix)) 
    return false;
  return verifyHmacSha256(secret, body, signature.slice(prefix.length));
}
