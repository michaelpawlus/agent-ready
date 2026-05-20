import { describe, expect, it } from "vitest";

import { handleBadge, parseRequest, shieldsUrl, unknownShieldsUrl } from "./handler.js";
import { GitHubError, type RepoSnapshot } from "./github.js";
import type { PyPiPayload } from "./score.js";

const PERFECT_SNAPSHOT: RepoSnapshot = {
  meta: { defaultBranch: "main" },
  rootPaths: ["README.md", "CHANGELOG.md", "LICENSE", "pyproject.toml"],
  allPaths: ["README.md", "CHANGELOG.md", "LICENSE", "pyproject.toml", "src/py.typed"],
  workflowPaths: [".github/workflows/ci.yml"],
  readme:
    "agent-ready supports --json on every command.\n\n" +
    "Long body. ".repeat(200),
  pyproject: "[project]\nname = \"agent-ready\"\n\n[project.scripts]\nx = \"a:b\"\n",
};

const PERFECT_PYPI: PyPiPayload = { latestUploadIso: "2026-05-01T00:00:00.000000Z" };
const NOW = new Date("2026-05-19T12:00:00.000Z");

function fetchers(snapshot: RepoSnapshot | Error, pypi: PyPiPayload | null) {
  return {
    github: async () => {
      if (snapshot instanceof Error) throw snapshot;
      return snapshot;
    },
    pypi: async () => pypi,
  };
}

describe("parseRequest", () => {
  it("accepts standard owner/repo", () => {
    const r = parseRequest({ owner: "michaelpawlus", repo: "agent-ready", format: "svg" });
    expect(r).toEqual({ owner: "michaelpawlus", repo: "agent-ready", format: "svg" });
  });

  it("defaults format to svg", () => {
    const r = parseRequest({ owner: "a", repo: "b" });
    expect("error" in r ? null : r.format).toBe("svg");
  });

  it("rejects path traversal", () => {
    const r = parseRequest({ owner: "../etc", repo: "x" });
    expect("error" in r).toBe(true);
  });

  it("rejects spaces", () => {
    const r = parseRequest({ owner: "foo bar", repo: "x" });
    expect("error" in r).toBe(true);
  });

  it("rejects unknown format", () => {
    const r = parseRequest({ owner: "a", repo: "b", format: "html" });
    expect("error" in r).toBe(true);
  });
});

describe("handleBadge — happy path", () => {
  it("svg → 302 to shields.io with A color", async () => {
    const res = await handleBadge(
      { owner: "michaelpawlus", repo: "agent-ready", format: "svg" },
      fetchers(PERFECT_SNAPSHOT, PERFECT_PYPI),
      NOW,
    );
    expect(res.kind).toBe("redirect");
    if (res.kind !== "redirect") throw new Error("unreachable");
    expect(res.status).toBe(302);
    expect(res.location).toBe(shieldsUrl("A"));
  });

  it("json → 200 with full scorecard", async () => {
    const res = await handleBadge(
      { owner: "michaelpawlus", repo: "agent-ready", format: "json" },
      fetchers(PERFECT_SNAPSHOT, PERFECT_PYPI),
      NOW,
    );
    expect(res.kind).toBe("json");
    if (res.kind !== "json") throw new Error("unreachable");
    expect(res.status).toBe(200);
    expect(res.body).toMatchObject({
      owner: "michaelpawlus",
      repo: "agent-ready",
      grade: "A",
      score: 100,
      subset: "public-signals-v1",
      cli_link: "https://pypi.org/project/agent-ready/",
    });
  });
});

describe("handleBadge — failure modes", () => {
  it("github 404 → svg fallback (302 grey)", async () => {
    const res = await handleBadge(
      { owner: "noone", repo: "nope", format: "svg" },
      fetchers(new GitHubError(404, "repo not found"), null),
      NOW,
    );
    expect(res.kind).toBe("redirect");
    if (res.kind !== "redirect") throw new Error("unreachable");
    expect(res.location).toBe(unknownShieldsUrl());
  });

  it("github 404 → json 404 with code=2", async () => {
    const res = await handleBadge(
      { owner: "noone", repo: "nope", format: "json" },
      fetchers(new GitHubError(404, "repo not found"), null),
      NOW,
    );
    expect(res.kind).toBe("error");
    if (res.kind !== "error") throw new Error("unreachable");
    expect(res.status).toBe(404);
    expect(res.body).toEqual({ error: "repo not found", code: 2 });
  });

  it("github 403 (rate limit) → json 503", async () => {
    const res = await handleBadge(
      { owner: "a", repo: "b", format: "json" },
      fetchers(new GitHubError(403, "github rate limit"), null),
      NOW,
    );
    expect(res.kind).toBe("error");
    if (res.kind !== "error") throw new Error("unreachable");
    expect(res.status).toBe(503);
  });

  it("invalid slug → svg fallback", async () => {
    const res = await handleBadge(
      { owner: "../etc", repo: "x", format: "svg" },
      fetchers(PERFECT_SNAPSHOT, PERFECT_PYPI),
      NOW,
    );
    expect(res.kind).toBe("redirect");
    if (res.kind !== "redirect") throw new Error("unreachable");
    expect(res.location).toBe(unknownShieldsUrl());
  });

  it("invalid slug + json → 400", async () => {
    const res = await handleBadge(
      { owner: "../etc", repo: "x", format: "json" },
      fetchers(PERFECT_SNAPSHOT, PERFECT_PYPI),
      NOW,
    );
    expect(res.kind).toBe("error");
    if (res.kind !== "error") throw new Error("unreachable");
    expect(res.status).toBe(400);
  });

  it("pypi missing → score still computes, just drops that signal", async () => {
    const res = await handleBadge(
      { owner: "michaelpawlus", repo: "agent-ready", format: "json" },
      fetchers(PERFECT_SNAPSHOT, null),
      NOW,
    );
    expect(res.kind).toBe("json");
    if (res.kind !== "json") throw new Error("unreachable");
    const body = res.body as { signals: { pypi_recently_released: boolean }; grade: string };
    expect(body.signals.pypi_recently_released).toBe(false);
    expect(body.grade).toBe("B"); // 7/8 = 88
  });
});
