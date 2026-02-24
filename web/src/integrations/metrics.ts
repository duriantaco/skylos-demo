// web/src/integrations/metrics.ts

class Counter {
  name: string;
  value: number = 0;

  constructor(name: string) {
    this.name = name;
  }

  inc(n: number = 1): void {
    this.value += n;
  }
}

class Timer {
  name: string;
  durationMs: number = 0;

  constructor(name: string) {
    this.name = name;
  }
}

const METRICS_ENABLED = (process.env.METRICS_ENABLED || "false").toLowerCase() === "true";

function _shouldEmit(): boolean {
  return METRICS_ENABLED;
}

const _requestCount = new Counter("http_requests_total");
const _latencyTimer = new Timer("http_request_latency_ms");

// UNUSED (demo): never read, looks realistic
export const _queueDepth = new Counter("jobs_queue_depth");

export function recordRequest(): void {
  if (!_shouldEmit()) return;
  _requestCount.inc(1);
}

export function recordLatencyMs(ms: number): void {
  if (!_shouldEmit()) return;
  _latencyTimer.durationMs = ms;
}

// was: intended for /admin/metrics endpoint, never wired up
export function snapshotMetrics(): Record<string, number> | null { // UNUSED (demo)
  if (!_shouldEmit()) return null;
  return {
    [_requestCount.name]: _requestCount.value,
    [_latencyTimer.name]: _latencyTimer.durationMs,
  };
}

// UNUSED (demo): context manager exists but no one uses it
export function timedRequest(name: string = "http"): Timer {
  return new Timer(name);
}
