"""Machine interface checks: is the output parseable?"""

from __future__ import annotations

import ast

from ..models import Repo
from .base import Check


def _has_json_option(func: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    for arg in func.args.args + func.args.kwonlyargs:
        if arg.arg == "json":
            return True
    for default in func.args.defaults + func.args.kw_defaults:
        if default is None:
            continue
        src = ast.unparse(default) if hasattr(ast, "unparse") else ""
        if "--json" in src:
            return True
    return False


def _typer_commands(tree: ast.AST) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    """Return functions decorated with @app.command() or @<name>.command()."""
    funcs: list[ast.FunctionDef | ast.AsyncFunctionDef] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for deco in node.decorator_list:
            target = deco.func if isinstance(deco, ast.Call) else deco
            if isinstance(target, ast.Attribute) and target.attr == "command":
                funcs.append(node)
                break
    return funcs


def _json_flag(repo: Repo) -> tuple[bool, str]:
    if not repo.cli_files:
        return False, "No cli.py found to inspect"
    missing: list[str] = []
    total = 0
    for cli_file in repo.cli_files:
        try:
            tree = ast.parse(cli_file.read_text(encoding="utf-8"))
        except (SyntaxError, OSError):
            continue
        for func in _typer_commands(tree):
            total += 1
            if not _has_json_option(func):
                missing.append(f"{cli_file.name}:{func.name}")
    if total == 0:
        return False, "No Typer @app.command() decorators detected"
    if missing:
        return False, f"{len(missing)}/{total} commands missing --json: {', '.join(missing[:3])}"
    return True, f"All {total} Typer commands accept --json"


def _claude_mentions(repo: Repo, *keywords: str) -> bool:
    if not repo.claude_md_text:
        return False
    text = repo.claude_md_text.lower()
    return all(k.lower() in text for k in keywords)


def _exit_codes_documented(repo: Repo) -> tuple[bool, str]:
    if not repo.claude_md_text:
        return False, "CLAUDE.md not present"
    text = repo.claude_md_text.lower()
    if "exit code" in text or "## exit codes" in text:
        return True, "CLAUDE.md mentions exit codes"
    return False, "CLAUDE.md does not document exit codes"


def _stderr_separation(repo: Repo) -> tuple[bool, str]:
    if not repo.claude_md_text:
        return False, "CLAUDE.md not present"
    text = repo.claude_md_text.lower()
    if "stderr" in text and ("stdout" in text or "json to stdout" in text):
        return True, "CLAUDE.md documents stdout/stderr split"
    return False, "CLAUDE.md does not document stdout/stderr separation"


def _non_interactive(repo: Repo) -> tuple[bool, str]:
    """Heuristic: CLAUDE.md or README mentions non-interactive/quick/yes flags, or CLI files have no input()."""
    hay = " ".join(t for t in (repo.claude_md_text, repo.readme_text) if t).lower()
    if any(tok in hay for tok in ("--json", "--quick", "--yes", "non-interactive")):
        # Also ensure cli.py does not call input()
        for cli_file in repo.cli_files:
            try:
                src = cli_file.read_text(encoding="utf-8")
            except OSError:
                continue
            if "input(" in src and "# noqa: input" not in src:
                return False, f"{cli_file.name} calls input(); not agent-safe"
        return True, "Non-interactive mode advertised (--json/--quick/--yes)"
    return False, "No sign of non-interactive mode support"


CHECKS = [
    Check(
        id="machine-interface.json-flag-on-commands",
        category="machine_interface",
        weight=5,
        title="--json flag on every command",
        description="Every top-level subcommand exposes a --json option so agents can parse output without regexing human text.",
        remediation="Add `json: bool = typer.Option(False, '--json')` to each command and branch output through a JSON helper.",
        detect=_json_flag,
        has_fix_template=True,
    ),
    Check(
        id="machine-interface.stderr-separation-documented",
        category="machine_interface",
        weight=3,
        title="stdout/stderr separation documented",
        description="CLAUDE.md documents that machine output goes to stdout and human messages to stderr.",
        remediation="Append a 'Machine vs Human Output' note to CLAUDE.md.",
        detect=_stderr_separation,
        has_fix_template=True,
    ),
    Check(
        id="machine-interface.exit-codes-documented",
        category="machine_interface",
        weight=3,
        title="Exit codes documented",
        description="Agents branch on exit codes. CLAUDE.md should document the meaning of 0/1/2.",
        remediation="Append an Exit Codes section to CLAUDE.md.",
        detect=_exit_codes_documented,
        has_fix_template=True,
    ),
    Check(
        id="machine-interface.non-interactive-supported",
        category="machine_interface",
        weight=3,
        title="Non-interactive mode supported",
        description="The CLI must run fully headless (no prompts) when --json is passed or stdin is not a TTY.",
        remediation="Add --quick / --yes flags and gate prompts behind interactive checks.",
        detect=_non_interactive,
    ),
]
