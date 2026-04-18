from src import scanner
from src.checks import machine_interface as mi


def _results(repo_path):
    repo = scanner.load_repo(repo_path)
    return {c.id: c.detect(repo) for c in mi.CHECKS}


def test_perfect_passes_all(repo_perfect):
    r = _results(repo_perfect)
    assert r["machine-interface.json-flag-on-commands"][0]
    assert r["machine-interface.exit-codes-documented"][0]
    assert r["machine-interface.stderr-separation-documented"][0]
    assert r["machine-interface.non-interactive-supported"][0]


def test_minimal_missing_json_flag(repo_minimal):
    r = _results(repo_minimal)
    assert not r["machine-interface.json-flag-on-commands"][0]
    # pyproject/README lack agent wording, so non-interactive also fails
    assert not r["machine-interface.non-interactive-supported"][0]
