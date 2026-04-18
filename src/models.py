"""Shared dataclasses."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Repo:
    path: Path
    name: str
    pyproject: dict | None = None
    claude_md_text: str | None = None
    readme_text: str | None = None
    cli_files: list[Path] = field(default_factory=list)
    config: "RepoConfig | None" = None


@dataclass
class RepoConfig:
    disabled_checks: list[str] = field(default_factory=list)
    weight_overrides: dict[str, int] = field(default_factory=dict)
    ignore_paths: list[str] = field(default_factory=list)


@dataclass
class CheckResult:
    check_id: str
    category: str
    weight: int
    passing: bool
    evidence: str
    has_fix_template: bool = False


@dataclass
class CategoryScore:
    name: str
    score: int
    weight: int
    checks: int
    passing: int


@dataclass
class ScoreCard:
    path: Path
    name: str
    score: int
    grade: str
    categories: dict[str, CategoryScore]
    results: list[CheckResult]

    @property
    def failing(self) -> list[CheckResult]:
        return [r for r in self.results if not r.passing]


@dataclass
class FileEdit:
    path: str  # repo-relative
    original: str  # empty string if creating new file
    updated: str

    @property
    def is_new(self) -> bool:
        return self.original == ""


@dataclass
class FixProposal:
    check_id: str
    summary: str
    edits: list[FileEdit]
