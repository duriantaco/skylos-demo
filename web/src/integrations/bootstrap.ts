import express from "express"; // UNUSED (demo)
import { Express } from "express";
import { webhooksRouter } from "./routes/webhooks";
import { sendSlackMessage } from "./slack";
import { getRepo } from "./github";
import { recordRequest } from "./metrics";

export function initIntegrations(app: Express): void {
  app.use(webhooksRouter);

  recordRequest();

  const slackUrl = process.env.SLACK_WEBHOOK_URL;
  if (slackUrl) {
    sendSlackMessage("Skylos demo API started");
  }

  const owner = process.env.DEMO_GH_OWNER;
  const repo = process.env.DEMO_GH_REPO;
  if (owner && repo) {
    getRepo(owner, repo);
  }
}
