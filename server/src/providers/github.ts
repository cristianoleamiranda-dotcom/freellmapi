import { OpenAICompatProvider } from './openai-compat.js';
import { providerHttpError, type KeyValidationResult, type ProviderFetchOptions } from './base.js';
import { bearerAuthHeader } from '../lib/credential.js';

/** Inference host. Overridable for GitHub Enterprise Server installs that
 *  front their own models endpoint. */
const DEFAULT_MODELS_BASE_URL = 'https://models.github.ai/inference';
/** REST host. Only used for credential checks — never for generation. */
const DEFAULT_API_BASE_URL = 'https://api.github.com';

/**
 * The REST API version this adapter pins (docs: "Autenticación en la API
 * REST"). Every request that carries a token sends it, so GitHub answers with
 * the documented shapes rather than an unpinned default. Bump only alongside
 * a matching review of the endpoints used here.
 */
export const GITHUB_API_VERSION = '2026-03-10';

/** Shared by the credential probe and the generation calls. `User-Agent` is
 *  not optional: api.github.com rejects requests without one. */
const BASE_HEADERS: Record<string, string> = {
  Accept: 'application/vnd.github+json',
  'X-GitHub-Api-Version': GITHUB_API_VERSION,
  'User-Agent': 'FreeLLMAPI/1.0',
};

function envUrl(name: string, fallback: string): string {
  const raw = process.env[name]?.trim();
  return (raw || fallback).replace(/\/+$/, '');
}

/**
 * GitHub Models answering 200 with the literal body `OK` and no JSON.
 *
 * This is the retirement banner GitHub started returning on 30 July 2026
 * (#549). It reads as a successful response to any status-code-only check, so
 * every key looked healthy while every generation was empty (#1557). The
 * adapter keeps the check even now that the provider is back, because the
 * placeholder is cheap to detect and expensive to miss: an upstream that parks
 * its endpoint again must surface as a failed request, never as a blank reply.
 */
export function isRetiredModelsResponse(text: string | null | undefined): boolean {
  return (text ?? '').trim().toLowerCase() === 'ok';
}

/**
 * GitHub Models — OpenAI-compatible inference behind a GitHub token.
 *
 * Authentication (see docs/en/providers/05-github-models.md) is a plain
 * `Authorization: Bearer <token>`, which is exactly what the OpenAI-compat base
 * class already sends. Three things are not stock, and they are the reason this
 * is a subclass:
 *
 * 1. **Validation.** `GET {inference}/models` is useless as a credential check:
 *    it is also where the retired service answered `200 OK`, and it says
 *    nothing about scopes. Validation therefore goes to `GET /user` on
 *    api.github.com, where a bad token is a real `401`, a token from another
 *    host is a `401`, and a token that is valid but not authorized for an SSO
 *    organization answers `403` with an `X-GitHub-SSO` header naming the
 *    authorization URL (valid for one hour).
 * 2. **Permission errors.** Per GitHub's docs, a token without the needed
 *    permission gets `404` or `403`, not `401`. Those must read as "this token
 *    cannot use the endpoint" with an actionable hint, not as "invalid key".
 * 3. **The retirement banner.** See isRetiredModelsResponse().
 */
export class GitHubProvider extends OpenAICompatProvider {
  private readonly apiBaseUrl: string;

  constructor(opts: { modelsBaseUrl?: string; apiBaseUrl?: string; timeoutMs?: number } = {}) {
    super({
      platform: 'github',
      name: 'GitHub Models',
      baseUrl: opts.modelsBaseUrl ?? envUrl('GITHUB_MODELS_BASE_URL', DEFAULT_MODELS_BASE_URL),
      extraHeaders: BASE_HEADERS,
      timeoutMs: opts.timeoutMs ?? 60_000,
    });
    this.apiBaseUrl = opts.apiBaseUrl ?? envUrl('GITHUB_API_BASE_URL', DEFAULT_API_BASE_URL);
  }

  /** Headers for the api.github.com credential probe. Anonymous sentinels send
   *  no Authorization header at all (an empty Bearer is itself a 401). */
  private apiHeaders(token: string): Record<string, string> {
    return { ...BASE_HEADERS, ...bearerAuthHeader(token) };
  }

