"""Shared helpers for inserting sections into CLAUDE.md."""

from __future__ import annotations

from ..models import FileEdit, Repo
from .base import ensure_trailing_newline, read_or_empty


SKELETON = """# Claude Code Notes

## Running Tests

    .venv/bin/pytest

## CLI Commands

<document each top-level subcommand here>

## Agent Persona

<describe how an agent should approach this project>
"""


def append_section(repo: Repo, heading: str, body: str) -> FileEdit:
    """Append a section to CLAUDE.md if that heading is not already present."""
    current = read_or_empty(repo.path, "CLAUDE.md")
    if not current:
        # Create a minimal file with just this section -- discoverability.claude-md-present
        # has its own full-skeleton fix.
        new_text = f"# Claude Code Notes\n\n## {heading}\n\n{body.strip()}\n"
        return FileEdit(path="CLAUDE.md", original="", updated=new_text)

    if f"## {heading}".lower() in current.lower():
        # Section exists; no-op edit.
        return FileEdit(path="CLAUDE.md", original=current, updated=current)

    base = ensure_trailing_newline(current)
    appended = base + "\n" + f"## {heading}\n\n{body.strip()}\n"
    return FileEdit(path="CLAUDE.md", original=current, updated=appended)


def propose_skeleton(repo: Repo) -> list[FileEdit]:
    current = read_or_empty(repo.path, "CLAUDE.md")
    if current:
        return []
    return [FileEdit(path="CLAUDE.md", original="", updated=SKELETON)]
