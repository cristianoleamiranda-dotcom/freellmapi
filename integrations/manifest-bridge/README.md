# Manifest LLM Gateway bridge

A small, isolated Node.js 20+ service that lets trusted server-side applications call Manifest without exposing the Manifest harness key in browser code.

## Why it is separate

This repository already contains FreeLLMAPI, which is itself a multi-provider gateway. The bridge is intentionally isolated under `integrations/manifest-bridge/`: it does not replace FreeLLMAPI, alter its routing, or make Manifest call FreeLLMAPI. Choose one gateway per request path to avoid double-routing and confusing cost/fallback logs.

## Configure

1. Copy `.env.example` to `.env` in this directory.
2. In the Manifest dashboard, create a Harness and connect at least one provider/model.
3. Set `MANIFEST_API_KEY` to the Harness key (`mnfst_...`).
4. Generate a long random `BRIDGE_API_TOKEN` and keep it server-side.
5. Set `ALLOWED_ORIGINS` to exact development origins. Do not use `*`.
6. Install Node.js 20.18+ and run:

```bash
npm start
```

The Manifest cloud base URL is `https://app.manifest.build`. For a self-hosted Manifest instance, set `MANIFEST_BASE_URL` to its reachable base URL.

## Routes

- `GET /health` — unauthenticated process health only.
- `GET /v1/models` — authenticated proxy to Manifest.
- `POST /v1/chat/completions` — authenticated OpenAI-compatible proxy; defaults `model` to `auto`.

All non-health routes require `Authorization: Bearer $BRIDGE_API_TOKEN`. Requests are limited to 1 MB and rate-limited per source IP. Streaming responses are passed through. The bridge does not log prompts, completions, or tokens.

## Security boundary

**Never put `MANIFEST_API_KEY` or `BRIDGE_API_TOKEN` in a static site, browser JavaScript, GitHub Pages, a public Vite `.env` variable, or a committed file.** A static frontend cannot safely hold a shared secret. For public-facing sites, place this bridge behind a real user/session authentication layer, abuse controls, and a serverless/backend deployment; allowlisted CORS origins alone are not authentication.

The included bearer token is intended for trusted server-to-server callers and local development only. Rotate it if exposed. Keep real `.env` files out of Git.

## Repository integration plan

- **abysstattoo**: keep the GitHub Pages site static. Add a small backend endpoint for authenticated staff workflows (draft captions, content plans, internal assistant). Do not call Manifest from the page itself.
- **sender-site**: same rule. Keep the Vite client public and route any AI feature through a protected backend/serverless function.
- **sender-motion-kit**: keep it as a reusable motion/design asset library; AI orchestration belongs in a backend, not inside the submodule.
- **freellmapi**: keep its own gateway functionality separate. This bridge is an optional integration for applications that explicitly choose Manifest.

## Smoke test

```bash
curl http://localhost:8787/health
curl http://localhost:8787/v1/models \
  -H "Authorization: Bearer $BRIDGE_API_TOKEN"
curl http://localhost:8787/v1/chat/completions \
  -H "Authorization: Bearer $BRIDGE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"model":"auto","messages":[{"role":"user","content":"Responde en español: conexión de prueba"}]}'
```

A successful `/v1/models` response confirms the Harness key and provider routing are accepted. A successful chat completion confirms the full path.
