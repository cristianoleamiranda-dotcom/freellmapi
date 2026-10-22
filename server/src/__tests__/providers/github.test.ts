import { describe, it, expect, vi, afterEach } from 'vitest';
import { GitHubProvider, isRetiredModelsResponse, GITHUB_API_VERSION } from '../../providers/github.js';

// GitHub Models is authenticated with a GitHub token. These tests pin the two
// behaviours that differ from a stock OpenAI-compatible endpoint: the credential
// probe goes to api.github.com/user (not the inference host), and the retired
// host's `200 "OK"` placeholder fails the request instead of looking healthy.

const provider = () => new GitHubProvider({
  apiBaseUrl: 'https://api.test',
  modelsBaseUrl: 'https://models.test/inference',
  timeoutMs: 5_000,
});

function jsonResponse(body: unknown, init: ResponseInit = { status: 200 }): Response {
  return new Response(JSON.stringify(body), {
    ...init,
    headers: { 'content-type': 'application/json', ...(init.headers as Record<string, string> | undefined) },
  });
}

afterEach(() => {
  vi.restoreAllMocks();
});

describe('isRetiredModelsResponse', () => {
  it('matches the exact placeholder GitHub answered with after the retirement', () => {
    expect(isRetiredModelsResponse('OK')).toBe(true);
    expect(isRetiredModelsResponse(' ok \n')).toBe(true);
    expect(isRetiredModelsResponse('')).toBe(false);
    expect(isRetiredModelsResponse(undefined)).toBe(false);
    // A real completion that happens to be short is not the banner.
    expect(isRetiredModelsResponse('OK, here is the answer')).toBe(false);
  });
});

describe('GitHubProvider.validateKey', () => {
  it('probes api.github.com/user with the documented headers, never the inference host', async () => {
    let capturedUrl = '';
    let capturedHeaders: Record<string, string> = {};
    vi.spyOn(global, 'fetch').mockImplementation(async (url, init) => {
      capturedUrl = String(url);
      capturedHeaders = (init as RequestInit).headers as Record<string, string>;
      return jsonResponse({ login: 'octocat' });
    });

    await expect(provider().validateKey('ghp_token')).resolves.toBe(true);

    expect(capturedUrl).toBe('https://api.test/user');
    expect(capturedHeaders.Authorization).toBe('Bearer ghp_token');
    expect(capturedHeaders.Accept).toBe('application/vnd.github+json');
    expect(capturedHeaders['X-GitHub-Api-Version']).toBe(GITHUB_API_VERSION);
    expect(capturedHeaders['User-Agent']).toBeTruthy();
  });

  it('reports a 401 as an invalid token with GitHub’s own message', async () => {
    vi.spyOn(global, 'fetch').mockResolvedValue(
      jsonResponse({ message: 'Bad credentials' }, { status: 401 }),
    );

    const result = await provider().validateKey('bad');
    expect(result).toEqual({ valid: false, error: 'GitHub rejected the token (HTTP 401): Bad credentials' });
  });

  it('surfaces the SAML SSO authorization URL from X-GitHub-SSO', async () => {
    vi.spyOn(global, 'fetch').mockResolvedValue(
      jsonResponse(
        { message: 'Resource protected by organization SAML enforcement' },
        {
          status: 403,
          headers: {
            'x-github-sso': 'required; url=https://github.com/orgs/acme/sso?authorization_request=abc',
          },
        },
      ),
    );

    const result = await provider().validateKey('ghp_token');
    expect(result.valid).toBe(false);
    expect((result as { error: string }).error).toContain('SAML SSO');
    expect((result as { error: string }).error).toContain('https://github.com/orgs/acme/sso?authorization_request=abc');
  });

  it('treats a 403 caused by the rate limit as inconclusive, not as a bad key', async () => {
    vi.spyOn(global, 'fetch').mockResolvedValue(
      jsonResponse(
        { message: 'API rate limit exceeded' },
        { status: 403, headers: { 'x-ratelimit-remaining': '0', 'x-ratelimit-limit': '5000' } },
      ),
    );

    // Thrown so health records an error without auto-disabling the key.
    await expect(provider().validateKey('ghp_token')).rejects.toThrow(/rate limit/i);
  });

  it('explains a 404 as a permission problem instead of an invalid token', async () => {
    vi.spyOn(global, 'fetch').mockResolvedValue(
      jsonResponse({ message: 'Not Found' }, { status: 404 }),
    );

    const result = await provider().validateKey('github_pat_finegrained');
    expect(result.valid).toBe(false);
    const error = (result as { error: string }).error;
    expect(error).toContain('HTTP 404');
    expect(error).toContain('Models');
    expect(error).not.toContain('invalid token');
  });

  it('keeps a 5xx inconclusive rather than blaming the credential', async () => {
    vi.spyOn(global, 'fetch').mockResolvedValue(
      jsonResponse({ message: 'Server Error' }, { status: 502 }),
    );

    await expect(provider().validateKey('ghp_token')).rejects.toThrow(/502/);
  });
});

describe('GitHubProvider chat completion', () => {
  it('fails a retired endpoint that answers 200 with a plain-text OK', async () => {
    vi.spyOn(global, 'fetch').mockResolvedValue(
      new Response('OK', { status: 200, headers: { 'content-type': 'text/plain' } }),
    );

    await expect(
      provider().chatCompletion('ghp_token', [{ role: 'user', content: 'hi' }], 'openai/gpt-4.1'),
    ).rejects.toThrow(/GitHub Models is unavailable/);
  });

  it('returns a normal JSON completion untouched', async () => {
    vi.spyOn(global, 'fetch').mockResolvedValue(
      jsonResponse({
        id: 'chatcmpl-1',
        object: 'chat.completion',
        created: 1,
        model: 'openai/gpt-4.1',
        choices: [{ index: 0, message: { role: 'assistant', content: 'hello' }, finish_reason: 'stop' }],
        usage: { prompt_tokens: 1, completion_tokens: 1, total_tokens: 2 },
      }),
    );

    const res = await provider().chatCompletion('ghp_token', [{ role: 'user', content: 'hi' }], 'openai/gpt-4.1');
    expect(res.choices[0].message.content).toBe('hello');
    expect(res._routed_via).toEqual({ platform: 'github', model: 'openai/gpt-4.1' });
  });
});
