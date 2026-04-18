"""Shared pyproject.toml helpers."""

from __future__ import annotations

import re

from ..models import FileEdit, Repo
from .base import read_or_empty


def _cli_module_path(repo: Repo) -> str | None:
    """Return a dotted module path like 'src.cli' or 'src.pkg.cli' for the first CLI file."""
    if not repo.cli_files:
        return None
    cli_file = repo.cli_files[0]
    try:
        rel = cli_file.relative_to(repo.path)
    except ValueError:
        return None
    parts = list(rel.with_suffix("").parts)
    if parts and parts[-1] == "__main__":
        parts = parts[:-1]
    return ".".join(parts) if parts else None


def add_project_scripts(repo: Repo, command_name: str | None = None) -> list[FileEdit]:
    current = read_or_empty(repo.path, "pyproject.toml")
    if not current:
        return []

    if re.search(r"^\[project\.scripts\]", current, flags=re.M):
        return []  # already present

    module = _cli_module_path(repo)
    if not module:
        return []

    cmd = command_name or repo.name.replace("_", "-")
    block = f"\n[project.scripts]\n{cmd} = \"{module}:app\"\n"
    updated = current.rstrip() + "\n" + block
    return [FileEdit(path="pyproject.toml", original=current, updated=updated)]
