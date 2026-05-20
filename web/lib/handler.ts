/**
 * Shared request handling for the badge endpoint. The Vercel function entry
 * point in api/badge.ts delegates here; tests exercise this module directly.
 */

import { fetchRepoSnapshot, GitHubError, type RepoSnapshot } from "./github.js";
import { fetchPyPi, pypiNameFromPyproject } from "./pypi.js";
import {
  SUBSET_VERSION,
  deriveSignals,
  gradeColor,
  scoreFromSignals,
  type ScoreResult,
} from "./score.js";

const SLUG_RE = /^[A-Za-z0-9._-]{1,100}$/;

export interface BadgeRequest {
  owner: string;
  repo: string;
  format: "svg" | "json";
}

export interface ParsedQuery {
  owner?: string | string[];
  repo?: string | string[];
  format?: string | string[];
}

export type BadgeResponse =
  | { kind: "redirect"; status: 302; location: string }
  | { kind: "svg-fallback"; status: number; svg: string }
  | { kind: "json"; status: number; body: unknown }
  | { kind: "error"; status: number; body: { error: string; code: number } };

export function parseRequest(query: ParsedQuery): BadgeRequest | { error: string } {
  const owner = firstString(query.owner);
  const repo = firstString(query.repo);
  const format = firstString(query.format) ?? "svg";
  if (!owner || !repo) return { error: "owner and repo required" };
  if (!SLUG_RE.test(owner) || !SLUG_RE.test(repo)) {
    return { error: "invalid owner/repo" };
  }
  if (format !== "svg" && format !== "json") return { error: "format must be svg or json" };
  return { owner, repo, format };
}

export async function loadAndScore(
  owner: string,
  repo: string,
  fetchers: Fetchers = defaultFetchers,
  now: Date = new Date(),
): Promise<ScoreResult> {
  const snapshot = await fetchers.github(owner, repo);
  const pkgName = pypiNameFromPyproject(snapshot.pyproject, repo);
  const pypi = await fetchers.pypi(pkgName);
  const signals = deriveSignals(
    {
      rootPaths: snapshot.rootPaths,
      allPaths: snapshot.allPaths,
      workflowPaths: snapshot.workflowPaths,
      readme: snapshot.readme,
      pyproject: snapshot.pyproject,
      pypi,
    },
    now,
  );
  return scoreFromSignals(signals);
}

export interface Fetchers {
  github: (owner: string, repo: string) => Promise<RepoSnapshot>;
  pypi: (name: string) => Promise<Awaited<ReturnType<typeof fetchPyPi>>>;
}

export const defaultFetchers: Fetchers = {
  github: fetchRepoSnapshot,
  pypi: fetchPyPi,
};

export function shieldsUrl(grade: ScoreResult["grade"]): string {
  const color = gradeColor(grade);
  return `https://img.shields.io/badge/agent--ready-${grade}-${color}`;
}

export function unknownShieldsUrl(): string {
  return "https://img.shields.io/badge/agent--ready-unknown-lightgrey";
}

export function jsonBody(owner: string, repo: string, result: ScoreResult, now: Date): unknown {
  return {
    owner,
    repo,
    score: result.score,
    grade: result.grade,
    signals: result.signals,
    scored_at: now.toISOString(),
    subset: SUBSET_VERSION,
    cli_link: "https://pypi.org/project/agent-ready/",
  };
}

export async function handleBadge(
  query: ParsedQuery,
  fetchers: Fetchers = defaultFetchers,
  now: Date = new Date(),
): Promise<BadgeResponse> {
  const parsed = parseRequest(query);
  if ("error" in parsed) {
    if (firstString(query.format) === "json") {
      return { kind: "error", status: 400, body: { error: parsed.error, code: 1 } };
    }
    return { kind: "redirect", status: 302, location: unknownShieldsUrl() };
  }
  const { owner, repo, format } = parsed;

  try {
    const result = await loadAndScore(owner, repo, fetchers, now);
    if (format === "json") {
      return { kind: "json", status: 200, body: jsonBody(owner, repo, result, now) };
    }
    return { kind: "redirect", status: 302, location: shieldsUrl(result.grade) };
  } catch (err) {
    if (err instanceof GitHubError) {
      if (format === "json") {
        return {
          kind: "error",
          status: err.status === 404 ? 404 : 503,
          body: { error: err.message, code: err.status === 404 ? 2 : 1 },
        };
      }
      return { kind: "redirect", status: 302, location: unknownShieldsUrl() };
    }
    if (format === "json") {
      return { kind: "error", status: 503, body: { error: "scoring failed", code: 1 } };
    }
    return { kind: "redirect", status: 302, location: unknownShieldsUrl() };
  }
}

function firstString(v: string | string[] | undefined): string | undefined {
  if (Array.isArray(v)) return v[0];
  return v;
}
