#!/usr/bin/env node
// Importa las skills desde los repos del perfil, las normaliza y reconstruye
// library/. Uso:
//   node src/sync.mjs             # clona/actualiza y reconstruye
//   node src/sync.mjs --offline   # usa el cache local sin tocar la red
//   node src/sync.mjs --repo Rae  # solo un repo

import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { cpSync, existsSync, readdirSync, rmSync, statSync, writeFileSync } from 'node:fs';
import { basename, dirname, join, posix } from 'node:path';
import { fileURLToPath } from 'node:url';

import { OWNER, REPOS, LIBRARY_VERSION } from './config.mjs';
import { splitFrontmatter, stringifyFrontmatter } from './frontmatter.mjs';
import {
  copySkillTree,
  detectLicense,
  dirStats,
  ensureDir,
  humanBytes,
  isKebab,
  readText,
  resetDir,
  slugify,
  walk,
  writeJson,
} from './fs-utils.mjs';
import { writeReports } from './report.mjs';

const hubRoot = join(dirname(fileURLToPath(import.meta.url)), '..');
const cacheDir = join(hubRoot, '.cache', 'repos');
const libraryDir = join(hubRoot, 'library');
const reportsDir = join(hubRoot, 'reports');

const args = process.argv.slice(2);
const offline = args.includes('--offline');
const onlyRepo = valueOf('--repo');

function valueOf(flag) {
  const index = args.indexOf(flag);
  return index !== -1 ? args[index + 1] : null;
}

function git(cwd, ...command) {
  return execFileSync('git', command, { cwd, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] }).trim();
}

function ensureRepo(repo, branch) {
  const dir = join(cacheDir, repo);
  const url = `https://github.com/${OWNER}/${repo}.git`;
  if (existsSync(join(dir, '.git'))) {
    if (offline) return { dir, url, commit: git(dir, 'rev-parse', 'HEAD') };
    try {
      git(dir, 'fetch', '--depth', '1', 'origin', branch);
      git(dir, 'reset', '--hard', 'FETCH_HEAD');
    } catch {
      // Si el fetch falla, seguimos con lo que haya en cache.
    }
    return { dir, url, commit: git(dir, 'rev-parse', 'HEAD') };
  }
  if (offline) throw new Error(`No hay cache para ${repo} y se pidió --offline`);
  ensureDir(cacheDir);
  git(cacheDir, 'clone', '--depth', '1', '--branch', branch, url, dir);
  return { dir, url, commit: git(dir, 'rev-parse', 'HEAD') };
}

function repoSizeKb(dir) {
  try {
    const out = execFileSync('du', ['-sk', dir], { encoding: 'utf8' });
    return Number(out.split(/\s+/)[0]) || null;
  } catch {
    return null;
  }
}

function normalizeDescription(text, slug, notes) {
  let description = String(text || '').replace(/\s+/g, ' ').trim();
  if (description.length > 1024) {
    const cut = description.slice(0, 1020);
    let boundary = Math.max(cut.lastIndexOf('. '), cut.lastIndexOf('; '), cut.lastIndexOf(', '));
    if (boundary < 700) boundary = cut.lastIndexOf(' ');
    description = `${cut.slice(0, boundary).replace(/[,;:.\s]+$/, '')} …`;
    notes.push('description recortada a 1024 caracteres');
  }
  if (!description) throw new Error(`${slug}: sin descripción`);
  return description;
}

function discoverSkills(repo) {
  const root = join(repo.dir, repo.discover.root);
  if (!existsSync(root)) return [];
  return readdirSync(root, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => join(repo.discover.root, entry.name, repo.discover.file))
    .filter((path) => existsSync(join(repo.dir, path)))
    .sort()
    .map((path) => {
      const dirName = basename(dirname(path));
      const extra = repo.classify ? repo.classify(dirName) : {};
      return { source: path, slug: dirName, ...extra };
    });
}

