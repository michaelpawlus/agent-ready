import shutil

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


def test_uses_hosted_badge_fails_when_readme_has_no_badge(repo_perfect):
    r = _results(repo_perfect)
    assert not r["documentation.uses-hosted-badge"][0]


def test_uses_hosted_badge_passes_with_vercel_host(repo_perfect, tmp_path):
    dest = tmp_path / "repo"
    shutil.copytree(repo_perfect, dest)
    readme = dest / "README.md"
    readme.write_text(
        "# project\n\n"
        "[![agent-ready](https://agent-ready-badge.vercel.app/badge/x/y.svg)](#)\n",
        encoding="utf-8",
    )
    repo = scanner.load_repo(dest)
    detect = {c.id: c.detect(repo) for c in documentation.CHECKS}
    assert detect["documentation.uses-hosted-badge"][0]


def test_uses_hosted_badge_passes_with_custom_domain(repo_perfect, tmp_path):
    dest = tmp_path / "repo"
    shutil.copytree(repo_perfect, dest)
    readme = dest / "README.md"
    readme.write_text(
        "# project\n\n"
        "[![agent-ready](https://agent-ready.dev/badge/x/y.svg)](#)\n",
        encoding="utf-8",
    )
    repo = scanner.load_repo(dest)
    detect = {c.id: c.detect(repo) for c in documentation.CHECKS}
    assert detect["documentation.uses-hosted-badge"][0]


def test_uses_hosted_badge_fails_when_readme_missing(repo_with_claude_md_only):
    r = _results(repo_with_claude_md_only)
    assert not r["documentation.uses-hosted-badge"][0]
