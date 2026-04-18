from src import scanner
from src.checks import ergonomics


def _results(repo_path):
    repo = scanner.load_repo(repo_path)
    return {c.id: c.detect(repo) for c in ergonomics.CHECKS}


def test_perfect_passes_structured_errors(repo_perfect):
    r = _results(repo_perfect)
    assert r["ergonomics.filter-flags-present"][0]
    assert r["ergonomics.structured-error-format"][0]
    assert r["ergonomics.agent-friendly-readme-section"][0]


def test_minimal_fails_structured_errors(repo_minimal):
    r = _results(repo_minimal)
    assert not r["ergonomics.structured-error-format"][0]