function prepare(entry, repo, repoLicense) {
  const notes = [];
  const curatedPath = entry.curated ? join(hubRoot, entry.curated) : null;
  const sourceAbs = curatedPath || join(repo.dir, entry.source);
  if (!existsSync(sourceAbs)) throw new Error(`${repo.repo}: no existe ${entry.source}`);

  const isDirectory = statSync(sourceAbs).isDirectory();
  const filePath = isDirectory ? join(sourceAbs, 'SKILL.md') : sourceAbs;
  const text = readText(filePath);
  const { data, body: rawBody, hasFrontmatter } = splitFrontmatter(text);

  const originalName = data.name ? String(data.name) : null;
  const slug = entry.slug || (originalName ? slugify(originalName) : basename(dirname(filePath)));
  if (!isKebab(slug)) throw new Error(`${repo.repo}: slug inválido «${slug}»`);

  const structural = [];
  if (originalName && originalName !== slug) {
    notes.push(`renombrada de «${originalName}» a «${slug}»`);
    structural.push('renombrada');
  }
  if (!hasFrontmatter) {
    notes.push('sin frontmatter en el origen: se generó');
    structural.push('frontmatter generado');
  }

  const description = normalizeDescription(entry.description || data.description, slug, notes);
  if (description !== String(entry.description || data.description || '').replace(/\s+/g, ' ').trim()) {
    structural.push('description recortada');
  }
  const license = entry.license || data.license || repoLicense?.kind || null;
  if (!license) notes.push('sin licencia declarada');

  let status = entry.status;
  if (!status) status = structural.length ? 'fixed' : 'ok';

  const skillRoot = repo.payload === 'repo'
    ? ''
    : entry.curated
      ? null
      : isDirectory
        ? entry.source
        : basename(filePath).toLowerCase() === 'skill.md'
          ? posix.dirname(entry.source)
          : null;
  let body = entry.curated
    ? rawBody
    : rewriteLinks(rawBody, {
        sourcePath: entry.source,
        repoDir: repo.dir,
        repoUrl: repo.url.replace(/\.git$/, ''),
        commit: repo.commit,
        skillRoot,
      });

  const metadata = {
    source: `${OWNER}/${repo.repo}`,
    'source-path': entry.curated || entry.source,
    'source-commit': repo.commit,
    category: entry.category,
    status,
  };
  if (originalName && originalName !== slug) metadata['original-name'] = originalName;
  if (entry.curated) metadata.generated = 'from-docs';

  const payload = stringifyFrontmatter({
    name: slug,
    description,
    license,
    metadata,
  }) + `${body.replace(/\s+$/, '')}\n`;

  const dest = join(libraryDir, slug);
  ensureDir(dest);

  let copied = { files: 0, bytes: 0 };
  const skippedAssets = [];
  if (entry.curated) {
    const skipped = copySkillTree(sourceAbs, dest);
    skippedAssets.push(...skipped);
  } else if (repo.payload === 'repo' || entry.payload === 'repo') {
    const skipped = copySkillTree(repo.dir, dest, { skip: ['.git'] });
    skippedAssets.push(...skipped);
  } else if (isDirectory) {
    const skipped = copySkillTree(sourceAbs, dest);
    skippedAssets.push(...skipped);
  } else if (basename(filePath).toLowerCase() === 'skill.md') {
    const skipped = copySkillTree(dirname(filePath), dest);
    skippedAssets.push(...skipped);
  } else {
    // Archivo suelto (p. ej. SKILL-motion.md): no arrastrar hermanos.
    cpSync(filePath, join(dest, 'SKILL.md'));
  }

  // El SKILL.md normalizado siempre gana.
  writeFileSync(join(dest, 'SKILL.md'), payload);

  copied = dirStats(dest);
  const manifest = {
    slug,
    name: slug,
    description,
    license,
    category: entry.category,
    tags: entry.tags || [],
    status,
    originalName,
    source: {
      repo: `${OWNER}/${repo.repo}`,
      path: entry.curated || entry.source,
      commit: repo.commit,
      url: `${repo.url.replace(/\.git$/, '')}/tree/${repo.commit}/${entry.curated ? '' : entry.source}`,
    },
    notes,
    skippedAssets,
    files: copied.files,
    bytes: copied.bytes,
    importedAt: new Date().toISOString(),
  };
  writeJson(join(dest, 'SOURCE.json'), manifest);
  return { manifest, bodyHash: hashBody(body), skippedAssets };
}

function rewriteLinks(body, { sourcePath, repoDir, repoUrl, commit, skillRoot }) {
  if (!sourcePath || !repoUrl) return body;
  const sourceDir = posix.dirname(sourcePath);
  return body.replace(/\]\((?!https?:|mailto:|#|tel:|\/)([^)\s]+)\)/g, (match, target) => {
    const [pathPart, hash = ''] = target.split('#');
    if (!pathPart) return match;
    const resolved = posix.normalize(posix.join(sourceDir, pathPart));
    if (resolved.startsWith('..')) return match;
    if (!existsSync(join(repoDir, resolved))) return match;
    if (skillRoot !== null && (resolved === skillRoot || resolved.startsWith(`${skillRoot}/`))) return match;
    return `](${repoUrl}/blob/${commit}/${resolved}${hash ? `#${hash}` : ''})`;
  });
}

function hashBody(body) {
  return createHash('sha1').update(body.replace(/\s+/g, ' ').trim()).digest('hex');
}

