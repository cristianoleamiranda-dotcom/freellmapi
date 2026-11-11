import http from "node:http";
import { timingSafeEqual } from "node:crypto";

const PORT = Number(process.env.PORT || 8787);
const BASE_URL = (process.env.MANIFEST_BASE_URL || "https://app.manifest.build").replace(/\/+$/, "");
const MANIFEST_API_KEY = process.env.MANIFEST_API_KEY || "";
const BRIDGE_API_TOKEN = process.env.BRIDGE_API_TOKEN || "";
const ALLOWED_ORIGINS = new Set((process.env.ALLOWED_ORIGINS || "").split(",").map(x => x.trim()).filter(Boolean));
const MAX_BODY_BYTES = 1_000_000;
const MAX_REQUESTS_PER_MINUTE = Math.max(1, Number(process.env.MAX_REQUESTS_PER_MINUTE || 30));
const windows = new Map();

function send(res, status, body, extra = {}) {
  res.writeHead(status, { "content-type": "application/json; charset=utf-8", "cache-control": "no-store", "x-content-type-options": "nosniff", ...extra });
  res.end(JSON.stringify(body));
}

function equalSecret(a, b) {
  const left = Buffer.from(a || "");
  const right = Buffer.from(b || "");
  return left.length === right.length && left.length > 0 && timingSafeEqual(left, right);
}

function allowedOrigin(req, res) {
  const origin = req.headers.origin;
  if (!origin) return true; // CLI and server-to-server clients.
  if (!ALLOWED_ORIGINS.has(origin)) return false;
  res.setHeader("access-control-allow-origin", origin);
  res.setHeader("vary", "Origin");
  res.setHeader("access-control-allow-headers", "authorization, content-type");
  res.setHeader("access-control-allow-methods", "GET, POST, OPTIONS");
  return true;
}

function rateAllowed(req) {
  const ip = req.socket.remoteAddress || "unknown";
  const now = Date.now();
  const entry = windows.get(ip);
  if (!entry || now - entry.startedAt >= 60_000) {
    windows.set(ip, { startedAt: now, count: 1 });
    return true;
  }
  entry.count += 1;
  return entry.count <= MAX_REQUESTS_PER_MINUTE;
}

async function readJson(req) {
  const chunks = [];
  let size = 0;
  for await (const chunk of req) {
    size += chunk.length;
    if (size > MAX_BODY_BYTES) throw Object.assign(new Error("Request body too large"), { status: 413 });
    chunks.push(chunk);
  }
  try { return JSON.parse(Buffer.concat(chunks).toString("utf8")); }
  catch { throw Object.assign(new Error("Invalid JSON body"), { status: 400 }); }
}

async function proxy(req, res, path, body) {
  const headers = { authorization: `Bearer ${MANIFEST_API_KEY}` };
  if (body) headers["content-type"] = "application/json";
  let upstream;
  try {
    upstream = await fetch(`${BASE_URL}${path}`, {
      method: body ? "POST" : "GET",
      headers,
      body: body ? JSON.stringify(body) : undefined,
      signal: AbortSignal.timeout(120_000)
    });
  } catch {
    return send(res, 502, { error: { code: "manifest_unreachable", message: "Could not reach the configured Manifest gateway." } });
  }

  if (!upstream.ok) {
    // Do not echo provider bodies, prompts, or credentials into public logs/responses.
    return send(res, upstream.status, { error: { code: "manifest_upstream_error", message: "Manifest rejected the request.", upstream_status: upstream.status } });
  }

  const contentType = upstream.headers.get("content-type") || "application/json";
  res.writeHead(upstream.status, {
    "content-type": contentType,
    "cache-control": "no-store",
    "x-content-type-options": "nosniff"
  });
  if (!upstream.body) return res.end();
  for await (const chunk of upstream.body) res.write(chunk);
  res.end();
}

const server = http.createServer(async (req, res) => {
  try {
    if (!allowedOrigin(req, res)) return send(res, 403, { error: { code: "origin_not_allowed", message: "This origin is not allowed." } });
    if (req.method === "OPTIONS") { res.writeHead(204); return res.end(); }
    const url = new URL(req.url || "/", "http://localhost");

    if (req.method === "GET" && url.pathname === "/health") {
      return send(res, 200, { ok: true, service: "manifest-bridge" });
    }

    if (!MANIFEST_API_KEY || !BRIDGE_API_TOKEN) {
      return send(res, 503, { error: { code: "bridge_not_configured", message: "Set MANIFEST_API_KEY and BRIDGE_API_TOKEN on the server." } });
    }

    const auth = req.headers.authorization || "";
    if (!equalSecret(auth.startsWith("Bearer ") ? auth.slice(7) : "", BRIDGE_API_TOKEN)) {
      return send(res, 401, { error: { code: "unauthorized", message: "A valid bridge bearer token is required." } });
    }
    if (!rateAllowed(req)) return send(res, 429, { error: { code: "rate_limited", message: "Request limit exceeded. Try again shortly." } });

    if (req.method === "GET" && url.pathname === "/v1/models") {
      return await proxy(req, res, "/v1/models");
    }
    if (req.method === "POST" && url.pathname === "/v1/chat/completions") {
      const input = await readJson(req);
      if (!Array.isArray(input.messages) || input.messages.length === 0) {
        return send(res, 400, { error: { code: "invalid_messages", message: "messages must be a non-empty array." } });
      }
      const model = typeof input.model === "string" && input.model.trim() ? input.model.trim() : "auto";
      const payload = { ...input, model };
      return await proxy(req, res, "/v1/chat/completions", payload);
    }
    return send(res, 404, { error: { code: "not_found", message: "Route not found." } });
  } catch (error) {
    return send(res, error.status || 500, { error: { code: "bridge_error", message: error.status ? error.message : "Unexpected bridge error." } });
  }
});

server.listen(PORT, "0.0.0.0", () => {
  console.log(`Manifest bridge listening on port ${PORT}; upstream: ${BASE_URL}`);
  console.log("Request bodies and credentials are not logged.");
});
