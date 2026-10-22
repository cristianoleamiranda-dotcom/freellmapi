// Migration: give back the GitHub keys the removal migration took away
// Created: 2026-10-22
//
// DOWN: reversible (deletes exactly the rows this migration restored)
//
// 20261017_000002 removed the GitHub Models provider and, with it, every
// api_keys row for platform 'github'. It stashed the deleted rows in the
// settings table under 'migration_github_removed_rows' so its own DOWN could
// put them back — but the keys themselves never returned to a live install.
//
// The provider is registered again (server/src/providers/github.ts): the
// credential is a GitHub token that is validated against api.github.com, so a
// stored token is useful on its own regardless of what the inference host is
// doing. Restoring the keys saves every existing install from re-pasting a PAT
// it already gave us.
//
// Only api_keys is restored. Models, embeddings, media rows, overrides, chain
// entries and profile pins stay deleted on purpose: those describe an endpoint
// that GitHub retired, and reviving them would put dead routes back in the
// fallback chain — the exact failure #1557 was filed about.

import type { Db } from '../types.js';

export const REMOVED_ROWS_SETTING = 'migration_github_removed_rows';
export const RESTORED_IDS_SETTING = 'migration_github_restored_key_ids';

type Row = Record<string, unknown>;

/** Columns the live schema actually has. The stash was written by an older
 *  schema, and later migrations add columns (base_url, last_healthy_at, …);
 *  inserting an unknown one would fail the whole upgrade. */
function apiKeyColumns(db: Db): Set<string> {
  const rows = db.prepare('PRAGMA table_info(api_keys)').all() as { name: string }[];
  return new Set(rows.map(row => row.name));
}

function decode(row: Row): Row {
  const out: Row = {};
  for (const [key, value] of Object.entries(row)) {
    const tagged = value as { $buffer?: string } | null;
    out[key] = tagged && typeof tagged === 'object' && typeof tagged.$buffer === 'string'
      ? Buffer.from(tagged.$buffer, 'base64')
      : value;
  }
  return out;
}

function readSetting<T>(db: Db, key: string): T | null {
  const row = db.prepare('SELECT value FROM settings WHERE key = ?').get(key) as { value: string } | undefined;
  if (!row) return null;
  try {
    return JSON.parse(row.value) as T;
  } catch {
    return null;
  }
}

export function up(db: Db): void {
  const table = db.prepare("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'api_keys'").get();
  if (!table) return;

  // No stash means 20261017_000002 never ran (or already rolled back): there is
  // nothing of ours to do, and DOWN must stay a no-op.
  const stashed = readSetting<{ api_keys?: Row[] }>(db, REMOVED_ROWS_SETTING);
  if (stashed === null) return;
  const rows = stashed.api_keys ?? [];

  const allowed = apiKeyColumns(db);
  const restored: number[] = [];

  for (const raw of rows) {
    const row = decode(raw);
    const cols = Object.keys(row).filter(col => allowed.has(col));
    // Without a platform there is nothing to restore, and NOT NULL columns the
    // stash predates must be filled by the schema itself rather than guessed.
    if (!cols.includes('platform') || row.platform !== 'github') continue;
    const inserted = db.prepare(
      `INSERT OR IGNORE INTO api_keys (${cols.join(', ')}) VALUES (${cols.map(() => '?').join(', ')})`,
    ).run(...cols.map(col => row[col] as never));
    if (inserted.changes > 0) restored.push(Number(inserted.lastInsertRowid));
  }

  // Written even when nothing needed restoring (an empty list). It is the only
  // record that this migration ran, so DOWN always has something of its own to
  // undo instead of silently doing nothing on a database that had no keys.
  db.prepare(`
    INSERT INTO settings (key, value) VALUES (?, ?)
    ON CONFLICT(key) DO UPDATE SET value = excluded.value
  `).run(RESTORED_IDS_SETTING, JSON.stringify(restored));
}

export function down(db: Db): void {
  const ids = readSetting<number[]>(db, RESTORED_IDS_SETTING);
  if (ids === null) return;
  for (const id of ids) {
    db.prepare("DELETE FROM api_keys WHERE id = ? AND platform = 'github'").run(id);
  }
  db.prepare('DELETE FROM settings WHERE key = ?').run(RESTORED_IDS_SETTING);
}
