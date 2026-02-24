// web/src/integrations/httpClient.ts
import http from "http";

export interface HttpRetryPolicy {
  maxAttempts: number;
  baseBackoffMs: number;
  maxBackoffMs: number;
  retryOnStatus: number[];
}

const defaultPolicy: HttpRetryPolicy = {
  maxAttempts: 3,
  baseBackoffMs: 200,
  maxBackoffMs: 2000,
  retryOnStatus: [429, 500, 502, 503, 504],
};

// UNUSED (demo): unused constant
export const DEFAULT_HEADERS: Record<string, string> = {
  "User-Agent": "skylos-demo/0.1",
};

// NOTE: re-exported in index.ts but never actually consumed anywhere
export function getHttpClient(): typeof http { // UNUSED (demo)
  return http;
}

export async function requestJson(
  url: string,
  options: { method?: string; body?: any; retry?: Partial<HttpRetryPolicy> } = {}
): Promise<any> {
  const policy = { ...defaultPolicy, ...options.retry };
  let lastError: Error | null = null;

  for (let attempt = 0; attempt < policy.maxAttempts; attempt++) {
    try {
      const resp = await fetch(url, {
        method: options.method || "GET",
        headers: { "Content-Type": "application/json" },
        body: options.body ? JSON.stringify(options.body) : undefined,
      });
      if (policy.retryOnStatus.includes(resp.status)) {
        await new Promise((r) => setTimeout(r, policy.baseBackoffMs * 2 ** attempt));
        continue;
      }
      return await resp.json();
    } catch (e) {
      lastError = e as Error;
      await new Promise((r) => setTimeout(r, policy.baseBackoffMs * 2 ** attempt));
    }
  }
  throw new Error(`requestJson failed after ${policy.maxAttempts} attempts: ${lastError?.message}`);
}

// UNUSED (demo): dead helper for text responses, never called
export async function requestText(
  url: string,
  options: { method?: string; body?: any } = {}
): Promise<string> {
  const resp = await fetch(url, {
    method: options.method || "GET",
    body: options.body ? JSON.stringify(options.body) : undefined,
  });
  return await resp.text();
}
