"""Load .agent-ready.toml."""

from __future__ import annotations

import tomllib
from pathlib import Path

from .models import RepoConfig


DEFAULT_IGNORE = ["node_modules/**", "dist/**", ".venv/**", "build/**", ".git/**"]


def load(repo_path: Path) -> RepoConfig:
    config_path = repo_path / ".agent-ready.toml"
    if not config_path.exists():
        return RepoConfig(ignore_paths=list(DEFAULT_IGNORE))

    with config_path.open("rb") as f:
        data = tomllib.load(f)

    disabled = list(data.get("checks", {}).get("disabled", []))
    weight_overrides = {str(k): int(v) for k, v in data.get("weights", {}).items()}
    ignore = list(data.get("ignore", {}).get("paths", DEFAULT_IGNORE))

    return RepoConfig(
        disabled_checks=disabled,
        weight_overrides=weight_overrides,
        ignore_paths=ignore,
    )


DEFAULT_TOML = """[checks]
# Disable checks by ID
disabled = []

# Override default weights
[weights]
# "machine-interface.json-flag-on-commands" = 5

[ignore]
# Glob patterns relative to repo root, excluded from file scans
paths = ["node_modules/**", "dist/**"]
"""
