# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-05-19

### Added

- Hosted badge endpoint under `web/` (Vercel Node functions). Routes:
  `GET /badge/{owner}/{repo}.svg` (302 to shields.io),
  `GET /badge/{owner}/{repo}.json` (full scorecard), `GET /health`, and a
  static landing page at `/`.
- `public-signals-v1` scoring subset — eight binary signals read from the
  GitHub Contents API and the PyPI JSON API. Responses carry an
  `X-Agent-Ready-Subset` header so consumers know this is an approximation
  of the full local CLI grade.
- New check `documentation.uses-hosted-badge` (weight 1) plus a `fix`
  template that inserts the hosted shield at the top of `README.md`,
  filling in `OWNER/REPO` from the `origin` remote when available.
- README rewritten with a "Hosted badge (recommended)" section and a
  live shield pointing at `agent-ready-badge.vercel.app`.

### Notes

- The endpoint deliberately does not clone repos. `?full=1` is *not*
  supported. Run `agent-ready score .` locally for the full rubric.
- The `agent-ready.dev` custom domain is not yet registered; the endpoint
  ships under `agent-ready-badge.vercel.app`. Both hosts are recognised
  by `documentation.uses-hosted-badge` so a future domain swap is a
  no-op for repos using either URL.

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

[Unreleased]: https://github.com/michaelpawlus/agent-ready/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/michaelpawlus/agent-ready/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/michaelpawlus/agent-ready/releases/tag/v0.1.0
