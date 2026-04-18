import shutil

from src import scanner
from src.fixes import claude_md_present, exit_codes_doc, stderr_separation_doc


def test_claude_md_skeleton_on_no_cli(repo_no_cli, tmp_path):
    dest = tmp_path / "repo"
    shutil.copytree(repo_no_cli, dest)
    repo = scanner.load_repo(dest)
    proposal = claude_md_present.propose(repo)
    assert proposal is not None
    assert len(proposal.edits) == 1
    edit = proposal.edits[0]
    assert edit.is_new
    assert "## CLI Commands" in edit.updated


def test_claude_md_skeleton_skipped_when_present(repo_perfect):
    repo = scanner.load_repo(repo_perfect)
    proposal = claude_md_present.propose(repo)
    assert proposal is None


def test_exit_codes_appended_to_existing_claude_md(repo_with_claude_md_only, tmp_path):
    dest = tmp_path / "repo"
    shutil.copytree(repo_with_claude_md_only, dest)
    repo = scanner.load_repo(dest)
    proposal = exit_codes_doc.propose(repo)
    assert proposal is not None
    edit = proposal.edits[0]
    assert not edit.is_new
    assert "## Exit Codes" in edit.updated


def test_stderr_doc_no_op_when_already_documented(repo_perfect):
    repo = scanner.load_repo(repo_perfect)
    proposal = stderr_separation_doc.propose(repo)
    assert proposal is None
