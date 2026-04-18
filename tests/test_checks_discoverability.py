from src import scanner
from src.checks import discoverability


def _results(repo_path):
    repo = scanner.load_repo(repo_path)
    return {c.id: c.detect(repo) for c in discoverability.CHECKS}


def test_perfect_passes_all(repo_perfect):
    r = _results(repo_perfect)
    assert r["discoverability.claude-md-present"][0]
    assert r["discoverability.readme-present"][0]
    assert r["discoverability.skill-manifest-present"][0]


def test_no_cli_fails_claude_md(repo_no_cli):
    r = _results(repo_no_cli)
    assert not r["discoverability.claude-md-present"][0]
    assert r["discoverability.readme-present"][0]
    assert not r["discoverability.skill-manifest-present"][0]


def test_claude_md_only_passes_claude_md(repo_with_claude_md_only):
    r = _results(repo_with_claude_md_only)
    assert r["discoverability.claude-md-present"][0]
    assert not r["discoverability.readme-present"][0]
