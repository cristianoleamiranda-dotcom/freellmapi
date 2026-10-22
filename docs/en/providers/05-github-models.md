# GitHub Models and GitHub API authentication

GitHub Models is OpenAI-compatible inference reached with a **GitHub token**. There is no separate API key to mint: the credential is the same one that authenticates the GitHub REST API, so the rules in GitHub's [Authentication for the REST API](https://docs.github.com/en/rest/authentication/authenticating-to-the-rest-api) documentation are the rules here.

This page covers the three ways to obtain that token, how FreeLLMAPI stores and validates it, what each failure code means, and the GitHub Actions case where the token is already in the environment.

- Platform id: `github`
- Adapter: [`server/src/providers/github.ts`](../../../server/src/providers/github.ts) (`GitHubProvider`, an `OpenAICompatProvider` subclass)
- Inference base URL: `https://models.github.ai/inference` (`GITHUB_MODELS_BASE_URL` overrides it)
- Credential-check endpoint: `https://api.github.com/user` (`GITHUB_API_BASE_URL` overrides it)
- REST API version pinned on every request: `2026-03-10`

## Getting a token

| Path | When to use | Notes |
| --- | --- | --- |
| **Fine-grained personal access token** | Personal use. GitHub recommends this over a classic token. | Grant the **Models** permission (read). Fine-grained tokens are authorized during creation, including for SAML SSO organizations. |
| **Personal access token (classic)** | Legacy personal setups. | Scopes are chosen per endpoint; a classic token needs to be **authorized for each SSO organization** after creation. |
| **GitHub App token** | Acting for an organization or on behalf of another user. | App tokens are authorized for SAML SSO automatically. Endpoint availability and required app permissions are documented per endpoint. |
| **`GITHUB_TOKEN` in a workflow** | Anything running inside GitHub Actions. | Recommended over storing a PAT as a secret. Scope it with the workflow's `permissions:` key. **Expires with the job.** |

Whichever path you take, the token travels in the `Authorization` header. `Authorization: Bearer <token>` and `Authorization: token <token>` are both accepted by GitHub; a JWT (GitHub App) **must** use `Bearer`. `GitHubProvider` always sends `Bearer`, plus the `Accept: application/vnd.github+json` and `X-GitHub-Api-Version: 2026-03-10` headers the REST docs ask for.

## Adding the key

**Dashboard** — Keys → add a key → **GitHub Models (PAT, GitHub App or Actions token)** → paste the token.

**Declarative config** — any boot config keeps working:

```json
{ "keys": [{ "platform": "github", "key": "github_pat_...", "label": "work" }] }
```

**Environment (headless / CI)** — see the next section.

## The GitHub Actions case

Workflows get a short-lived token for free. The documented way to pass it is an environment variable:

```yaml
jobs:
  gateway:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      models: read        # the permission the models endpoint needs
    steps:
      - env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          curl --request GET \
            --url "https://api.github.com/PATH" \
            --header "Authorization: Bearer $GH_TOKEN"
```

FreeLLMAPI reads that environment at boot ([`server/src/services/github-token.ts`](../../../server/src/services/github-token.ts)):

| Variable | Effect |
| --- | --- |
| `FREELLMAPI_GITHUB_TOKEN` | Explicit opt-in. Imported as a `github` key whenever it is set, from any environment. |
| `GITHUB_TOKEN` | Imported **only** when `GITHUB_ACTIONS=true`. |
| `GH_TOKEN` | Same, used when `GITHUB_TOKEN` is absent. |
| `FREELLMAPI_GITHUB_TOKEN_SEED=off` | Turns the automatic import off; explicit `FREELLMAPI_GITHUB_TOKEN` still wins. |

Rules the import follows:

- It runs **once**, at startup, right after migrations and the declarative config. A `keys` entry for `github` therefore wins over the environment.
- It never overwrites an existing `github` key row — not even a **disabled** one. Turning the platform off in the dashboard is not undone by the next boot.
- The token is encrypted with the same key material as every other credential (`ENCRYPTION_KEY`), and the startup log line names the variable, never the token.
- Nothing is imported when the variable is absent: a generic `GITHUB_TOKEN` on a developer machine is left alone, because it usually belongs to `git` or `gh` rather than to this gateway.

Because an Actions token dies with the job, a long-running gateway should use a PAT (or a GitHub App installation token) instead and let the health pass keep it honest.

