"""Fix for invocability.cli-entry-point."""

from __future__ import annotations

from ..models import FixProposal, Repo
from . import pyproject as py_fix


def propose(repo: Repo) -> FixProposal | None:
    edits = py_fix.add_project_scripts(repo)
    if not edits:
        return None
    return FixProposal(
        check_id="invocability.cli-entry-point",
        summary="Register [project.scripts] entry in pyproject.toml",
        edits=edits,
    )
