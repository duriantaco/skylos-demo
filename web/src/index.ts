// web/src/index.ts
import express from "express";
import { configureLogging } from "./logging";
import { loadConfig } from "./config";
import { initDb } from "./db/session";
import { healthRouter, notesRouter, reportsRouter } from "./routes";
import { initIntegrations } from "./integrations/bootstrap";
import { runExport } from "./services/exportService";
import { dispatch } from "./handlers";
import { getHandler } from "./core/registry";
import { search } from "./services/reportService";

// UNUSED (demo): not used anywhere in runtime
export const APP_DISPLAY_NAME = "Skylos Demo API";

export function createApp(): express.Express {
  configureLogging();

  const app = express();
  app.use(express.json());

  app.use(healthRouter);
  app.use(notesRouter);
  app.use(reportsRouter);

  initIntegrations(app);
  initDb();

  // Force dynamic dispatch modules to be loaded
  void runExport;
  void dispatch;
  void getHandler;
  void search;

  return app;
}

const config = loadConfig();
export const app = createApp();

if (require.main === module) {
  app.listen(config.port, () => {
    console.log(`Server running on port ${config.port}`);
  });
}
