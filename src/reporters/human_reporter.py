"""Human-readable terminal output."""

from __future__ import annotations

from ..models import FixProposal, ScoreCard
from ..fixes.base import render_diff


GRADE_SUFFIX = {
    "A": "Agent-ready",
    "B": "Usable with rough edges",
    "C": "Agent can sort-of use it",
    "D": "Human-only surface",
    "F": "Opaque to agents",
}


def render_scorecard(card: ScoreCard) -> str:
    lines = []
    suffix = GRADE_SUFFIX.get(card.grade, "")
    header = f"{card.name}: {card.score}/100 -- grade {card.grade}"
    if suffix:
        header += f" ({suffix})"
    lines.append(header)
    lines.append(f"  path: {card.path}")
    lines.append("")
    lines.append("  Category scores:")
    for name, cat in card.categories.items():
        lines.append(
            f"    {name:<20} {cat.score:>3}/100   {cat.passing}/{cat.checks} checks"
        )

    failing = card.failing
    if failing:
        lines.append("")
        lines.append(f"  Failing checks ({len(failing)}):")
        for r in failing:
            template = " [fix available]" if r.has_fix_template else ""
            lines.append(f"    [FAIL] {r.check_id}{template}")
            lines.append(f"           weight={r.weight}  {r.evidence}")
    else:
        lines.append("")
        lines.append("  All checks passing.")
    return "\n".join(lines)


def render_many(cards: list[ScoreCard]) -> str:
    parts = [render_scorecard(c) for c in cards]
    return "\n\n".join(parts)


def render_fix_proposal(proposal: FixProposal) -> str:
    lines = [f"=== {proposal.check_id}", f"    {proposal.summary}", ""]
    for edit in proposal.edits:
        tag = "(new file)" if edit.is_new else "(patch)"
        lines.append(f"    --- {edit.path} {tag}")
        diff = render_diff(edit)
        if diff:
            lines.append(diff.rstrip())
        else:
            lines.append("    (no change)")
        lines.append("")
    return "\n".join(lines)
