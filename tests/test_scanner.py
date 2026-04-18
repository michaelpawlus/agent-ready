from src import scanner


def test_load_repo_perfect(repo_perfect):
    repo = scanner.load_repo(repo_perfect)
    assert repo.name == "repo_perfect"
    assert repo.pyproject is not None
    assert repo.claude_md_text
    assert repo.readme_text
    assert len(repo.cli_files) == 1
    assert repo.cli_files[0].name == "cli.py"


def test_load_repo_no_cli_has_no_cli_files(repo_no_cli):
    repo = scanner.load_repo(repo_no_cli)
    assert repo.cli_files == []


def test_load_repo_ignores_pyproject_absent(repo_no_cli):
    repo = scanner.load_repo(repo_no_cli)
    assert repo.pyproject is None
