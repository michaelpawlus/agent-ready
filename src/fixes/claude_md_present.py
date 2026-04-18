"""Fix for discoverability.claude-md-present."""

from __future__ import annotations

from ..models import FileEdit, FixProposal, Repo
from . import claude_md


def propose(repo: Repo) -> FixProposal | None:
    edits = claude_md.propose_skeleton(repo)
    if not edits:
        return None
    return FixProposal(
        check_id="discoverability.claude-md-present",
        summary="Create a minimal CLAUDE.md skeleton",
        edits=edits,
    )
