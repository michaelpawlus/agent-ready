import shutil

from src import scanner
from src.fixes import cli_entry_point


def test_cli_entry_point_added_when_missing(repo_minimal, tmp_path):
    dest = tmp_path / "repo"
    shutil.copytree(repo_minimal, dest)
    repo = scanner.load_repo(dest)
    proposal = cli_entry_point.propose(repo)
    assert proposal is not None
    edit = proposal.edits[0]
    assert "[project.scripts]" in edit.updated
    assert ":app" in edit.updated


def test_cli_entry_point_skipped_when_present(repo_perfect):
    repo = scanner.load_repo(repo_perfect)
    proposal = cli_entry_point.propose(repo)
    assert proposal is None
