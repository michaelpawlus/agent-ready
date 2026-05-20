import type { VercelRequest, VercelResponse } from "@vercel/node";

import { SUBSET_VERSION } from "../lib/score.js";
import { handleBadge } from "../lib/handler.js";

export default async function handler(req: VercelRequest, res: VercelResponse): Promise<void> {
  if (req.method !== "GET" && req.method !== "HEAD") {
    res.status(405).json({ error: "method not allowed", code: 1 });
    return;
  }

  const result = await handleBadge(req.query);

  switch (result.kind) {
    case "redirect":
      res.setHeader("Location", result.location);
      res.setHeader("X-Agent-Ready-Subset", SUBSET_VERSION);
      res.status(result.status).end();
      return;
    case "json":
      res.setHeader("Content-Type", "application/json; charset=utf-8");
      res.setHeader("X-Agent-Ready-Subset", SUBSET_VERSION);
      res.status(result.status).send(JSON.stringify(result.body));
      return;
    case "error":
      res.setHeader("Content-Type", "application/json; charset=utf-8");
      res.status(result.status).send(JSON.stringify(result.body));
      return;
    case "svg-fallback":
      res.setHeader("Content-Type", "image/svg+xml");
      res.status(result.status).send(result.svg);
      return;
  }
}
