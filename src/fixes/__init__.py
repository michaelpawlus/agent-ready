"""Fix template registry."""

from __future__ import annotations

from typing import Callable

from ..models import FixProposal, Repo
from . import (
    claude_md_present,
    cli_commands_doc,
    cli_entry_point,
    exit_codes_doc,
    json_flag,
    justfile_present,
    skill_manifest,
    stderr_separation_doc,
    structured_errors,
)


ProposeFn = Callable[[Repo], FixProposal | None]


REGISTRY: dict[str, ProposeFn] = {
    "discoverability.claude-md-present": claude_md_present.propose,
    "discoverability.skill-manifest-present": skill_manifest.propose,
    "invocability.cli-entry-point": cli_entry_point.propose,
    "invocability.justfile-present": justfile_present.propose,
    "machine-interface.json-flag-on-commands": json_flag.propose,
    "machine-interface.exit-codes-documented": exit_codes_doc.propose,
    "machine-interface.stderr-separation-documented": stderr_separation_doc.propose,
    "ergonomics.structured-error-format": structured_errors.propose,
    "documentation.cli-commands-in-claude-md": cli_commands_doc.propose,
}


def get(check_id: str) -> ProposeFn | None:
    return REGISTRY.get(check_id)
