"""Fix for documentation.cli-commands-in-claude-md."""

from __future__ import annotations

import ast

from ..models import FixProposal, Repo
from . import claude_md


def _render_commands(repo: Repo) -> str | None:
    entries: list[str] = []
    for cli_file in repo.cli_files:
        try:
            tree = ast.parse(cli_file.read_text(encoding="utf-8"))
        except (OSError, SyntaxError):
            continue
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if not any(
                isinstance(d.func if isinstance(d, ast.Call) else d, ast.Attribute)
                and (d.func if isinstance(d, ast.Call) else d).attr == "command"
                for d in node.decorator_list
            ):
                continue
            doc = ast.get_docstring(node) or ""
            summary = doc.splitlines()[0].strip() if doc else ""
            cmd_name = node.name.replace("_", "-")
            if summary:
                entries.append(f"- `{cmd_name}` -- {summary}")
            else:
                entries.append(f"- `{cmd_name}`")
    if not entries:
        return None
    return "\n".join(entries) + "\n"


def propose(repo: Repo) -> FixProposal | None:
    body = _render_commands(repo)
    if not body:
        return None
    edit = claude_md.append_section(repo, "CLI Commands", body)
    if edit.original == edit.updated:
        return None
    return FixProposal(
        check_id="documentation.cli-commands-in-claude-md",
        summary="Insert CLI Commands reference block into CLAUDE.md",
        edits=[edit],
    )
