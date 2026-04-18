"""Fix for invocability.justfile-present."""

from __future__ import annotations

from ..models import FileEdit, FixProposal, Repo


JUSTFILE = """# Common tasks
install:
    .venv/bin/pip install -e .[dev]

test:
    .venv/bin/pytest

run *ARGS:
    .venv/bin/python -m src.cli {{ARGS}}
"""


def propose(repo: Repo) -> FixProposal | None:
    if (repo.path / "justfile").exists() or (repo.path / "Justfile").exists():
        return None
    edit = FileEdit(path="justfile", original="", updated=JUSTFILE)
    return FixProposal(
        check_id="invocability.justfile-present",
        summary="Add a justfile with install/test/run recipes",
        edits=[edit],
    )
