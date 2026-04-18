"""Fix for ergonomics.structured-error-format."""

from __future__ import annotations

from ..models import FileEdit, FixProposal, Repo


MODULE = '''"""Structured error helper for JSON output."""

from __future__ import annotations

import json
import sys


def json_error(code: int, message: str) -> None:
    """Write a structured error to stdout and exit with ``code``."""
    sys.stdout.write(json.dumps({"error": message, "code": code}) + "\\n")
    raise SystemExit(code)
'''


def propose(repo: Repo) -> FixProposal | None:
    target = repo.path / "src" / "errors.py"
    if target.exists():
        return None
    edit = FileEdit(path="src/errors.py", original="", updated=MODULE)
    return FixProposal(
        check_id="ergonomics.structured-error-format",
        summary="Add src/errors.py with a json_error() helper",
        edits=[edit],
    )
