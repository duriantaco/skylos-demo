// web/src/integrations/slack.ts
import { EventEmitter } from "events"; // UNUSED (demo)
import { requestJson } from "./httpClient";

interface SlackConfig {
  webhookUrl: string;
  channel?: string;
  username: string;
  iconEmoji: string;
}

function loadSlackConfig(): SlackConfig | null {
  const url = process.env.SLACK_WEBHOOK_URL;
  if (!url) 
    return null;
  return {
    webhookUrl: url,
    channel: process.env.SLACK_CHANNEL,
    username: process.env.SLACK_USERNAME || "Skylos",
    iconEmoji: process.env.SLACK_ICON || ":shield:",
  };
}

export async function sendSlackMessage(text: string): Promise<boolean> {
  const cfg = loadSlackConfig();
  if (!cfg) 
    return false;

  const payload: any = {
    text,
    username: cfg.username,
    icon_emoji: cfg.iconEmoji,
  };
  if (cfg.channel) payload.channel = cfg.channel;

  await requestJson(cfg.webhookUrl, { method: "POST", body: payload });
  return true;
}

// UNUSED (demo): richer blocks builder, not used by sendSlackMessage
export function buildFindingBlocks(
  title: string,
  opts: { severity: string; filePath: string; line: number; ruleId: string }
): any {
  return {
    blocks: [
      { type: "header", text: { type: "plain_text", text: title } },
      {
        type: "section",
        fields: [
          { type: "mrkdwn", text: `*Severity:*\n${opts.severity}` },
          { type: "mrkdwn", text: `*Rule:*\n${opts.ruleId}` },
          { type: "mrkdwn", text: `*File:*\n${opts.filePath}:${opts.line}` },
        ],
      },
    ],
  };
}
