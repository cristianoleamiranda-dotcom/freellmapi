import Database from 'better-sqlite3';
import { afterEach, describe, expect, it } from 'vitest';
import { runMigrations } from '../../../db/migrate/runner.js';
import { up as removeGitHub, down as undoRemoveGitHub } from '../../../db/migrations/20261017_000002_remove_github_provider.js';
import {
  up as restoreGitHubKeys,
  down as undoRestoreGitHubKeys,
  RESTORED_IDS_SETTING,
  REMOVED_ROWS_SETTING,
} from '../../../db/migrations/20261022_000001_restore_github_keys.js';

// 20261017_000002 took the GitHub keys away. The provider is registered again,
// so the token (a real GitHub credential, validated against api.github.com) is
// worth giving back — while the model, chain and profile rows that pointed at
// the retired host stay gone.

const dbs: Database.Database[] = [];
afterEach(() => {
  for (const db of dbs.splice(0)) db.close();
});

async function migratedDb(): Promise<Database.Database> {
  const db = new Database(':memory:');
  dbs.push(db);
  await runMigrations(db, 'up');
  return db;
}

function counts(db: Database.Database) {
  const count = (sql: string) => (db.prepare(sql).get() as { n: number }).n;
  return {
    keys: count("SELECT COUNT(*) AS n FROM api_keys WHERE platform = 'github'"),
    models: count("SELECT COUNT(*) AS n FROM models WHERE platform = 'github'"),
    chain: count("SELECT COUNT(*) AS n FROM fallback_config WHERE model_db_id IN (SELECT id FROM models WHERE platform = 'github')"),
  };
}

describe('restore_github_keys migration', () => {
  it('gives back the stashed github key only, and DOWN removes exactly that row', async () => {
    const db = await migratedDb();

    // The state 20261017_000002 was written for: a key, a custom model and a
    // chain entry pointing at it.
    const keyId = Number(db.prepare(`
      INSERT INTO api_keys (platform, label, encrypted_key, iv, auth_tag, status, enabled)
      VALUES ('github', 'gh', 'enc', 'iv', 'tag', 'healthy', 1)
    `).run().lastInsertRowid);
    const modelId = Number(db.prepare(`
      INSERT INTO models (platform, model_id, display_name, intelligence_rank, speed_rank, enabled, source)
      VALUES ('github', 'openai/gpt-4.1', 'GPT-4.1', 20, 7, 1, 'user')
    `).run().lastInsertRowid);
    db.prepare('INSERT INTO fallback_config (model_db_id, priority, enabled) VALUES (?, 999, 1)').run(modelId);

    removeGitHub(db);
    expect(counts(db)).toEqual({ keys: 0, models: 0, chain: 0 });

    restoreGitHubKeys(db);
    expect(counts(db)).toEqual({ keys: 1, models: 0, chain: 0 });
    expect(db.prepare("SELECT id, label, status, enabled FROM api_keys WHERE platform = 'github'").get())
      .toEqual({ id: keyId, label: 'gh', status: 'healthy', enabled: 1 });
    expect(db.prepare('SELECT value FROM settings WHERE key = ?').get(RESTORED_IDS_SETTING))
      .toEqual({ value: JSON.stringify([keyId]) });
    expect(db.pragma('foreign_key_check')).toEqual([]);

    undoRestoreGitHubKeys(db);
    expect(counts(db).keys).toBe(0);
    expect(db.prepare('SELECT value FROM settings WHERE key = ?').get(RESTORED_IDS_SETTING)).toBeUndefined();
    // Undoing the restore leaves the older migration's own DOWN working.
    undoRemoveGitHub(db);
    expect(counts(db)).toEqual({ keys: 1, models: 1, chain: 1 });
  });

  it('records an empty marker when the stash holds no keys, and DOWN removes it', async () => {
    const db = await migratedDb();

    // The migration already ran once during the upgrade: the stash exists (the
    // removal migration always writes it) but held no github keys, so the
    // marker is an empty list rather than nothing at all.
    const marker = () => db.prepare('SELECT value FROM settings WHERE key = ?').get(RESTORED_IDS_SETTING);
    expect(marker()).toEqual({ value: '[]' });

    restoreGitHubKeys(db);
    restoreGitHubKeys(db);
    expect(counts(db).keys).toBe(0);
    expect(marker()).toEqual({ value: '[]' });

    const otherBefore = (db.prepare("SELECT COUNT(*) AS n FROM api_keys WHERE platform != 'github'").get() as { n: number }).n;
    undoRestoreGitHubKeys(db);
    expect(marker()).toBeUndefined();
    expect(counts(db).keys).toBe(0);
    expect((db.prepare("SELECT COUNT(*) AS n FROM api_keys WHERE platform != 'github'").get() as { n: number }).n)
      .toBe(otherBefore);
    // Second DOWN is a no-op, not an error.
    undoRestoreGitHubKeys(db);
  });

  it('does nothing at all when the removal migration never ran', async () => {
    const db = await migratedDb();
    db.prepare('DELETE FROM settings WHERE key = ?').run(REMOVED_ROWS_SETTING);
    db.prepare('DELETE FROM settings WHERE key = ?').run(RESTORED_IDS_SETTING);

    restoreGitHubKeys(db);
    expect(db.prepare('SELECT value FROM settings WHERE key = ?').get(RESTORED_IDS_SETTING)).toBeUndefined();
    expect(counts(db).keys).toBe(0);
  });
});
