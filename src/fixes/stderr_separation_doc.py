"""Fix for machine-interface.stderr-separation-documented."""

from __future__ import annotations

from ..models import FixProposal, Repo
from . import claude_md


BODY = """When `--json` is passed, structured data goes to stdout and all human-readable
messages (progress, warnings, errors) go to stderr. This lets agents pipe stdout
into `jq` without contamination.
"""


def propose(repo: Repo) -> FixProposal | None:
    edit = claude_md.append_section(repo, "Machine vs Human Output", BODY)
    if edit.original == edit.updated:
        return None
    return FixProposal(
        check_id="machine-interface.stderr-separation-documented",
        summary="Document stdout/stderr separation in CLAUDE.md",
        edits=[edit],
    )
