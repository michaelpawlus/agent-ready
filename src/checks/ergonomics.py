"""Ergonomics checks: can an agent compose the CLI?"""

from __future__ import annotations

from ..models import Repo
from .base import Check


FILTER_FLAG_TOKENS = ("--type", "--tags", "--since", "--until", "--folder", "--search", "--category", "--status")


def _filter_flags(repo: Repo) -> tuple[bool, str]:
    hay = " ".join(
        src
        for cli_file in repo.cli_files
        if (src := _read_or_empty(cli_file))
    )
    if not hay:
        hay = " ".join(t for t in (repo.claude_md_text, repo.readme_text) if t)
    found = [tok for tok in FILTER_FLAG_TOKENS if tok in hay]
    if found:
        return True, f"Filter flags found: {', '.join(found)}"
    return False, "No structured filter flags (--type/--tags/--since/etc.) detected"


def _structured_errors(repo: Repo) -> tuple[bool, str]:
    for cli_file in repo.cli_files:
        src = _read_or_empty(cli_file)
        if not src:
            continue
        if '"error"' in src and '"code"' in src:
            return True, f"{cli_file.name} has a structured error shape"
    errors_mod = repo.path / "src" / "errors.py"
    if errors_mod.exists():
        src = _read_or_empty(errors_mod)
        if '"error"' in src or "json_error" in src:
            return True, "src/errors.py defines a JSON error helper"
    return False, "No JSON error schema detected in cli.py or src/errors.py"


def _agent_section_in_readme(repo: Repo) -> tuple[bool, str]:
    text = (repo.readme_text or "").lower()
    markers = ("agent", "claude", "--json", "agent-friendly")
    hits = [m for m in markers if m in text]
    if len(hits) >= 2:
        return True, f"README mentions: {', '.join(hits)}"
    return False, "README lacks an agent-facing section"


def _read_or_empty(path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


CHECKS = [
    Check(
        id="ergonomics.filter-flags-present",
        category="ergonomics",
        weight=2,
        title="Structured filter flags present",
        description="Read commands take filter flags (--type/--tags/--since/etc.) so agents can narrow results.",
        remediation="Add at least one filter flag to each list/search command.",
        detect=_filter_flags,
    ),
    Check(
        id="ergonomics.structured-error-format",
        category="ergonomics",
        weight=2,
        title="Structured error format",
        description="Errors emitted as `{\"error\": \"...\", \"code\": N}` let agents catch and branch.",
        remediation="Add src/errors.py with a json_error(code, message) helper and route error paths through it.",
        detect=_structured_errors,
        has_fix_template=True,
    ),
    Check(
        id="ergonomics.agent-friendly-readme-section",
        category="ergonomics",
        weight=1,
        title="Agent-friendly README section",
        description="README calls out that the CLI is agent-callable (--json, non-interactive).",
        remediation="Add an 'Agent-Friendly Interface' section to README.md.",
        detect=_agent_section_in_readme,
    ),
]
