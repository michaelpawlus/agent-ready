"""Invocability checks: can an agent call the project?"""

from __future__ import annotations

from ..models import Repo
from .base import Check


def _entry_points(pyproject: dict | None) -> dict[str, str]:
    if not pyproject:
        return {}
    scripts = pyproject.get("project", {}).get("scripts", {})
    return {str(k): str(v) for k, v in scripts.items()}


def _cli_entry_point(repo: Repo) -> tuple[bool, str]:
    scripts = _entry_points(repo.pyproject)
    if scripts:
        names = ", ".join(sorted(scripts.keys()))
        return True, f"[project.scripts] defines: {names}"
    if not (repo.path / "pyproject.toml").exists():
        return False, "No pyproject.toml -- cannot register a console script"
    return False, "pyproject.toml has no [project.scripts] entries"


def _venv_binary(repo: Repo) -> tuple[bool, str]:
    scripts = _entry_points(repo.pyproject)
    if not scripts:
        return False, "No [project.scripts] entries to probe"
    venv_bin = repo.path / ".venv" / "bin"
    if not venv_bin.exists():
        return False, ".venv/bin does not exist; run `pip install -e .`"
    missing = [name for name in scripts if not (venv_bin / name).exists()]
    if missing:
        return False, f"Missing venv binaries: {', '.join(missing)}"
    return True, f"All {len(scripts)} script(s) installed in .venv/bin"


def _justfile(repo: Repo) -> tuple[bool, str]:
    for name in ("justfile", "Justfile", "Makefile"):
        if (repo.path / name).exists():
            return True, f"{name} present"
    return False, "No justfile or Makefile at repo root"


CHECKS = [
    Check(
        id="invocability.cli-entry-point",
        category="invocability",
        weight=5,
        title="CLI entry point registered",
        description="[project.scripts] in pyproject.toml is what turns a Python module into a callable command on PATH.",
        remediation="Add a [project.scripts] table to pyproject.toml mapping a command name to a Typer app.",
        detect=_cli_entry_point,
        has_fix_template=True,
    ),
    Check(
        id="invocability.venv-binary-installed",
        category="invocability",
        weight=3,
        title="CLI binary present in .venv/bin",
        description="If the script entry exists but the binary is not installed, an agent cannot actually run the command.",
        remediation="Run `.venv/bin/pip install -e .` in the repo.",
        detect=_venv_binary,
    ),
    Check(
        id="invocability.justfile-present",
        category="invocability",
        weight=1,
        title="justfile or Makefile present",
        description="A task runner gives agents a predictable entry point for common workflows (install, test, run).",
        remediation="Add a justfile or Makefile with install, test, run recipes.",
        detect=_justfile,
        has_fix_template=True,
    ),
]