## How the token is validated

`GET /models` on the inference host is not a credential check — it is also where the retired service answered `200 OK`. `GitHubProvider` validates against the REST API instead:

```
GET https://api.github.com/user
Authorization: Bearer <token>
Accept: application/vnd.github+json
X-GitHub-Api-Version: 2026-03-10
User-Agent: FreeLLMAPI/1.0
```

| Response | Verdict | What the key row shows |
| --- | --- | --- |
| `200` | valid | `healthy` |
| `401` | invalid credentials | the GitHub message for the token |
| `403` + `X-GitHub-SSO` | token is valid but not SSO-authorized | the authorization URL from the header (**valid for one hour**) |
| `403` + `X-RateLimit-Remaining: 0` | inconclusive — GitHub is refusing the probe, not the token | an error, without counting toward auto-disable |
| `403` / `404` otherwise | the token cannot use the endpoint | a hint about the **Models** permission and SSO |
| `5xx` | inconclusive | an error, without counting toward auto-disable |

A `404` is the documented answer for "you may not see this", which is why a permission problem must not be reported as "invalid token".

Failed-login throttling applies here too: several invalid credentials in a short window make GitHub refuse **all** authentication for that user for a while, including valid tokens. A burst of `403`s after a token rotation is usually this, not a broken key — wait it out.

## Failure codes you will actually see

- **`200 OK` in plain text with no JSON** — the retired inference host. GitHub retired the service on 30 July 2026 and answered every path with that placeholder, which made every key look healthy while every generation was empty (#1557). The adapter detects it and fails the request explicitly, so the fallback chain moves on and the dashboard does not show a healthy-but-dead key.
- **`404 Not Found` / `403 Forbidden` on a request** — missing permission, an unscoped classic token, or an SSO organization that has not authorized the token. For SSO, `X-GitHub-SSO` carries the authorization URL (one hour). When a multi-org query is only partly authorized, the header looks like `partial-results; organizations=21955855,20582480`.
- **`401 Unauthorized`** — expired, revoked, or malformed token. Actions tokens expire with the job.
- **`403` after repeated bad credentials** — the temporary auth block described above.
- **Username/password authentication is not supported** and fails with a 4xx.

## Rate limits

An authenticated request gets a higher hourly allowance than an anonymous one, and the token's own permissions decide which endpoints answer. The response headers (`X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`, `X-RateLimit-Resource`) are the authoritative numbers — see [Rate limits for the REST API](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api). FreeLLMAPI's own per-key accounting (`PROVIDER_DAILY_REQUEST_CAP_GITHUB`, `PROVIDER_TIMEOUT_GITHUB`) sits in front of that and is described in [02-quotas-and-cooldowns.md](02-quotas-and-cooldowns.md).

## Keeping the token safe

A token acts as your identity, limited only by its scopes or permissions. Prefer fine-grained tokens with the narrowest permission set, keep them out of logs (this repo redacts `github_pat_…` and `ghp_…` patterns in `lib/log-redaction.ts`), rotate on a schedule, and revoke immediately if a token is exposed. `ENCRYPTION_KEY` protects the stored copy — treat it like the tokens themselves.

## Status and caveats

The provider is registered so the credential path works: a token can be stored, validated and health-checked, and models can be added manually or arrive through the hosted catalog. Whether the **inference** host serves traffic is GitHub's call — if `models.github.ai` still answers `OK`, every generation fails with the explicit error above instead of returning an empty completion. Point `GITHUB_MODELS_BASE_URL` at an endpoint that still serves the API (for example a GitHub Enterprise Server deployment running its own models surface) to use the adapter against it, and adjust `GITHUB_API_BASE_URL` so the credential probe hits the matching REST host.

## Related

- [01-supported-platforms.md](01-supported-platforms.md) — the full platform table
- [03-adding-a-new-provider.md](03-adding-a-new-provider.md) — adapter contract and the tests a provider ships with
- [`server/src/providers/github.ts`](../../../server/src/providers/github.ts) — the adapter
- [`server/src/services/github-token.ts`](../../../server/src/services/github-token.ts) — the Actions/env import
- GitHub docs: [Authentication for the REST API](https://docs.github.com/en/rest/authentication/authenticating-to-the-rest-api), [Managing personal access tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
