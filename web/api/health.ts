import type { VercelRequest, VercelResponse } from "@vercel/node";

import { ENDPOINT_VERSION } from "../lib/version.js";

export default function handler(_req: VercelRequest, res: VercelResponse): void {
  res.setHeader("Cache-Control", "no-cache, no-store, must-revalidate");
  res.status(200).json({ ok: true, version: ENDPOINT_VERSION });
}
