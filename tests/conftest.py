"""Shared pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def repo_perfect() -> Path:
    return FIXTURES / "repo_perfect"


@pytest.fixture
def repo_minimal() -> Path:
    return FIXTURES / "repo_minimal"


@pytest.fixture
def repo_no_cli() -> Path:
    return FIXTURES / "repo_no_cli"


@pytest.fixture
def repo_with_claude_md_only() -> Path:
    return FIXTURES / "repo_with_claude_md_only"
