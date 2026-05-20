import { describe, expect, it } from "vitest";

import {
  SUBSET_VERSION,
  deriveSignals,
  gradeColor,
  gradeLetter,
  scoreFromSignals,
} from "./score.js";

const PERFECT_INPUTS = {
  rootPaths: [
    "README.md",
    "CHANGELOG.md",
    "LICENSE",
    "pyproject.toml",
    "src",
    ".github",
  ],
  workflowPaths: [".github/workflows/ci.yml"],
  readme:
    "# project\n\nA CLI with `--json` output.\n\n" +
    "This README is intentionally long so that the substantial-length signal trips. ".repeat(50),
  pyproject: "[project]\nname = \"project\"\n\n[project.scripts]\nproject = \"src.cli:app\"\n",
  pypi: { latestUploadIso: "2026-05-01T12:00:00.000000Z" },
  allPaths: ["src/py.typed", "src/__init__.py"],
};

const NOW = new Date("2026-05-19T00:00:00.000Z");

describe("gradeLetter", () => {
  it.each([
    [100, "A"],
    [90, "A"],
    [89, "B"],
    [75, "B"],
    [60, "C"],
    [40, "D"],
    [39, "F"],
    [0, "F"],
  ])("maps %i -> %s", (score, expected) => {
    expect(gradeLetter(score)).toBe(expected);
  });
});

describe("gradeColor", () => {
  it("returns brightgreen for A", () => {
    expect(gradeColor("A")).toBe("brightgreen");
  });
  it("returns red for F", () => {
    expect(gradeColor("F")).toBe("red");
  });
});

describe("deriveSignals — perfect inputs", () => {
  it("trips every signal", () => {
    const s = deriveSignals(PERFECT_INPUTS, NOW);
    expect(s).toEqual({
      readme_has_json: true,
      readme_substantial: true,
      changelog_exists: true,
      license_exists: true,
      ci_present: true,
      pyproject_has_scripts: true,
      pypi_recently_released: true,
      py_typed_marker: true,
    });
  });

  it("scores 100 / A", () => {
    const r = scoreFromSignals(deriveSignals(PERFECT_INPUTS, NOW));
    expect(r.score).toBe(100);
    expect(r.grade).toBe("A");
  });
});

describe("deriveSignals — individual signal fails", () => {
  it("readme_has_json: false when README lacks --json", () => {
    const s = deriveSignals({ ...PERFECT_INPUTS, readme: "# project\nnothing about output" }, NOW);
    expect(s.readme_has_json).toBe(false);
  });

  it("readme_substantial: false for short READMEs", () => {
    const s = deriveSignals({ ...PERFECT_INPUTS, readme: "# project --json" }, NOW);
    expect(s.readme_substantial).toBe(false);
  });

  it("readme_has_json: false when README is null", () => {
    const s = deriveSignals({ ...PERFECT_INPUTS, readme: null }, NOW);
    expect(s.readme_has_json).toBe(false);
    expect(s.readme_substantial).toBe(false);
  });

  it("changelog_exists: matches CHANGELOG or CHANGELOG.md", () => {
    expect(deriveSignals({ ...PERFECT_INPUTS, rootPaths: ["CHANGELOG"] }, NOW).changelog_exists).toBe(true);
    expect(deriveSignals({ ...PERFECT_INPUTS, rootPaths: [] }, NOW).changelog_exists).toBe(false);
  });

  it("license_exists: matches LICENSE, LICENSE.md, LICENCE", () => {
    expect(deriveSignals({ ...PERFECT_INPUTS, rootPaths: ["LICENCE"] }, NOW).license_exists).toBe(true);
    expect(deriveSignals({ ...PERFECT_INPUTS, rootPaths: [] }, NOW).license_exists).toBe(false);
  });

  it("ci_present: false when no workflow yaml", () => {
    expect(deriveSignals({ ...PERFECT_INPUTS, workflowPaths: [] }, NOW).ci_present).toBe(false);
    expect(
      deriveSignals(
        { ...PERFECT_INPUTS, workflowPaths: [".github/workflows/README.md"] },
        NOW,
      ).ci_present,
    ).toBe(false);
  });

  it("pyproject_has_scripts: false when no [project.scripts] section", () => {
    expect(
      deriveSignals(
        { ...PERFECT_INPUTS, pyproject: "[project]\nname = \"x\"\n" },
        NOW,
      ).pyproject_has_scripts,
    ).toBe(false);
    expect(
      deriveSignals({ ...PERFECT_INPUTS, pyproject: null }, NOW).pyproject_has_scripts,
    ).toBe(false);
  });

  it("pypi_recently_released: false for stale or missing releases", () => {
    expect(
      deriveSignals(
        { ...PERFECT_INPUTS, pypi: { latestUploadIso: "2024-01-01T00:00:00Z" } },
        NOW,
      ).pypi_recently_released,
    ).toBe(false);
    expect(deriveSignals({ ...PERFECT_INPUTS, pypi: null }, NOW).pypi_recently_released).toBe(false);
    expect(
      deriveSignals(
        { ...PERFECT_INPUTS, pypi: { latestUploadIso: null } },
        NOW,
      ).pypi_recently_released,
    ).toBe(false);
  });

  it("py_typed_marker: matches src/py.typed or top-level py.typed", () => {
    expect(deriveSignals({ ...PERFECT_INPUTS, allPaths: ["py.typed"] }, NOW).py_typed_marker).toBe(true);
    expect(
      deriveSignals({ ...PERFECT_INPUTS, allPaths: ["src/pkg/py.typed"] }, NOW).py_typed_marker,
    ).toBe(true);
    expect(deriveSignals({ ...PERFECT_INPUTS, allPaths: ["src/foo.py"] }, NOW).py_typed_marker).toBe(false);
  });
});

describe("scoreFromSignals — score bucketing", () => {
  it("8/8 = 100 A", () => {
    const r = scoreFromSignals(deriveSignals(PERFECT_INPUTS, NOW));
    expect(r.score).toBe(100);
    expect(r.grade).toBe("A");
  });

  it("0/8 = 0 F", () => {
    const r = scoreFromSignals(
      deriveSignals(
        {
          rootPaths: [],
          workflowPaths: [],
          readme: null,
          pyproject: null,
          pypi: null,
          allPaths: [],
        },
        NOW,
      ),
    );
    expect(r.score).toBe(0);
    expect(r.grade).toBe("F");
  });

  it("4/8 = 50 D", () => {
    const r = scoreFromSignals({
      readme_has_json: true,
      readme_substantial: true,
      changelog_exists: true,
      license_exists: true,
      ci_present: false,
      pyproject_has_scripts: false,
      pypi_recently_released: false,
      py_typed_marker: false,
    });
    expect(r.score).toBe(50);
    expect(r.grade).toBe("D");
  });
});

describe("constants", () => {
  it("subset is public-signals-v1", () => {
    expect(SUBSET_VERSION).toBe("public-signals-v1");
  });
});
