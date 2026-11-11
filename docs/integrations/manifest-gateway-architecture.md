# Manifest integration architecture

## Decision

Use Manifest as an optional, server-side model router for selected application workflows. Keep the current FreeLLMAPI gateway as a separate product/service. Do not chain Manifest → FreeLLMAPI → another router for the same request.

## Request path

```text
Trusted app / CLI / authenticated staff UI
                 |
                 v
       Application backend
       (session/auth + quotas)
                 |
                 v
 integrations/manifest-bridge
       (server-only credentials)
                 |
                 v
       Manifest LLM Gateway
       model=auto or pinned ID
                 |
                 v
       Connected provider/model
```

## Repository map (reviewed 2026-11-11)

| Repository | Current role | Integration boundary |
|---|---|---|
| `freellmapi` | Node/TypeScript monorepo with server, client, CLI and its own provider-routing gateway | Hosts the isolated bridge prototype under `integrations/manifest-bridge`; do not replace its router |
| `abysstattoo` | Static GitHub Pages studio site with media/brand CI | Use a protected backend for internal AI content tools; never ship a Manifest key to Pages |
| `sender-site` | Vite static site with GSAP, Lenis and Three.js | Keep AI requests behind an authenticated backend/serverless function |
| `sender-motion-kit` | Shared motion-design submodule | Store reusable prompt recipes and media utilities here only if they contain no credentials |

## Suggested Harnesses

Create separate Manifest Harnesses to isolate limits, routing and cost attribution:

- `abyss-content`: captions, campaign variants, FAQ drafts and internal studio workflows.
- `sender-content`: bilingual copy, SEO drafts, technical summaries and content operations.
- `motion-rnd`: prompt engineering, storyboards, shot lists and code assistance.

Do not use the same harness key in browser apps. Prefer one key per backend integration and rotate independently.

## API contract

- Cloud base URL: `https://app.manifest.build`
- OpenAI-compatible endpoint: `POST /v1/chat/completions`
- Model routing: `auto` (or a concrete model ID returned by `GET /v1/models`)
- Auth: `Authorization: Bearer mnfst_...`
- Use `/v1/responses` only for clients that need the Responses API; send the full conversation each time rather than relying on `previous_response_id`.

## Deployment phases

1. **Local smoke test**: configure a Harness, connect a provider, run the bridge in Termux or a development machine, and verify `/health`, `/v1/models`, and one chat completion.
2. **Backend hardening**: add real user/session auth, persistent per-user quotas, request audit metadata (never prompts by default), HTTPS, and secrets management before public deployment.
3. **ABYSS pilot**: staff-only caption and campaign assistant. Leave the public tattoo booking and customer WhatsApp flows untouched.
4. **Sender pilot**: authenticated internal bilingual SEO/content helper. No AI calls from static client code.
5. **Motion R&D**: use the same backend for prompt drafting and production checklists; actual image/video generation remains with the selected media provider.

## Acceptance checks

- No `mnfst_` key in Git history, frontend bundles, browser storage, or client-side environment variables.
- `GET /v1/models` succeeds with the bridge token.
- `POST /v1/chat/completions` succeeds with `model: auto`.
- Disallowed origins receive 403; missing bridge token receives 401; oversized payload receives 413; rate limit returns 429.
- Existing FreeLLMAPI, ABYSS CI/Pages and Sender builds remain unchanged.
