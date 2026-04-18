"""Fix for discoverability.skill-manifest-present."""

from __future__ import annotations

import json

from ..models import FileEdit, FixProposal, Repo


def propose(repo: Repo) -> FixProposal | None:
    target = repo.path / ".claude" / "skill.json"
    if target.exists():
        return None

    manifest = {
        "name": repo.name,
        "description": f"Describe what {repo.name} does in one sentence.",
        "triggers": [repo.name, f"run {repo.name}"],
        "commands": [
            {"name": "example", "summary": "Replace with a real subcommand."},
        ],
    }
    body = json.dumps(manifest, indent=2) + "\n"
    edit = FileEdit(path=".claude/skill.json", original="", updated=body)
    return FixProposal(
        check_id="discoverability.skill-manifest-present",
        summary="Write a .claude/skill.json stub",
        edits=[edit],
    )
