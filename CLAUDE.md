# Claude Code Notes

## Running Tests

    .venv/bin/pytest

## CLI Commands

    agent-ready score [PATH ...] [--json] [--category CAT] [--min-grade GRADE] [--root ROOT] [--fail-under INT]
    agent-ready explain CHECK_ID [--json]
    agent-ready fix PATH [--json] [--check CHECK_ID] [--category CAT] [--dry-run] [--apply]
    agent-ready list-checks [--json] [--category CAT]
    agent-ready init [--json] [--force]

All commands support `--json` for agent orchestration (JSON to stdout, human text to stderr).

## Exit Codes

- 0 -- success
- 1 -- error (scan failed, invalid config, etc.)
- 2 -- not found (path/check-id does not exist)

## Machine vs Human Output

When `--json` is passed, structured data goes to stdout and all human-readable
messages (progress, warnings) go to stderr. This lets agents pipe stdout into
`jq` without contamination.

## Agent Persona

agent-ready is a tool for the agent. The CLI performs deterministic static
checks; Claude Code is the intelligence layer that picks which failing check
to attack first and narrates the scorecard. Do not bake "should we fix this"
logic into the CLI -- that judgment lives in the skill layer.

## Agent Workflow: Weekly Portfolio Readiness Sweep

1. `agent-ready score --root ~/projects --json --min-grade B`
2. Pick the project with the worst score that you also have a live quest on
3. `agent-ready fix <path> --dry-run --json`
4. Apply the smallest PR-sized fix
5. Re-run step 1 to confirm the grade moved

## Dogfood

This repo has its own `.agent-ready.toml`. `agent-ready score .` on this repo
should grade A.
