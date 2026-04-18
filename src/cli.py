"""agent-ready Typer CLI."""

from __future__ import annotations

import json as jsonlib
import subprocess
import sys
from pathlib import Path
from typing import Optional

import typer

from . import checks as checks_mod
from . import fixes as fixes_mod
from . import scanner, grader
from .config import DEFAULT_TOML
from .fixes.base import apply_edit
from .reporters import human_reporter, json_reporter


app = typer.Typer(
    name="agent-ready",
    help="Score a repo on agent-readiness and emit PR-sized fixes.",
    no_args_is_help=True,
    add_completion=False,
)


GRADE_ORDER = {"A": 4, "B": 3, "C": 2, "D": 1, "F": 0}
VALID_CATEGORIES = {
    "discoverability",
    "invocability",
    "machine_interface",
    "machine-interface",
    "ergonomics",
    "documentation",
}


def _normalize_category(value: str | None) -> str | None:
    if not value:
        return None
    if value not in VALID_CATEGORIES:
        _emit_error(f"Unknown category: {value}", code=2, json_out=False)
    return value.replace("-", "_")


def _emit_error(message: str, *, code: int, json_out: bool) -> None:
    if json_out:
        sys.stdout.write(jsonlib.dumps({"error": message, "code": code}) + "\n")
    else:
        typer.echo(message, err=True)
    raise typer.Exit(code=code)


def _err(message: str) -> None:
    typer.echo(message, err=True)


@app.command()
def score(
    paths: list[Path] = typer.Argument(None, help="Repo paths to score. Defaults to cwd."),
    json: bool = typer.Option(False, "--json", help="Emit JSON to stdout."),
    category: Optional[str] = typer.Option(None, "--category", help="Limit checks to one category."),
    min_grade: Optional[str] = typer.Option(None, "--min-grade", help="Only show projects below this grade."),
    root: Optional[Path] = typer.Option(None, "--root", help="Scan every git repo directly under this folder."),
    fail_under: Optional[int] = typer.Option(None, "--fail-under", help="Exit 1 if any project scores below this."),
) -> None:
    """Score one or more repositories on agent-readiness."""
    cat_norm = _normalize_category(category)

    targets: list[Path] = []
    if root:
        if not root.exists():
            _emit_error(f"--root path does not exist: {root}", code=2, json_out=json)
        targets = scanner.discover_repos(root)
        if not targets:
            _err(f"No git repos found under {root}")
    elif paths:
        for p in paths:
            if not p.exists():
                _emit_error(f"Path not found: {p}", code=2, json_out=json)
            targets.append(p)
    else:
        targets = [Path.cwd()]

    cards = []
    for path in targets:
        repo = scanner.load_repo(path)
        results = checks_mod.run_checks(repo, category=cat_norm)
        card = grader.score_repo(repo, results)
        cards.append(card)

    if min_grade:
        min_grade = min_grade.upper()
        if min_grade not in GRADE_ORDER:
            _emit_error(f"Invalid --min-grade: {min_grade}", code=2, json_out=json)
        threshold = GRADE_ORDER[min_grade]
        cards = [c for c in cards if GRADE_ORDER[c.grade] < threshold]

    if json:
        payload = json_reporter.build_score_payload(cards)
        sys.stdout.write(jsonlib.dumps(payload, indent=2) + "\n")
    else:
        if cards:
            typer.echo(human_reporter.render_many(cards))
        else:
            _err("No projects matched the filter.")

    if fail_under is not None:
        below = [c for c in cards if c.score < fail_under]
        if below:
            raise typer.Exit(code=1)


@app.command("list-checks")
def list_checks(
    json: bool = typer.Option(False, "--json"),
    category: Optional[str] = typer.Option(None, "--category"),
) -> None:
    """List every known check."""
    cat_norm = _normalize_category(category)
    all_checks = checks_mod.all_checks()
    if cat_norm:
        all_checks = [c for c in all_checks if c.category == cat_norm]

    if json:
        payload = {
            "checks": [
                {
                    "id": c.id,
                    "category": c.category,
                    "weight": c.weight,
                    "title": c.title,
                    "has_fix_template": c.has_fix_template,
                }
                for c in all_checks
            ]
        }
        sys.stdout.write(jsonlib.dumps(payload, indent=2) + "\n")
        return

    by_cat: dict[str, list] = {}
    for c in all_checks:
        by_cat.setdefault(c.category, []).append(c)
    for cat_name in sorted(by_cat):
        typer.echo(f"\n{cat_name}/")
        for c in by_cat[cat_name]:
            marker = "*" if c.has_fix_template else " "
            typer.echo(f"  {marker} {c.id:<50} (weight {c.weight})  {c.title}")
    typer.echo("\n* = fix template available")


