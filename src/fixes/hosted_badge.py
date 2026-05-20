"""Fix for documentation.uses-hosted-badge.

Inserts a hosted agent-ready shield at the top of README.md. If a git remote is
configured, owner/repo are filled in; otherwise placeholders are left so the
human reviewer fills them in.
"""

from __future__ import annotations

import re
import subprocess

from ..models import FileEdit, FixProposal, Repo


HOSTED_HOST = "agent-ready-badge.vercel.app"


def _git_remote_owner_repo(repo: Repo) -> tuple[str, str] | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo.path), "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    url = result.stdout.strip()
    if not url:
        return None
    # Match github.com:owner/repo(.git) or github.com/owner/repo(.git)
    m = re.search(r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$", url)
    if not m:
        return None
    return m.group(1), m.group(2)


def _badge_line(owner: str, repo_name: str) -> str:
    return (
        f"[![agent-ready](https://{HOSTED_HOST}/badge/{owner}/{repo_name}.svg)]"
        f"(https://{HOSTED_HOST}/badge/{owner}/{repo_name}.json)"
    )


def propose(repo: Repo) -> FixProposal | None:
    readme = repo.readme_text
    if readme is None:
        return None
    if HOSTED_HOST in readme or "agent-ready.dev" in readme:
        return None

    owner_repo = _git_remote_owner_repo(repo)
    if owner_repo:
        owner, repo_name = owner_repo
    else:
        owner, repo_name = "OWNER", "REPO"

    badge_line = _badge_line(owner, repo_name)
    updated = _insert_badge(readme, badge_line)
    if updated == readme:
        return None

    edit = FileEdit(path="README.md", original=readme, updated=updated)
    return FixProposal(
        check_id="documentation.uses-hosted-badge",
        summary="Add hosted agent-ready badge to README",
        edits=[edit],
    )


def _insert_badge(readme: str, badge_line: str) -> str:
    """Insert the badge after an existing run of shield lines under the H1, or
    immediately after the H1 if none exist."""
    lines = readme.splitlines(keepends=True)
    if not lines:
        return readme

    h1_idx = next(
        (i for i, ln in enumerate(lines) if ln.lstrip().startswith("# ")),
        None,
    )
    if h1_idx is None:
        return badge_line + "\n\n" + readme

    # Skip blank lines after the H1, then collect any existing shield lines.
    insert_at = h1_idx + 1
    while insert_at < len(lines) and lines[insert_at].strip() == "":
        insert_at += 1

    shield_re = re.compile(r"!\[[^\]]*\]\(https?://img\.shields\.io")
    while insert_at < len(lines) and (
        shield_re.search(lines[insert_at])
        or "agent-ready-badge.vercel.app" in lines[insert_at]
    ):
        insert_at += 1

    new_lines = lines[:insert_at] + [badge_line + "\n"] + lines[insert_at:]
    return "".join(new_lines)
