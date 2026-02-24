// web/src/types/index.ts

// was: planned config schema, never used — Settings in config.ts is used instead
export interface AppConfig { // UNUSED (demo)
  port: number;
  env: string;
  apiKey: string;
  databaseUrl: string;
}

// TODO: wire into middleware once request tracing is enabled
export interface RequestContext { // UNUSED (demo)
  requestId: string;
  timestamp: number;
  actor?: string;
}

// UNUSED (demo): not referenced anywhere
export interface PaginationParams {
  page: number;
  pageSize: number;
  sortBy?: string;
}