@app.command()
def explain(
    check_id: str = typer.Argument(..., help="Check ID, e.g. machine-interface.json-flag-on-commands"),
    json: bool = typer.Option(False, "--json"),
) -> None:
    """Show what a check looks for."""
    check = checks_mod.get(check_id)
    if not check:
        _emit_error(f"Unknown check: {check_id}", code=2, json_out=json)

    if json:
        payload = {
            "id": check.id,
            "category": check.category,
            "weight": check.weight,
            "title": check.title,
            "description": check.description,
            "remediation": check.remediation,
            "has_fix_template": check.has_fix_template,
        }
        sys.stdout.write(jsonlib.dumps(payload, indent=2) + "\n")
        return

    typer.echo(f"Check: {check.id} (weight {check.weight})")
    typer.echo(f"Category: {check.category}")
    typer.echo("")
    typer.echo("What it looks for:")
    typer.echo(f"  {check.description}")
    typer.echo("")
    typer.echo("Standard fix:")
    typer.echo(f"  {check.remediation}")
    if check.has_fix_template:
        typer.echo("")
        typer.echo("Fix template available -- run `agent-ready fix <path> --check " f"{check.id} --dry-run`.")


@app.command()
def fix(
    path: Path = typer.Argument(..., help="Repo path to fix."),
    json: bool = typer.Option(False, "--json"),
    check: Optional[str] = typer.Option(None, "--check", help="Fix a single check by ID."),
    category: Optional[str] = typer.Option(None, "--category", help="Fix every failing check in a category."),
    dry_run: bool = typer.Option(True, "--dry-run/--no-dry-run", help="Print diffs without editing."),
    apply: bool = typer.Option(False, "--apply", help="Apply the patches (requires clean git state)."),
) -> None:
    """Produce PR-sized patches for failing checks."""
    if not path.exists():
        _emit_error(f"Path not found: {path}", code=2, json_out=json)

    cat_norm = _normalize_category(category)

    if check and not checks_mod.get(check):
        _emit_error(f"Unknown check: {check}", code=2, json_out=json)

    if apply:
        dry_run = False
        if not _git_clean(path):
            _emit_error(
                f"Refusing to --apply: {path} has uncommitted changes.",
                code=1,
                json_out=json,
            )

    repo = scanner.load_repo(path)
    results = checks_mod.run_checks(repo)

    target_ids: list[str] = []
    if check:
        target_ids = [check]
    elif cat_norm:
        target_ids = [r.check_id for r in results if not r.passing and r.category == cat_norm]
    else:
        target_ids = [r.check_id for r in results if not r.passing]

    proposals = []
    for cid in target_ids:
        propose_fn = fixes_mod.get(cid)
        if not propose_fn:
            continue
        proposal = propose_fn(repo)
        if proposal and proposal.edits:
            proposals.append(proposal)

    if apply:
        for proposal in proposals:
            for edit in proposal.edits:
                if edit.original == edit.updated:
                    continue
                apply_edit(repo.path, edit)

    if json:
        payload = json_reporter.build_fix_payload(str(repo.path), proposals, applied=apply)
        sys.stdout.write(jsonlib.dumps(payload, indent=2) + "\n")
        return

    if not proposals:
        typer.echo("No applicable fix templates.")
        return

    for proposal in proposals:
        typer.echo(human_reporter.render_fix_proposal(proposal))
    if apply:
        typer.echo(f"\nApplied {len(proposals)} fix(es).")
    else:
        typer.echo("\n(dry-run -- pass --apply to write changes)")


@app.command()
def init(
    json: bool = typer.Option(False, "--json"),
    force: bool = typer.Option(False, "--force", help="Overwrite an existing .agent-ready.toml."),
) -> None:
    """Drop a minimal .agent-ready.toml in the current repo."""
    target = Path.cwd() / ".agent-ready.toml"
    if target.exists() and not force:
        _emit_error(
            f"{target.name} already exists. Use --force to overwrite.",
            code=1,
            json_out=json,
        )
    target.write_text(DEFAULT_TOML, encoding="utf-8")
    if json:
        sys.stdout.write(jsonlib.dumps({"created": str(target)}) + "\n")
    else:
        typer.echo(f"Wrote {target}")


def _git_clean(path: Path) -> bool:
    try:
        result = subprocess.run(
            ["git", "-C", str(path), "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return True  # no git binary; assume clean
    return result.returncode == 0 and not result.stdout.strip()


if __name__ == "__main__":
    app()
