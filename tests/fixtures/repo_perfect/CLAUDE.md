# Claude Code Notes

## Running Tests

    .venv/bin/pytest

## CLI Commands

    perfect score [PATH] [--json]

All commands support `--json`. JSON output goes to stdout while human-readable
messages go to stderr.

## Exit Codes

- 0 -- success
- 1 -- error
- 2 -- not found

## Machine vs Human Output

Agents should pipe stdout to jq; stderr carries human progress messages.

## Agent Persona

This project is a surface for agents. Keep the CLI deterministic and headless.

## Agent Workflow

1. Run `perfect score . --json`.
2. Parse the result.
3. Decide the next action based on the failing checks.
