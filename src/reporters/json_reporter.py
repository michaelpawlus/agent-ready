"""JSON output helpers."""

from __future__ import annotations

from datetime import datetime, timezone

from ..models import FixProposal, ScoreCard
from ..fixes.base import render_diff


def scorecard_to_dict(card: ScoreCard) -> dict:
    return {
        "path": str(card.path),
        "name": card.name,
        "score": card.score,
        "grade": card.grade,
        "categories": {
            name: {
                "score": cat.score,
                "weight": cat.weight,
                "checks": cat.checks,
                "passing": cat.passing,
            }
            for name, cat in card.categories.items()
        },
        "failing_checks": [
            {
                "id": r.check_id,
                "category": r.category,
                "weight": r.weight,
                "evidence": r.evidence,
                "has_fix_template": r.has_fix_template,
            }
            for r in card.failing
        ],
    }


def build_score_payload(cards: list[ScoreCard]) -> dict:
    grade_dist: dict[str, int] = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
    for c in cards:
        grade_dist[c.grade] = grade_dist.get(c.grade, 0) + 1

    avg = round(sum(c.score for c in cards) / len(cards)) if cards else 0

    return {
        "scanned_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "projects": [scorecard_to_dict(c) for c in cards],
        "summary": {
            "project_count": len(cards),
            "average_score": avg,
            "grade_distribution": grade_dist,
        },
    }


def build_fix_payload(
    repo_path: str,
    proposals: list[FixProposal],
    applied: bool,
) -> dict:
    fixes_out = []
    for p in proposals:
        files_out = []
        for edit in p.edits:
            files_out.append(
                {
                    "path": edit.path,
                    "is_new": edit.is_new,
                    "diff": render_diff(edit),
                }
            )
        fixes_out.append(
            {
                "check_id": p.check_id,
                "summary": p.summary,
                "files": files_out,
                "applied": applied,
            }
        )
    return {
        "path": repo_path,
        "fixes": fixes_out,
        "total_fixes": len(proposals),
    }
