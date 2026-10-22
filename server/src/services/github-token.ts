import { getDb } from '../db/index.js';
import { encrypt } from '../lib/crypto.js';

/**
 * Boot-time import of the GitHub token a CI job already has.
 *
 * GitHub Actions hands every workflow a short-lived `GITHUB_TOKEN` through the
 * `secrets` context, and the documented way to use it is an environment
 * variable (`GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}`) — that is the pattern the
 * "Autenticación en la API REST" docs recommend over minting a long-lived PAT.
 * A gateway running inside a workflow should therefore be able to pick the
 * token up instead of asking the operator to paste it.
 *
 * Deliberately narrow, because a generic `GITHUB_TOKEN` in a shell or a CI job
 * usually belongs to git/gh, not to this gateway:
 *
 *   - `FREELLMAPI_GITHUB_TOKEN` is always used when set (explicit opt-in).
 *   - `GITHUB_TOKEN` / `GH_TOKEN` are only imported when GitHub Actions is
 *     actually running this process (`GITHUB_ACTIONS=true`).
 *   - `FREELLMAPI_GITHUB_TOKEN_SEED=off` disables the automatic import while
 *     leaving every other path alone.
 *   - An existing `github` key row always wins — including a disabled one, so
 *     turning the platform off is not undone at the next boot.
 */

export const GITHUB_ENV_TOKEN_LABEL = 'GITHUB_TOKEN (env)';

export interface GitHubTokenSource {
  token: string;
  /** Name of the variable it came from, for logs. Never log the token. */
  variable: 'FREELLMAPI_GITHUB_TOKEN' | 'GITHUB_TOKEN' | 'GH_TOKEN';
}

function isOff(raw: string | undefined): boolean {
  const value = raw?.trim().toLowerCase();
  return value === 'off' || value === '0' || value === 'false' || value === 'no';
}

/** Pure resolver: which env var (if any) should provide the GitHub key. */
export function resolveGitHubTokenSource(env: NodeJS.ProcessEnv = process.env): GitHubTokenSource | null {
  const explicit = env.FREELLMAPI_GITHUB_TOKEN?.trim();
  if (explicit) return { token: explicit, variable: 'FREELLMAPI_GITHUB_TOKEN' };

  if (isOff(env.FREELLMAPI_GITHUB_TOKEN_SEED)) return null;

  // Outside Actions the built-in token is not ours to claim.
  const inActions = env.GITHUB_ACTIONS?.trim().toLowerCase() === 'true';
  if (!inActions) return null;

  const actionsToken = env.GITHUB_TOKEN?.trim();
  if (actionsToken) return { token: actionsToken, variable: 'GITHUB_TOKEN' };
  const ghToken = env.GH_TOKEN?.trim();
  if (ghToken) return { token: ghToken, variable: 'GH_TOKEN' };
  return null;
}

/**
 * Store the resolved token as the `github` platform key, once.
 *
 * Returns the new key id, or null when nothing was imported. Never throws: a
 * broken env import must not stop the server from booting (the same rule the
 * declarative-config loader follows, #600).
 */
export function seedGitHubTokenFromEnv(env: NodeJS.ProcessEnv = process.env): number | null {
  try {
    const source = resolveGitHubTokenSource(env);
    if (!source) return null;

    const db = getDb();
    const existing = db.prepare("SELECT id FROM api_keys WHERE platform = 'github' LIMIT 1").get();
    if (existing) return null;

    const { encrypted, iv, authTag } = encrypt(source.token);
    const inserted = db.prepare(`
      INSERT INTO api_keys (platform, label, encrypted_key, iv, auth_tag, status, enabled)
      VALUES ('github', ?, ?, ?, ?, 'unknown', 1)
    `).run(GITHUB_ENV_TOKEN_LABEL, encrypted, iv, authTag);

    console.log(
      `[github] imported ${source.variable} as a GitHub Models key (id ${Number(inserted.lastInsertRowid)}); `
      + 'run a health check to confirm it can reach the inference host',
    );
    return Number(inserted.lastInsertRowid);
  } catch (err) {
    console.warn(`[github] could not import the env token: ${err instanceof Error ? err.message : String(err)}`);
    return null;
  }
}
