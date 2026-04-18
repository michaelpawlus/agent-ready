"""Walk paths and load repo metadata for checks to consume."""

from __future__ import annotations

import tomllib
from fnmatch import fnmatch
from pathlib import Path

from . import config as config_mod
from .models import Repo


def load_repo(path: Path) -> Repo:
    """Load all static metadata a check might need from a repo."""
    path = path.resolve()
    cfg = config_mod.load(path)

    repo = Repo(path=path, name=path.name, config=cfg)

    pyproject_path = path / "pyproject.toml"
    if pyproject_path.exists():
        try:
            with pyproject_path.open("rb") as f:
                repo.pyproject = tomllib.load(f)
        except tomllib.TOMLDecodeError:
            repo.pyproject = None

    claude = path / "CLAUDE.md"
    if claude.exists():
        try:
            repo.claude_md_text = claude.read_text(encoding="utf-8")
        except OSError:
            repo.claude_md_text = None

    readme = path / "README.md"
    if readme.exists():
        try:
            repo.readme_text = readme.read_text(encoding="utf-8")
        except OSError:
            repo.readme_text = None

    repo.cli_files = _find_cli_files(path, cfg.ignore_paths)

    return repo


def _find_cli_files(path: Path, ignore: list[str]) -> list[Path]:
    """Locate plausible CLI entry files (cli.py, typer_cli.py, __main__.py)."""
    targets = {"cli.py", "typer_cli.py", "__main__.py"}
    hits: list[Path] = []
    src_dir = path / "src"
    search_roots = [src_dir] if src_dir.exists() else [path]
    for root in search_roots:
        for p in root.rglob("*.py"):
            if p.name not in targets:
                continue
            rel = p.relative_to(path).as_posix()
            if _is_ignored(rel, ignore):
                continue
            hits.append(p)
    return hits


def _is_ignored(rel_path: str, ignore: list[str]) -> bool:
    for pattern in ignore:
        if fnmatch(rel_path, pattern):
            return True
        prefix = pattern.rstrip("/*").rstrip("/")
        if prefix and rel_path.startswith(prefix + "/"):
            return True
    return False


def discover_repos(root: Path) -> list[Path]:
    """Return direct children of root that look like git repos."""
    root = root.resolve()
    repos: list[Path] = []
    if not root.is_dir():
        return repos
    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        if (child / ".git").exists():
            repos.append(child)
    return repos
