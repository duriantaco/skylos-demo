// web/src/config.ts

export interface Settings {
  databaseUrl: string;
  apiKey: string;
  port: number;
}

export function loadConfig(): Settings {
  return {
    databaseUrl: process.env.DATABASE_URL || "sqlite:///./demo.db",
    apiKey: process.env.API_KEY || "dev-key",
    port: parseInt(process.env.PORT || "3000", 10),
  };
}

// UNUSED (demo)
export function _isProd(): boolean {
  return loadConfig().apiKey !== "dev-key";
}
