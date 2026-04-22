# agent-ready

[![PyPI version](https://img.shields.io/pypi/v/agent-ready.svg)](https://pypi.org/project/agent-ready/)
[![Python versions](https://img.shields.io/pypi/pyversions/agent-ready.svg)](https://pypi.org/project/agent-ready/)
[![CI](https://github.com/michaelpawlus/agent-ready/actions/workflows/ci.yml/badge.svg)](https://github.com/michaelpawlus/agent-ready/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![agent-ready](https://img.shields.io/badge/agent--ready-A%20(100%2F100)-brightgreen)](#badge-your-own-repo)

> **Score any repo on how usable it is to an AI agent. Auto-fix the gaps.**

<p align="center">
  <img src="assets/demo.gif" alt="agent-ready score . run from the terminal, showing the category scorecard and an explain of a failing check" width="720">
</p>

## Why this exists

Your repo has a new reader. Claude Code, Cursor, and every other tool-using LLM
now land in your project the same way a new hire does -- except they only have
what's discoverable from the filesystem. Nobody measures whether a repo is
actually shaped for that reader. `agent-ready` is a rubric (five weighted
categories, static checks) plus a `fix` command that writes the PR-sized
patches for the gaps it finds.

## Quickstart

    pip install agent-ready
    agent-ready score .
    agent-ready fix . --dry-run

That's it. Everything else is `--json` variants of those three commands.

## What it measures

| Category | Weight | What it checks | Example |
|---|---|---|---|
| Discoverability   | 20% | Can an agent find the surface?    | `CLAUDE.md`, `README.md`, skill manifest present |
| Invocability      | 25% | Can an agent call it?             | CLI entry point in `pyproject.toml`, venv-installed binary, `justfile`/`Makefile` |
| Machine Interface | 30% | Is the output parseable?          | `--json` flag on every command, `{"error", "code"}` error shape, documented exit codes, non-interactive mode |
| Ergonomics        | 15% | Can an agent compose it?          | Filter flags (`--since`, `--type`, `--tags`), structured errors, agent-friendly README section |
| Documentation     | 10% | Is the surface documented?        | `## CLI Commands` block in `CLAUDE.md`, agent workflow section |

Run `agent-ready list-checks` to see every individual check, and
`agent-ready explain <check-id>` for what any single check looks for and how
to fix it.

**Grades:** A 90-100 · B 75-89 · C 60-74 · D 40-59 · F 0-39.

## Example output

```
$ agent-ready score .
agent-ready: 100/100 -- grade A (Agent-ready)
  path: /home/you/projects/agent-ready

  Category scores:
    discoverability      100/100   3/3 checks
    invocability         100/100   3/3 checks
    machine_interface    100/100   4/4 checks
    ergonomics           100/100   3/3 checks
    documentation        100/100   2/2 checks

  All checks passing.
```

Sweep a whole portfolio and filter to anything below a B:

    agent-ready score --root ~/projects --json --min-grade B | jq '.projects[] | {name, grade, score}'

## Badge your own repo

Once you've scored an A, advertise it. Drop this in the target repo's README:

```markdown
[![agent-ready](https://img.shields.io/badge/agent--ready-A-brightgreen)](https://github.com/michaelpawlus/agent-ready)
```

HTML variant (if you need to control width / alignment):

```html
<a href="https://github.com/michaelpawlus/agent-ready">
  <img src="https://img.shields.io/badge/agent--ready-A-brightgreen" alt="agent-ready: A">
</a>
```

A hosted endpoint at `https://agent-ready.dev/badge/{owner}/{repo}.svg` that
scores on demand is on the roadmap (see `CHANGELOG.md`).

## Programmatic use

Every command takes `--json`. JSON goes to stdout; all human-readable progress
and warnings go to stderr -- pipe into `jq` without contamination.

    agent-ready score . --json | jq '.projects[0].grade'
    agent-ready list-checks --json | jq '.checks[] | select(.has_fix_template)'
    agent-ready explain machine-interface.json-flag-on-commands --json

**Exit codes:** `0` success · `1` error · `2` not found (path or check-id).

Use `--fail-under N` in CI to gate merges on score:

    agent-ready score . --fail-under 90

Python import path (same entry point the CLI uses):

```python
from src import scanner, grader
from src import checks as checks_mod

repo = scanner.load_repo(".")
results = checks_mod.run_checks(repo)
card = grader.score_repo(repo, results)
print(card.score, card.grade)
```

## Fix failing checks

`agent-ready fix` proposes patches. `--dry-run` is the default:

    agent-ready fix . --check machine-interface.json-flag-on-commands --dry-run
    agent-ready fix . --category machine-interface --apply

`--apply` refuses to run on a dirty working tree -- keeps every fix as a
reviewable, PR-sized diff.

## Config

Drop a `.agent-ready.toml` to disable checks, tune weights, or exclude paths:

    agent-ready init

```toml
[checks]
disabled = []

[weights]

[ignore]
paths = ["node_modules/**", "dist/**", ".venv/**", "build/**", "tests/fixtures/**"]
```

## Related

- [`typer-duo`](https://github.com/michaelpawlus/typer-duo) -- scaffolds the
  kind of Typer CLI this scorer rewards (json/human dual output, exit codes,
  agent-ready instructions in CLAUDE.md).
- [`portfolio-audit`](https://github.com/michaelpawlus/portfolio-audit) --
  sweeps every repo in `~/projects` and reports activity, CLI health, and
  activation gaps; pairs with `agent-ready score --root ~/projects`.

## License

[MIT](LICENSE)
