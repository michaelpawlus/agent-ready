/**
 * Minimal GitHub Contents/Repos API client.
 *
 * Anonymous by default. If GITHUB_TOKEN is set in the Vercel environment, it is
 * sent as a Bearer token to lift the per-IP 60 req/hr rate limit.
 */

export interface RepoMeta {
  defaultBranch: string;
}

export interface RepoSnapshot {
  meta: RepoMeta;
  rootPaths: string[];
  allPaths: string[];
  workflowPaths: string[];
  readme: string | null;
  pyproject: string | null;
}

export class GitHubError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = "GitHubError";
  }
}

const API_BASE = "https://api.github.com";

function authHeaders(): HeadersInit {
  const token = process.env.GITHUB_TOKEN;
  const headers: Record<string, string> = {
    Accept: "application/vnd.github+json",
    "User-Agent": "agent-ready-badge",
    "X-GitHub-Api-Version": "2022-11-28",
  };
  if (token) headers.Authorization = `Bearer ${token}`;
  return headers;
}

async function ghFetch(path: string): Promise<Response> {
  const res = await fetch(`${API_BASE}${path}`, { headers: authHeaders() });
  return res;
}

export async function fetchRepoSnapshot(owner: string, repo: string): Promise<RepoSnapshot> {
  const repoRes = await ghFetch(`/repos/${owner}/${repo}`);
  if (repoRes.status === 404) throw new GitHubError(404, "repo not found");
  if (repoRes.status === 403) throw new GitHubError(403, "github rate limit");
  if (!repoRes.ok) throw new GitHubError(repoRes.status, `github error ${repoRes.status}`);
  const repoJson = (await repoRes.json()) as { default_branch?: string };
  const defaultBranch = repoJson.default_branch || "main";

  const treeRes = await ghFetch(`/repos/${owner}/${repo}/git/trees/${defaultBranch}?recursive=1`);
  if (!treeRes.ok) throw new GitHubError(treeRes.status, `github tree error ${treeRes.status}`);
  const treeJson = (await treeRes.json()) as {
    tree?: Array<{ path: string; type: string }>;
    truncated?: boolean;
  };
  const all = (treeJson.tree ?? []).filter((n) => n.type === "blob").map((n) => n.path);

  const rootPaths = all.filter((p) => !p.includes("/"));
  const workflowPaths = all.filter((p) => p.startsWith(".github/workflows/"));

  const readme = await fetchTextIfPresent(owner, repo, defaultBranch, all, [
    "README.md",
    "README.rst",
    "README.txt",
    "README",
  ]);
  const pyproject = await fetchTextIfPresent(owner, repo, defaultBranch, all, ["pyproject.toml"]);

  return {
    meta: { defaultBranch },
    rootPaths,
    allPaths: all,
    workflowPaths,
    readme,
    pyproject,
  };
}

async function fetchTextIfPresent(
  owner: string,
  repo: string,
  branch: string,
  allPaths: string[],
  candidates: string[],
): Promise<string | null> {
  for (const candidate of candidates) {
    if (!allPaths.includes(candidate)) continue;
    const raw = `https://raw.githubusercontent.com/${owner}/${repo}/${branch}/${candidate}`;
    const res = await fetch(raw, { headers: { "User-Agent": "agent-ready-badge" } });
    if (res.ok) return await res.text();
  }
  return null;
}
