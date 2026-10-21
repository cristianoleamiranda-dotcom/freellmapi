import {
  cpSync,
  existsSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  rmSync,
  statSync,
  writeFileSync,
} from 'node:fs';
import { basename, dirname, join, relative, resolve } from 'node:path';

export const SKIP_DIRS = new Set(['.git', 'node_modules', 'dist', 'build', '.cache', '.next', '.turbo']);
export const SKIP_FILES = new Set(['.DS_Store', 'Thumbs.db']);
export const MAX_ASSET_BYTES = 5 * 1024 * 1024;

export function readText(path) {
  return readFileSync(path, 'utf8');
}

export function readJson(path, fallback = null) {
  try {
    return JSON.parse(readFileSync(path, 'utf8'));
  } catch {
    return fallback;
  }
}

export function writeJson(path, value) {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, `${JSON.stringify(value, null, 2)}\n`);
}

export function ensureDir(path) {
  mkdirSync(path, { recursive: true });
}

export function walk(dir) {
  const out = [];
  if (!existsSync(dir)) return out;
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const full = join(dir, entry.name);
    if (entry.isDirectory()) {
      if (SKIP_DIRS.has(entry.name)) continue;
      out.push(...walk(full));
    } else if (entry.isFile()) {
      if (SKIP_FILES.has(entry.name)) continue;
      out.push(full);
    }
  }
  return out;
}

export function dirStats(dir) {
  const files = walk(dir);
  let bytes = 0;
  for (const f of files) bytes += statSync(f).size;
  return { files: files.length, bytes };
}

/** Copia un árbol de skill omitiendo ruido y assets gigantes. */
export function copySkillTree(src, dest, { skip = [] } = {}) {
  ensureDir(dest);
  const skipped = [];
  const walkCopy = (from, to) => {
    for (const entry of readdirSync(from, { withFileTypes: true })) {
      const source = join(from, entry.name);
      const target = join(to, entry.name);
      const rel = relative(src, source);
      if (skip.includes(rel)) continue;
      if (entry.isDirectory()) {
        if (SKIP_DIRS.has(entry.name)) continue;
        ensureDir(target);
        walkCopy(source, target);
        continue;
      }
      if (!entry.isFile()) continue;
      if (SKIP_FILES.has(entry.name)) continue;
      const size = statSync(source).size;
      if (size > MAX_ASSET_BYTES) {
        skipped.push({ path: rel, bytes: size });
        continue;
      }
      cpSync(source, target);
    }
  };
  walkCopy(src, dest);
  return skipped;
}

export function slugify(value) {
  return String(value)
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 64);
}

export function isKebab(value) {
  return /^[a-z0-9]+(-[a-z0-9]+)*$/.test(value) && value.length <= 64;
}

export function detectLicense(dir) {
  const candidates = readdirSync(dir).filter((name) => /^(LICEN[CS]E|COPYING)(\.|$)/i.test(name));
  if (!candidates.length) return null;
  const file = candidates[0];
  const text = readFileSync(join(dir, file), 'utf8').slice(0, 4000);
  const kind =
    /MIT License/i.test(text)
      ? 'MIT'
      : /Apache License/i.test(text)
        ? 'Apache-2.0'
        : /BSD/i.test(text)
          ? 'BSD'
          : /GNU (GENERAL|LESSER)/i.test(text)
            ? 'GPL'
            : 'UNKNOWN';
  return { kind, file };
}

export function humanBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

export function resetDir(dir) {
  rmSync(dir, { recursive: true, force: true });
  ensureDir(dir);
}

export function repoCacheName(repo) {
  return basename(repo);
}

export function absolute(root, ...parts) {
  return resolve(root, ...parts);
}

export function writeFileSyncSafe(path, content) {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, content.endsWith('\n') ? content : `${content}\n`);
}
