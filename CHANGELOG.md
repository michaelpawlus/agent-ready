# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-04-22

Initial public release.

### Added

- `agent-ready score` -- grade a repo (or every repo under `--root`) on five
  agent-readiness categories: discoverability, invocability, machine interface,
  ergonomics, documentation.
- `agent-ready fix` -- propose PR-sized patches for failing checks; `--dry-run`
  by default, `--apply` writes to disk (requires clean git state).
- `agent-ready explain <check-id>` -- describe what a check looks for and its
  standard remediation.
- `agent-ready list-checks` -- enumerate every check, grouped by category, with
  a marker for checks that ship with a fix template.
- `agent-ready init` -- drop a minimal `.agent-ready.toml` config.
- `--json` on every command; JSON to stdout, human output to stderr.
- Exit codes: 0 success / 1 error / 2 not found.
- `py.typed` marker; public surface is type-checked.
- Self-dogfooded: this repo scores A (100/100).

[Unreleased]: https://github.com/michaelpawlus/agent-ready/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/michaelpawlus/agent-ready/releases/tag/v0.1.0
