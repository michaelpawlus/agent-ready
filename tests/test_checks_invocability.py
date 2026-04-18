from src import scanner
from src.checks import invocability


def _results(repo_path):
    repo = scanner.load_repo(repo_path)
    return {c.id: c.detect(repo) for c in invocability.CHECKS}


def test_perfect_has_entry_point_and_venv(repo_perfect):
    r = _results(repo_perfect)
    assert r["invocability.cli-entry-point"][0]
    assert r["invocability.venv-binary-installed"][0]
    assert r["invocability.justfile-present"][0]


def test_minimal_missing_entry_point(repo_minimal):
    r = _results(repo_minimal)
    assert not r["invocability.cli-entry-point"][0]
    assert not r["invocability.venv-binary-installed"][0]
