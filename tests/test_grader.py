from src import checks as checks_mod, grader, scanner


def test_perfect_grades_A(repo_perfect):
    repo = scanner.load_repo(repo_perfect)
    results = checks_mod.run_checks(repo)
    card = grader.score_repo(repo, results)
    assert card.grade == "A", f"expected A, got {card.grade} with score {card.score}"
    assert card.score >= 90


def test_no_cli_grades_F(repo_no_cli):
    repo = scanner.load_repo(repo_no_cli)
    results = checks_mod.run_checks(repo)
    card = grader.score_repo(repo, results)
    assert card.grade in {"F", "D"}, f"expected F/D, got {card.grade}"


def test_grade_thresholds():
    assert grader.grade_letter(95) == "A"
    assert grader.grade_letter(90) == "A"
    assert grader.grade_letter(89) == "B"
    assert grader.grade_letter(60) == "C"
    assert grader.grade_letter(39) == "F"
