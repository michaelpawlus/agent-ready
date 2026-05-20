import shutil

from src import scanner
from src.fixes import hosted_badge


def test_hosted_badge_inserts_after_shield_block(repo_perfect, tmp_path):
    dest = tmp_path / "repo"
    shutil.copytree(repo_perfect, dest)
    (dest / "README.md").write_text(
        "# project\n"
        "\n"
        "[![CI](https://img.shields.io/badge/ci-passing-green)](#)\n"
        "\n"
        "Body text.\n",
        encoding="utf-8",
    )
    repo = scanner.load_repo(dest)
    proposal = hosted_badge.propose(repo)
    assert proposal is not None
    assert len(proposal.edits) == 1
    edit = proposal.edits[0]
    assert edit.path == "README.md"
    assert not edit.is_new
    assert "agent-ready-badge.vercel.app" in edit.updated
    # The inserted line should land after the existing shield line.
    ci_idx = edit.updated.index("ci-passing-green")
    badge_idx = edit.updated.index("agent-ready-badge.vercel.app")
    assert ci_idx < badge_idx
    # Original body must be preserved.
    assert "Body text." in edit.updated


def test_hosted_badge_skipped_when_already_present(repo_perfect, tmp_path):
    dest = tmp_path / "repo"
    shutil.copytree(repo_perfect, dest)
    (dest / "README.md").write_text(
        "# project\n\n"
        "[![agent-ready](https://agent-ready-badge.vercel.app/badge/x/y.svg)](#)\n",
        encoding="utf-8",
    )
    repo = scanner.load_repo(dest)
    proposal = hosted_badge.propose(repo)
    assert proposal is None


def test_hosted_badge_skipped_when_no_readme(repo_with_claude_md_only, tmp_path):
    dest = tmp_path / "repo"
    shutil.copytree(repo_with_claude_md_only, dest)
    repo = scanner.load_repo(dest)
    proposal = hosted_badge.propose(repo)
    assert proposal is None


def test_hosted_badge_uses_placeholders_when_no_git_remote(repo_perfect, tmp_path):
    dest = tmp_path / "repo"
    shutil.copytree(repo_perfect, dest)
    (dest / "README.md").write_text(
        "# project\n\nBody.\n",
        encoding="utf-8",
    )
    # No .git directory in fixture → owner/repo placeholders.
    repo = scanner.load_repo(dest)
    proposal = hosted_badge.propose(repo)
    assert proposal is not None
    edit = proposal.edits[0]
    assert "OWNER/REPO" in edit.updated


def test_hosted_badge_inserts_immediately_after_h1_when_no_existing_shields(
    repo_perfect, tmp_path
):
    dest = tmp_path / "repo"
    shutil.copytree(repo_perfect, dest)
    (dest / "README.md").write_text(
        "# project\n\nFirst paragraph.\n",
        encoding="utf-8",
    )
    repo = scanner.load_repo(dest)
    proposal = hosted_badge.propose(repo)
    assert proposal is not None
    edit = proposal.edits[0]
    lines = edit.updated.splitlines()
    # The badge line should appear before the first paragraph.
    badge_line = next(i for i, ln in enumerate(lines) if "agent-ready-badge" in ln)
    para_line = next(i for i, ln in enumerate(lines) if "First paragraph" in ln)
    assert badge_line < para_line
