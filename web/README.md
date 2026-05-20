# agent-ready badge — `web/`

Vercel Node functions that serve the hosted badge endpoint. The CLI in the
parent repo is unchanged; this tree ships independently.

## Routes

| Route | Returns |
|---|---|
| `GET /badge/{owner}/{repo}.svg` | 302 to shields.io |
| `GET /badge/{owner}/{repo}.json` | JSON scorecard |
| `GET /health` | `{"ok": true, "version": "..."}` |
| `GET /` | Static landing page |

## Local development

    cd web
    npm install
    npm test
    npm run typecheck
    npm run dev     # requires vercel CLI

## Deploy

    cd web
    vercel link
    vercel --prod

The Vercel project root must be set to `web/`. No env vars are required; set
`GITHUB_TOKEN` to lift the anonymous GitHub API rate limit if traffic grows.

## Scoring subset

`lib/score.ts` computes the `public-signals-v1` subset. The hosted endpoint
deliberately does not clone repos — see the spec in
`Project Ideas/agent-ready-badge-endpoint-spec.md` for the full rationale.
