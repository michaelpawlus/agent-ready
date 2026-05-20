"""Documentation checks: is the surface documented where agents look?"""

from __future__ import annotations

from ..models import Repo
from .base import Check


def _cli_commands_section(repo: Repo) -> tuple[bool, str]:
    text = repo.claude_md_text or ""
    if not text:
        return False, "CLAUDE.md not present"
    lowered = text.lower()
    if "## cli commands" in lowered or "### cli commands" in lowered:
        return True, "CLAUDE.md has a CLI Commands section"
    return False, "CLAUDE.md has no CLI Commands section"


def _agent_workflow_section(repo: Repo) -> tuple[bool, str]:
    text = (repo.claude_md_text or "").lower()
    if not text:
        return False, "CLAUDE.md not present"
    markers = ("## agent workflow", "### agent workflow", "## agent persona", "## agent-")
    if any(m in text for m in markers):
        return True, "CLAUDE.md has an Agent Workflow/Persona section"
    return False, "CLAUDE.md has no Agent Workflow section"


HOSTED_BADGE_HOSTS = ("agent-ready-badge.vercel.app", "agent-ready.dev")


def _uses_hosted_badge(repo: Repo) -> tuple[bool, str]:
    text = repo.readme_text or ""
    if not text:
        return False, "README not present"
    for host in HOSTED_BADGE_HOSTS:
        if host in text:
            return True, f"README links to hosted badge at {host}"
    return False, "README has no hosted agent-ready badge"


CHECKS = [
    Check(
        id="documentation.cli-commands-in-claude-md",
        category="documentation",
        weight=3,
        title="CLI Commands section in CLAUDE.md",
        description="A '## CLI Commands' section in CLAUDE.md is where agents look first for the command surface.",
        remediation="Parse the CLI and insert a Markdown reference block under '## CLI Commands' in CLAUDE.md.",
        detect=_cli_commands_section,
        has_fix_template=True,
    ),
    Check(
        id="documentation.agent-workflow-section",
        category="documentation",
        weight=2,
        title="Agent workflow section",
        description="CLAUDE.md documents how an agent should use the project step-by-step.",
        remediation="Add an 'Agent Workflow' section with a numbered walkthrough.",
        detect=_agent_workflow_section,
    ),
    Check(
        id="documentation.uses-hosted-badge",
        category="documentation",
        weight=1,
        title="README links to hosted agent-ready badge",
        description=(
            "A hosted shield from the agent-ready badge endpoint advertises the "
            "score in the README and links viewers to a live JSON scorecard."
        ),
        remediation=(
            "Add `![agent-ready](https://agent-ready-badge.vercel.app/badge/"
            "OWNER/REPO.svg)` to the top of README.md."
        ),
        detect=_uses_hosted_badge,
        has_fix_template=True,
    ),
]
