"""Fix template helpers -- FileEdit rendering and safe application."""

from __future__ import annotations

import difflib
from pathlib import Path

from ..models import FileEdit


def render_diff(edit: FileEdit) -> str:
    """Render a unified diff. For new files, show the full added content."""
    a_label = "/dev/null" if edit.is_new else f"a/{edit.path}"
    b_label = f"b/{edit.path}"
    original_lines = edit.original.splitlines(keepends=True)
    updated_lines = edit.updated.splitlines(keepends=True)
    diff = difflib.unified_diff(
        original_lines,
        updated_lines,
        fromfile=a_label,
        tofile=b_label,
        n=3,
    )
    return "".join(diff)


def apply_edit(repo_path: Path, edit: FileEdit) -> None:
    target = repo_path / edit.path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(edit.updated, encoding="utf-8")


def read_or_empty(repo_path: Path, relative: str) -> str:
    path = repo_path / relative
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def ensure_trailing_newline(text: str) -> str:
    if not text:
        return text
    return text if text.endswith("\n") else text + "\n"
