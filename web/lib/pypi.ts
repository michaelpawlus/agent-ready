/**
 * PyPI JSON API client. Returns the latest release upload time or null if the
 * package is not published.
 */

import type { PyPiPayload } from "./score.js";

export async function fetchPyPi(name: string): Promise<PyPiPayload | null> {
  const res = await fetch(`https://pypi.org/pypi/${encodeURIComponent(name)}/json`, {
    headers: { "User-Agent": "agent-ready-badge", Accept: "application/json" },
  });
  if (res.status === 404) return null;
  if (!res.ok) return null;
  const json = (await res.json()) as {
    urls?: Array<{ upload_time_iso_8601?: string; yanked?: boolean }>;
  };
  const urls = (json.urls ?? []).filter((u) => !u.yanked);
  if (urls.length === 0) return { latestUploadIso: null };
  // PyPI returns one urls entry per artifact for the latest version; any of
  // them carries the upload time for that release.
  const iso = urls[0].upload_time_iso_8601 ?? null;
  return { latestUploadIso: iso };
}

/**
 * Best-effort package-name guess from pyproject contents. Falls back to the
 * GitHub repo name.
 */
export function pypiNameFromPyproject(pyproject: string | null, fallback: string): string {
  if (!pyproject) return fallback;
  const m = pyproject.match(/^\s*name\s*=\s*["']([^"']+)["']/m);
  return m ? m[1] : fallback;
}
