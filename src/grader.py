"""Aggregate check results into category scores, overall score, and grade."""

from __future__ import annotations

from pathlib import Path

from .models import CategoryScore, CheckResult, Repo, ScoreCard


CATEGORY_WEIGHTS = {
    "discoverability": 20,
    "invocability": 25,
    "machine_interface": 30,
    "ergonomics": 15,
    "documentation": 10,
}


def grade_letter(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 60:
        return "C"
    if score >= 40:
        return "D"
    return "F"


def score_repo(repo: Repo, results: list[CheckResult]) -> ScoreCard:
    by_cat: dict[str, list[CheckResult]] = {c: [] for c in CATEGORY_WEIGHTS}
    for r in results:
        by_cat.setdefault(r.category, []).append(r)

    category_scores: dict[str, CategoryScore] = {}
    overall_weighted = 0.0
    overall_weight_sum = 0

    for cat, cat_weight in CATEGORY_WEIGHTS.items():
        cat_results = by_cat.get(cat, [])
        weight_total = sum(r.weight for r in cat_results)
        passing_weight = sum(r.weight for r in cat_results if r.passing)
        passing_count = sum(1 for r in cat_results if r.passing)

        if weight_total == 0:
            cat_score = 100
        else:
            cat_score = round(passing_weight / weight_total * 100)

        category_scores[cat] = CategoryScore(
            name=cat,
            score=cat_score,
            weight=cat_weight,
            checks=len(cat_results),
            passing=passing_count,
        )
        overall_weighted += cat_score * cat_weight
        overall_weight_sum += cat_weight

    overall = round(overall_weighted / overall_weight_sum) if overall_weight_sum else 0

    return ScoreCard(
        path=repo.path,
        name=repo.name,
        score=overall,
        grade=grade_letter(overall),
        categories=category_scores,
        results=results,
    )
