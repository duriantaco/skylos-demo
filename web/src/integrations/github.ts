import { requestJson } from "./httpClient";

interface GitHubConfig {
  token: string;
  apiBase: string;
}

function loadGitHubConfig(): GitHubConfig | null {
  const tok = process.env.GITHUB_TOKEN;
  if (!tok) 
    return null;
  return {
    token: tok,
    apiBase: process.env.GITHUB_API_BASE || "https://api.github.com",
  };
}

// was intended for authenticated requests, never wired in
function authHeaders(cfg: GitHubConfig): Record<string, string> { // UNUSED (demo)
  return {
    Authorization: `Bearer ${cfg.token}`,
    Accept: "application/vnd.github+json",
  };
}

export async function getRepo(owner: string, repo: string): Promise<any | null> {
  const cfg = loadGitHubConfig();
  if (!cfg) return null;
  return requestJson(`${cfg.apiBase}/repos/${owner}/${repo}`, {
    method: "GET",
  });
}

// UNUSED (demo): helper for checking if an issue exists, never called
export async function findIssueByTitle(
  owner: string,
  repo: string,
  title: string
): Promise<number | null> {
  const cfg = loadGitHubConfig();
  if (!cfg) 
    return null;
  const data = await requestJson(`${cfg.apiBase}/repos/${owner}/${repo}/issues`);
  const items = Array.isArray(data) ? data : data?.items;
  if (!Array.isArray(items)) 
    return null;
  for (const it of items) {
    if (it?.title === title && typeof it?.number === "number") {
      return it.number;
    }
  }
  return null;
}
