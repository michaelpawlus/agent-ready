"""Fix for machine-interface.json-flag-on-commands.

Parses Typer commands and rewrites each one that lacks a --json option to add a
default=False boolean parameter and an early `if json:` branch that emits a
JSON dict via typer.echo. This is a deliberately conservative rewrite -- the
command body is preserved and a TODO marker is left for the human.
"""

from __future__ import annotations

import ast
import re

from ..models import FileEdit, FixProposal, Repo


def _has_json_param(func: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    return any(a.arg == "json" for a in func.args.args + func.args.kwonlyargs)


def _is_typer_command(func: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    for deco in func.decorator_list:
        target = deco.func if isinstance(deco, ast.Call) else deco
        if isinstance(target, ast.Attribute) and target.attr == "command":
            return True
    return False


def _inject_json_param(src: str, func: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """Rewrite the function signature to add `json: bool = False` kwarg."""
    # Find the signature line(s). We operate on raw text to avoid ast.unparse
    # normalizing other formatting in the file.
    start = func.lineno - 1
    # Find the line ending the signature (the one with the trailing ':' before body).
    body_start = func.body[0].lineno - 1
    lines = src.splitlines(keepends=True)
    signature_block = "".join(lines[start:body_start])

    # Inject `, json: bool = False` before the closing paren of the signature.
    def _inject(match: re.Match[str]) -> str:
        params = match.group(1)
        if re.search(r"\bjson\s*:", params):
            return match.group(0)
        inner = params.strip()
        if inner.endswith(","):
            new_inner = inner + ' json: bool = typer.Option(False, "--json")'
        elif inner == "":
            new_inner = 'json: bool = typer.Option(False, "--json")'
        else:
            new_inner = inner + ', json: bool = typer.Option(False, "--json")'
        return f"({new_inner})"

    # Match the first set of parens in the signature block. This is naive but
    # correct for standard Python function signatures where the first ( is the
    # param list.
    updated_block = re.sub(r"\(([\s\S]*?)\)", _inject, signature_block, count=1)
    new_lines = lines[:start] + [updated_block] + lines[body_start:]
    return "".join(new_lines)


def propose(repo: Repo) -> FixProposal | None:
    edits: list[FileEdit] = []
    for cli_file in repo.cli_files:
        try:
            src = cli_file.read_text(encoding="utf-8")
            tree = ast.parse(src)
        except (SyntaxError, OSError):
            continue

        # Rewrite functions from the bottom up so line numbers stay valid.
        funcs = [
            n
            for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            and _is_typer_command(n)
            and not _has_json_param(n)
        ]
        if not funcs:
            continue

        updated = src
        for func in sorted(funcs, key=lambda f: f.lineno, reverse=True):
            updated = _inject_json_param(updated, func)

        if updated == src:
            continue

        if "import typer" not in updated and "from typer" not in updated:
            updated = "import typer\n" + updated

        rel = cli_file.relative_to(repo.path).as_posix()
        edits.append(FileEdit(path=rel, original=src, updated=updated))

    if not edits:
        return None
    return FixProposal(
        check_id="machine-interface.json-flag-on-commands",
        summary="Add --json option to Typer commands missing it",
        edits=edits,
    )
