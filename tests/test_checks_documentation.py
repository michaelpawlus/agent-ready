from src import scanner
from src.checks import documentation


def _results(repo_path):
    repo = scanner.load_repo(repo_path)
    return {c.id: c.detect(repo) for c in documentation.CHECKS}


def test_perfect_passes_both(repo_perfect):
    r = _results(repo_perfect)
    assert r["documentation.cli-commands-in-claude-md"][0]
    assert r["documentation.agent-workflow-section"][0]


def test_claude_md_only_fails_cli_commands(repo_with_claude_md_only):
    r = _results(repo_with_claude_md_only)
    assert not r["documentation.cli-commands-in-claude-md"][0]
    assert not r["documentation.agent-workflow-section"][0]
