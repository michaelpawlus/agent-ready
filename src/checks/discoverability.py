"""Discoverability checks: can an agent find the surface?"""

from __future__ import annotations

from ..models import Repo
from .base import Check


def _claude_md(repo: Repo) -> tuple[bool, str]:
    path = repo.path / "CLAUDE.md"
    if path.exists():
        return True, f"CLAUDE.md found at {path.name}"
    return False, "CLAUDE.md not found in repo root"


def _readme(repo: Repo) -> tuple[bool, str]:
    for name in ("README.md", "README.rst", "README.txt", "README"):
        if (repo.path / name).exists():
            return True, f"{name} found"
    return False, "No README.* at repo root"


def _skill_manifest(repo: Repo) -> tuple[bool, str]:
    candidates = [
        repo.path / ".claude" / "skill.json",
        repo.path / ".claude" / "skill.yml",
        repo.path / ".claude" / "skill.yaml",
        repo.path / "SKILL.md",
    ]
    for c in candidates:
        if c.exists():
            rel = c.relative_to(repo.path).as_posix()
            return True, f"Skill manifest found at {rel}"
    return False, "No .claude/skill.json or SKILL.md found"


CHECKS = [
    Check(
        id="discoverability.claude-md-present",
        category="discoverability",
        weight=3,
        title="CLAUDE.md present",
        description="A CLAUDE.md file at the repo root tells agents where to find instructions, CLI commands, and workflow notes.",
        remediation="Create a CLAUDE.md at the repo root with sections: CLI Commands, Running Tests, Agent Persona.",
        detect=_claude_md,
        has_fix_template=True,
    ),
    Check(
        id="discoverability.readme-present",
        category="discoverability",
        weight=2,
        title="README present",
        description="Agents look for a README.md to learn what the project does.",
        remediation="Add a README.md with a one-paragraph summary and Quick Start.",
        detect=_readme,
    ),
    Check(
        id="discoverability.skill-manifest-present",
        category="discoverability",
        weight=2,
        title="Skill manifest present",
        description="A .claude/skill.json (or SKILL.md) advertises the project as a callable skill with documented triggers and commands.",
        remediation="Create .claude/skill.json with name, description, triggers, and commands.",
        detect=_skill_manifest,
        has_fix_template=True,
    ),
]