function main() {
  ensureDir(reportsDir);
  resetDir(libraryDir);

  const selected = REPOS.filter((repo) => !onlyRepo || repo.repo === onlyRepo);
  if (!selected.length) throw new Error(`No hay repo llamado ${onlyRepo}`);

  const sources = [];
  const skills = [];
  const duplicates = [];
  const findings = [];
  const seenSlugs = new Set();
  const seenHashes = new Map();

  for (const repo of selected) {
    process.stdout.write(`→ ${repo.repo} … `);
    const resolved = ensureRepo(repo.repo, repo.branch || 'main');
    const licenseInfo = detectLicense(resolved.dir);
    const sizeKb = repoSizeKb(resolved.dir);
    const entries = repo.discover
      ? discoverSkills({ ...repo, dir: resolved.dir })
      : repo.curated
        ? [
            {
              curated: repo.curated,
              source: null,
              slug: repo.slug,
              category: repo.category,
              tags: repo.tags,
              status: repo.status,
            },
          ]
        : repo.skills;

    let imported = 0;
    for (const entry of entries) {
      const slug = entry.slug;
      if (!slug) throw new Error(`${repo.repo}: entrada sin slug`);
      if (seenSlugs.has(slug)) throw new Error(`Slug duplicado: ${slug}`);
      const { manifest, bodyHash } = prepare(entry, { ...repo, ...resolved }, licenseInfo);
      if (seenHashes.has(bodyHash)) {
        duplicates.push({ slug, duplicateOf: seenHashes.get(bodyHash), repo: repo.repo });
        // La copia ya escrita se descarta para no publicar duplicados.
        rmSync(join(libraryDir, slug), { recursive: true, force: true });
        continue;
      }
      seenHashes.set(bodyHash, slug);
      seenSlugs.add(slug);
      skills.push(manifest);
      imported += 1;
    }

    const skipped = (repo.skip || []).map((path) => ({
      path,
      reason: 'copia idéntica de otro repo (se importa desde Rae)',
    }));
    for (const item of skipped) duplicates.push({ slug: basename(item.path), repo: repo.repo, reason: item.reason });

    if (sizeKb && sizeKb > 50 * 1024) {
      findings.push({
        repo: repo.repo,
        level: 'aviso',
        message: `El repo pesa ${humanBytes(sizeKb * 1024)}. Mezcla skills con assets de sitios; conviene separar el material pesado del repo de skills.`,
      });
    }
    if (!licenseInfo) {
      findings.push({
        repo: repo.repo,
        level: 'aviso',
        message: 'No hay archivo LICENSE. Las skills se importan, pero no conviene publicarlas en un marketplace sin licencia.',
      });
    }
    if (repo.repo === 'scroll-craft') {
      const readme = join(resolved.dir, 'README.md');
      if (existsSync(readme) && /^import\s+\{/.test(readText(readme).trim())) {
        findings.push({
          repo: repo.repo,
          level: 'error',
          message: 'README.md contiene código compilado de App.tsx (no documentación) y el repo no trae SKILL.md pese a describirse como agent skill. La skill del hub se generó desde docs/ y requiere revisión.',
        });
      }
    }

    sources.push({
      repo: repo.repo,
      branch: repo.branch || 'main',
      commit: resolved.commit,
      url: `https://github.com/${OWNER}/${repo.repo}`,
      license: licenseInfo?.kind || null,
      licenseFile: licenseInfo?.file || null,
      sizeKb,
      imported,
      skipped: (repo.skip || []).length,
    });
    process.stdout.write(`${imported} skills\n`);
  }

  const lock = {
    schemaVersion: LIBRARY_VERSION,
    owner: OWNER,
    generatedAt: new Date().toISOString(),
    skillCount: skills.length,
    sources,
    duplicates,
    findings,
    skills: skills.sort((a, b) => a.slug.localeCompare(b.slug)),
  };

  writeJson(join(hubRoot, 'registry.lock.json'), lock);
  writeJson(join(hubRoot, 'skills.json'), {
    owner: OWNER,
    generatedAt: lock.generatedAt,
    count: skills.length,
    skills: lock.skills.map((skill) => ({
      name: skill.name,
      description: skill.description,
      category: skill.category,
      tags: skill.tags,
      license: skill.license,
      status: skill.status,
      path: `library/${skill.slug}`,
      source: skill.source,
    })),
  });

  writeReports({ hubRoot, libraryDir, lock, humanBytes });
  const totalBytes = skills.reduce((sum, skill) => sum + skill.bytes, 0);
  console.log(`\n✓ ${skills.length} skills desde ${sources.length} repos (${humanBytes(totalBytes)})`);
  console.log(`  catálogo: skills.json · inventario: reports/INVENTARIO.md`);
}

try {
  main();
} catch (error) {
  console.error(`\n✗ ${error.message}`);
  process.exit(1);
}
