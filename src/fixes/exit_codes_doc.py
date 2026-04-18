"""Fix for machine-interface.exit-codes-documented."""

from __future__ import annotations

from ..models import FixProposal, Repo
from . import claude_md


BODY = """- 0 -- success
- 1 -- error (scan failed, invalid config, etc.)
- 2 -- not found (path/check-id does not exist)
"""


def propose(repo: Repo) -> FixProposal | None:
    edit = claude_md.append_section(repo, "Exit Codes", BODY)
    if edit.original == edit.updated:
        return None
    return FixProposal(
        check_id="machine-interface.exit-codes-documented",
        summary="Add Exit Codes section to CLAUDE.md",
        edits=[edit],
    )