  /**
   * Turn a non-2xx `/user` response into a verdict.
   *
   * 401 → the token is bad (fail the key).
   * 403 with `X-GitHub-SSO` → the token is fine but not SSO-authorized; the
   *   header carries the URL to authorize it (fail with that URL, since it is
   *   the only thing the operator can act on).
   * 403 with the rate-limit counter at zero → inconclusive: GitHub is refusing
   *   the probe, not the credential. Thrown so health records an error without
   *   counting it toward auto-disable.
   * 403/404 otherwise → permission failure (fine-grained tokens need
   *   `models:read`; classic tokens need no scope for read-only user data, but
   *   an SSO-enforced org answers 404 for unauthorized tokens).
   * 5xx → inconclusive, same as the rate-limit case.
   */
  private async userProbeVerdict(res: Response): Promise<KeyValidationResult> {
    const detail = await this.githubErrorMessage(res);

    if (res.status === 401) {
      return { valid: false, error: `GitHub rejected the token (HTTP 401)${detail ? `: ${detail}` : ''}` };
    }

    const sso = res.headers?.get('x-github-sso');
    if (sso) {
      const url = /url=(\S+)/.exec(sso)?.[1];
      return {
        valid: false,
        error: url
          ? `GitHub token is valid but not authorized for SAML SSO; authorize it here (link valid for one hour): ${url}`
          : `GitHub token is valid but not authorized for SAML SSO (${sso}); authorize it in GitHub's SSO settings`,
      };
    }

    if (res.status === 403 && res.headers?.get('x-ratelimit-remaining') === '0') {
      throw providerHttpError(res, `GitHub rate limit reached while validating the token${detail ? `: ${detail}` : ''}`);
    }

    if (res.status === 403 || res.status === 404) {
      return {
        valid: false,
        error: `GitHub token cannot use this endpoint (HTTP ${res.status})${detail ? `: ${detail}` : ''}. `
          + 'A fine-grained token needs the "Models" permission (read); a token from another host or an SSO-protected organization it was not authorized for answers the same way.',
      };
    }

    if (res.status >= 500) {
      throw providerHttpError(res, `GitHub returned HTTP ${res.status} while validating the token; the credential was not checked`);
    }

    return this.validationResult(res);
  }

  /** GitHub errors are `{"message": "...", "documentation_url": "..."}`; OAuth
   *  errors use `error`/`error_description`. Read whichever is present. */
  private async githubErrorMessage(res: Response): Promise<string | null> {
    let body: any = null;
    try {
      if (typeof (res as any).json === 'function') body = await res.json();
    } catch {
      // A status alone is still more useful than nothing.
    }
    const candidates = [body?.message, body?.error_description, body?.error, res.statusText];
    const found = candidates.find((v) => typeof v === 'string' && v.trim().length > 0);
    return found ? found.trim() : null;
  }

  async validateKey(apiKey: string): Promise<KeyValidationResult> {
    const res = await this.fetchWithTimeout(
      `${this.apiBaseUrl}/user`,
      { method: 'GET', headers: this.apiHeaders(apiKey) },
      15_000,
      { timeoutBounds: 'request' },
    );
    if (res.ok) return true;
    return this.userProbeVerdict(res);
  }

  /**
   * Catch the "200 OK, no body content" retirement banner before the base class
   * turns it into a generic non-JSON error.
   *
   * Only chat responses are inspected, and only when the upstream did not claim
   * JSON or SSE — i.e. exactly the case that is about to fail anyway. The body
   * is read through `clone()` so the caller still gets an untouched response
   * when the content is a legitimate (if unexpected) JSON shapes.
   */
  protected async fetchWithTimeout(
    url: string,
    init: RequestInit,
    timeoutMs?: number,
    fetchOpts?: ProviderFetchOptions,
  ): Promise<Response> {
    const res = await super.fetchWithTimeout(url, init, timeoutMs, fetchOpts);
    if (!url.includes('/chat/completions') || !res.ok) return res;

    const contentType = (res.headers?.get?.('content-type') ?? '').toLowerCase();
    if (contentType.includes('json') || contentType.includes('event-stream')) return res;
    if (typeof (res as any).clone !== 'function') return res;

    const text = await res.clone().text().catch(() => '');
    if (!isRetiredModelsResponse(text)) return res;

    throw providerHttpError(
      res,
      'GitHub Models is unavailable: the endpoint answers every request with 200 "OK" in plain text, '
      + 'which is the placeholder GitHub returned after retiring the service on 30 July 2026. '
      + 'Remove or disable the GitHub Models keys, or point GITHUB_MODELS_BASE_URL at an endpoint that still serves the API.',
      text,
    );
  }
}
