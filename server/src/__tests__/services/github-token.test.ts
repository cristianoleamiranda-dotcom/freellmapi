import { describe, it, expect, beforeAll, beforeEach, vi } from 'vitest';
import { initDb, getDb } from '../../db/index.js';
import { decrypt } from '../../lib/crypto.js';
import {
  resolveGitHubTokenSource,
  seedGitHubTokenFromEnv,
  GITHUB_ENV_TOKEN_LABEL,
} from '../../services/github-token.js';

// A gateway running inside GitHub Actions already has a GitHub token in its
// environment. The import is deliberately narrow: the built-in GITHUB_TOKEN is
// only claimed inside Actions, an explicit FREELLMAPI_GITHUB_TOKEN always wins,
// and an existing key row is never touched.

beforeAll(() => {
  process.env.ENCRYPTION_KEY = '0'.repeat(64);
  initDb(':memory:');
});

beforeEach(() => {
  getDb().prepare("DELETE FROM api_keys WHERE platform = 'github'").run();
  vi.spyOn(console, 'log').mockImplementation(() => {});
  vi.spyOn(console, 'warn').mockImplementation(() => {});
});

describe('resolveGitHubTokenSource', () => {
  it('uses FREELLMAPI_GITHUB_TOKEN from any environment', () => {
    expect(resolveGitHubTokenSource({ FREELLMAPI_GITHUB_TOKEN: 'pat-explicit' }))
      .toEqual({ token: 'pat-explicit', variable: 'FREELLMAPI_GITHUB_TOKEN' });
  });

  it('ignores a generic GITHUB_TOKEN outside GitHub Actions', () => {
    expect(resolveGitHubTokenSource({ GITHUB_TOKEN: 'ci-token', GH_TOKEN: 'ci-token' })).toBeNull();
    // Present but false: still not Actions.
    expect(resolveGitHubTokenSource({ GITHUB_ACTIONS: 'false', GITHUB_TOKEN: 'ci-token' })).toBeNull();
  });

  it('claims the built-in token inside Actions, GITHUB_TOKEN before GH_TOKEN', () => {
    expect(resolveGitHubTokenSource({ GITHUB_ACTIONS: 'true', GITHUB_TOKEN: 'builtin' }))
      .toEqual({ token: 'builtin', variable: 'GITHUB_TOKEN' });
    expect(resolveGitHubTokenSource({ GITHUB_ACTIONS: 'true', GH_TOKEN: 'gh-cli' }))
      .toEqual({ token: 'gh-cli', variable: 'GH_TOKEN' });
  });

  it('honours the off switch for the automatic import', () => {
    expect(resolveGitHubTokenSource({
      GITHUB_ACTIONS: 'true',
      GITHUB_TOKEN: 'builtin',
      FREELLMAPI_GITHUB_TOKEN_SEED: 'off',
    })).toBeNull();
    // The explicit variable still wins when the import is off.
    expect(resolveGitHubTokenSource({
      GITHUB_ACTIONS: 'true',
      GITHUB_TOKEN: 'builtin',
      FREELLMAPI_GITHUB_TOKEN_SEED: 'off',
      FREELLMAPI_GITHUB_TOKEN: 'pat-explicit',
    })).toEqual({ token: 'pat-explicit', variable: 'FREELLMAPI_GITHUB_TOKEN' });
  });
});

describe('seedGitHubTokenFromEnv', () => {
  function githubKeys() {
    return getDb().prepare("SELECT * FROM api_keys WHERE platform = 'github'").all() as Array<Record<string, unknown>>;
  }

  it('stores the Actions token encrypted, under a label that names its source', () => {
    const id = seedGitHubTokenFromEnv({ GITHUB_ACTIONS: 'true', GITHUB_TOKEN: 'builtin-token' });
    expect(id).toBeTypeOf('number');

    const rows = githubKeys();
    expect(rows).toHaveLength(1);
    expect(rows[0].label).toBe(GITHUB_ENV_TOKEN_LABEL);
    expect(rows[0].status).toBe('unknown');
    expect(rows[0].enabled).toBe(1);
    expect(decrypt(
      rows[0].encrypted_key as string,
      rows[0].iv as string,
      rows[0].auth_tag as string,
    )).toBe('builtin-token');
  });

  it('never overwrites an existing key, not even a disabled one', () => {
    getDb().prepare(`
      INSERT INTO api_keys (platform, label, encrypted_key, iv, auth_tag, status, enabled)
      VALUES ('github', 'mine', 'enc', 'iv', 'tag', 'healthy', 0)
    `).run();

    expect(seedGitHubTokenFromEnv({ GITHUB_ACTIONS: 'true', GITHUB_TOKEN: 'builtin-token' })).toBeNull();
    expect(githubKeys()).toHaveLength(1);
    expect(githubKeys()[0].label).toBe('mine');
    expect(githubKeys()[0].enabled).toBe(0);
  });

  it('does nothing when no token is available', () => {
    expect(seedGitHubTokenFromEnv({})).toBeNull();
    expect(seedGitHubTokenFromEnv({ GITHUB_TOKEN: 'not-ours' })).toBeNull();
    expect(githubKeys()).toHaveLength(0);
  });

  it('imports only once per boot sequence', () => {
    expect(seedGitHubTokenFromEnv({ GITHUB_ACTIONS: 'true', GITHUB_TOKEN: 'builtin-token' })).toBeTypeOf('number');
    expect(seedGitHubTokenFromEnv({ GITHUB_ACTIONS: 'true', GITHUB_TOKEN: 'builtin-token' })).toBeNull();
    expect(githubKeys()).toHaveLength(1);
  });
});
