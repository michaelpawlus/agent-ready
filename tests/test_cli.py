import json

from typer.testing import CliRunner

from src.cli import app


runner = CliRunner()


def test_score_json_on_perfect_fixture(repo_perfect):
    result = runner.invoke(app, ["score", str(repo_perfect), "--json"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["projects"][0]["grade"] == "A"


def test_score_human_output(repo_perfect):
    result = runner.invoke(app, ["score", str(repo_perfect)])
    assert result.exit_code == 0
    assert "grade A" in result.stdout


def test_list_checks_json():
    result = runner.invoke(app, ["list-checks", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert len(data["checks"]) >= 10


def test_explain_unknown_check_returns_2():
    result = runner.invoke(app, ["explain", "bogus.check"])
    assert result.exit_code == 2


def test_explain_known_check():
    result = runner.invoke(app, ["explain", "machine-interface.json-flag-on-commands", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["has_fix_template"]


def test_fix_dry_run_on_minimal(repo_minimal):
    result = runner.invoke(app, ["fix", str(repo_minimal), "--dry-run", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["total_fixes"] >= 1
    assert all(not f["applied"] for f in data["fixes"])


def test_fail_under_triggers_exit_1(repo_minimal):
    result = runner.invoke(app, ["score", str(repo_minimal), "--fail-under", "90", "--json"])
    assert result.exit_code == 1
