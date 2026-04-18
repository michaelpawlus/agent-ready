# agent-ready

Score a local repository on **agent-readiness** -- how usable the project is as
a surface for an AI agent (Claude Code or any tool-using LLM). Emit PR-sized
fixes for failing checks.

## Install

    pip install -e .

## Quick Start

    agent-ready score .
    agent-ready score --root ~/projects --json --min-grade B
    agent-ready fix . --dry-run
    agent-ready list-checks
    agent-ready explain machine-interface.json-flag-on-commands

## Categories

| Category | Weight | What it measures |
|---|---|---|
| Discoverability   | 20% | Can an agent find the surface? |
| Invocability      | 25% | Can an agent call it? |
| Machine Interface | 30% | Is the output parseable? |
| Ergonomics        | 15% | Can an agent compose it? |
| Documentation     | 10% | Is the surface documented? |

## Grades

- **A** 90-100 -- Agent-ready
- **B** 75-89  -- Usable with rough edges
- **C** 60-74  -- Agent can sort-of use it
- **D** 40-59  -- Human-only surface
- **F** 0-39   -- Opaque to agents

## Exit Codes

- 0 success
- 1 error
- 2 not found

## Agent-Friendly Interface

Every command supports `--json` for agent orchestration: JSON to stdout, human
text to stderr. Commands are non-interactive when `--json` is passed.
