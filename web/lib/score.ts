/**
 * Pure scoring function for the public-signals-v1 subset.
 *
 * The hosted endpoint cannot clone arbitrary repos, so it computes a subset of
 * eight binary signals from public GitHub + PyPI metadata. Each signal carries
 * equal weight (1 of 8). The resulting percentage is mapped to a letter grade
 * using the same thresholds as the CLI grader (see src/grader.py).
 */

export const SUBSET_VERSION = "public-signals-v1";

export type Grade = "A" | "B" | "C" | "D" | "F";

export interface Signals {
  readme_has_json: boolean;
  readme_substantial: boolean;
  changelog_exists: boolean;
  license_exists: boolean;
  ci_present: boolean;
  pyproject_has_scripts: boolean;
  pypi_recently_released: boolean;
  py_typed_marker: boolean;
}

export interface ScoreResult {
  score: number;
  grade: Grade;
  signals: Signals;
}

export interface RepoInputs {
  // Tree listing of the default branch root (paths only).
  rootPaths: string[];
  // Tree listing of .github/workflows (paths only).
  workflowPaths: string[];
  // Decoded README content (utf-8) or null if missing.
  readme: string | null;
  // Decoded pyproject.toml content or null if missing.
  pyproject: string | null;
  // PyPI JSON release payload or null if no published package.
  pypi: PyPiPayload | null;
  // Default branch tree paths — used to look for py.typed anywhere under src/.
  allPaths: string[];
}

export interface PyPiPayload {
  // upload_time_iso_8601 of the latest non-yanked release, e.g. "2026-04-22T12:00:00.000000Z".
  latestUploadIso: string | null;
}

const README_SUBSTANTIAL_CHARS = 1500;
const PYPI_RECENT_DAYS = 180;

export function gradeLetter(score: number): Grade {
  if (score >= 90) return "A";
  if (score >= 75) return "B";
  if (score >= 60) return "C";
  if (score >= 40) return "D";
  return "F";
}

export function gradeColor(grade: Grade): string {
  switch (grade) {
    case "A":
      return "brightgreen";
    case "B":
      return "green";
    case "C":
      return "yellowgreen";
    case "D":
      return "orange";
    case "F":
      return "red";
  }
}

export function deriveSignals(inputs: RepoInputs, now: Date = new Date()): Signals {
  const rootSet = new Set(inputs.rootPaths.map((p) => p.toLowerCase()));
  const allSet = new Set(inputs.allPaths.map((p) => p.toLowerCase()));

  const readme = inputs.readme ?? "";
  const readmeLower = readme.toLowerCase();

  return {
    readme_has_json: readme.length > 0 && readmeLower.includes("--json"),
    readme_substantial: readme.length >= README_SUBSTANTIAL_CHARS,
    changelog_exists:
      rootSet.has("changelog.md") ||
      rootSet.has("changelog") ||
      rootSet.has("changes.md") ||
      rootSet.has("history.md"),
    license_exists:
      rootSet.has("license") ||
      rootSet.has("license.md") ||
      rootSet.has("license.txt") ||
      rootSet.has("licence") ||
      rootSet.has("copying"),
    ci_present: inputs.workflowPaths.some((p) => /\.ya?ml$/i.test(p)),
    pyproject_has_scripts: pyprojectHasScripts(inputs.pyproject),
    pypi_recently_released: pypiRecent(inputs.pypi, now),
    py_typed_marker: [...allSet].some((p) => p === "py.typed" || p.endsWith("/py.typed")),
  };
}

export function scoreFromSignals(signals: Signals): ScoreResult {
  const keys = Object.keys(signals) as (keyof Signals)[];
  const passed = keys.reduce((acc, k) => acc + (signals[k] ? 1 : 0), 0);
  const score = Math.round((passed / keys.length) * 100);
  return { score, grade: gradeLetter(score), signals };
}

export function score(inputs: RepoInputs, now: Date = new Date()): ScoreResult {
  return scoreFromSignals(deriveSignals(inputs, now));
}

function pyprojectHasScripts(pyproject: string | null): boolean {
  if (!pyproject) return false;
  // Avoid pulling in a TOML parser for one boolean. The CLI grader checks the
  // same condition by reading [project.scripts]; a substring match is enough
  // because TOML section headers are unambiguous.
  return /\[project\.scripts\]/.test(pyproject);
}

function pypiRecent(pypi: PyPiPayload | null, now: Date): boolean {
  if (!pypi || !pypi.latestUploadIso) return false;
  const uploaded = Date.parse(pypi.latestUploadIso);
  if (Number.isNaN(uploaded)) return false;
  const ageMs = now.getTime() - uploaded;
  const ageDays = ageMs / (1000 * 60 * 60 * 24);
  return ageDays <= PYPI_RECENT_DAYS;
}
