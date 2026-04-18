"""Check registry."""

from __future__ import annotations

from ..models import CheckResult, Repo
from .base import Check
from . import (
    discoverability,
    documentation,
    ergonomics,
    invocability,
    machine_interface,
)


_ALL_MODULES = (
    discoverability,
    invocability,
    machine_interface,
    ergonomics,
    documentation,
)


def _build_registry() -> dict[str, Check]:
    reg: dict[str, Check] = {}
    for mod in _ALL_MODULES:
        for check in mod.CHECKS:
            reg[check.id] = check
    return reg


REGISTRY: dict[str, Check] = _build_registry()


def get(check_id: str) -> Check | None:
    return REGISTRY.get(check_id)


def all_checks() -> list[Check]:
    return list(REGISTRY.values())


def run_checks(repo: Repo, category: str | None = None) -> list[CheckResult]:
    results: list[CheckResult] = []
    disabled = set(repo.config.disabled_checks) if repo.config else set()
    overrides = repo.config.weight_overrides if repo.config else {}

    for check in REGISTRY.values():
        if check.id in disabled:
            continue
        if category and check.category != category:
            continue
        weight = overrides.get(check.id, check.weight)
        try:
            passing, evidence = check.detect(repo)
        except Exception as exc:  # noqa: BLE001 -- surface detector errors as failures
            passing = False
            evidence = f"Detector crashed: {exc.__class__.__name__}: {exc}"
        results.append(
            CheckResult(
                check_id=check.id,
                category=check.category,
                weight=weight,
                passing=passing,
                evidence=evidence,
                has_fix_template=check.has_fix_template,
            )
        )
    return results
