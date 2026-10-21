#!/usr/bin/env node
// Activa la biblioteca en un proyecto copiando (o enlazando) cada skill al
// directorio que lee el cliente. Uso:
//   node src/install.mjs --target claude,agents --project ../..
//   node src/install.mjs --target openclaw --project ~/.openclaw
//   node src/install.mjs --target cursor --link --git-exclude
//   node src/install.mjs --only sender-design-system,scrollcraft-arena

import { cpSync, existsSync, lstatSync, mkdirSync, readFileSync, readdirSync, rmSync, symlinkSync, writeFileSync } from 'node:fs';
import { dirname, join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

import { INSTALL_TARGETS } from './config.mjs';
import { readJson, writeJson } from './fs-utils.mjs';

const hubRoot = join(dirname(fileURLToPath(import.meta.url)), '..');
const libraryDir = join(hubRoot, 'library');

const args = process.argv.slice(2);
const flags = new Set(args.filter((arg) => arg.startsWith('--')));
const valueOf = (name, fallback = null) => {
  const index = args.indexOf(`--${name}`);
  return index !== -1 ? args[index + 1] : fallback;
};

const targets = (valueOf('target', 'claude,agents') || '')
  .split(',')
  .map((item) => item.trim())
  .filter(Boolean);
const project = resolve(valueOf('project', join(hubRoot, '..')));
const link = flags.has('--link');
const dryRun = flags.has('--dry-run');
const force = flags.has('--force');
const gitExclude = flags.has('--git-exclude');
const only = (valueOf('only', '') || '')
  .split(',')
  .map((item) => item.trim())
  .filter(Boolean);

if (!targets.length) fail('Indica al menos un --target (claude, agents, cursor, opencode, openclaw)');
for (const target of targets) {
  if (!INSTALL_TARGETS[target]) fail(`Target desconocido: ${target}\nVálidos: ${Object.keys(INSTALL_TARGETS).join(', ')}`);
}
if (!existsSync(libraryDir)) fail('No existe library/. Ejecuta primero: npm run sync');

const installed = readdirSync(libraryDir, { withFileTypes: true })
  .filter((entry) => entry.isDirectory())
  .map((entry) => entry.name)
  .filter((slug) => !only.length || only.includes(slug))
  .sort();

if (!installed.length) fail(`No hay skills para instalar${only.length ? ` con --only ${only.join(',')}` : ''}`);

const excludeLines = [];
for (const target of targets) {
  const relativeDir = INSTALL_TARGETS[target];
  const targetDir = join(project, relativeDir);
  const manifestPath = join(targetDir, '.skills-hub.json');
  const previous = readJson(manifestPath, { skills: [] });

  if (dryRun) {
    console.log(`[dry-run] ${target}: ${installed.length} skills → ${targetDir}`);
    continue;
  }

  mkdirSync(targetDir, { recursive: true });

  // Limpia solo lo que instaló este hub anteriormente.
  for (const slug of previous.skills || []) {
    const previousDir = join(targetDir, slug);
    if (existsSync(previousDir)) rmSync(previousDir, { recursive: true, force: true });
  }

  let copied = 0;
  let skipped = 0;
  for (const slug of installed) {
    const source = join(libraryDir, slug);
    const dest = join(targetDir, slug);
    if (existsSync(dest) && !existsSync(join(dest, 'SOURCE.json')) && !force) {
      console.warn(`  ! ${target}: «${slug}» ya existía sin marcador del hub, se omite (usa --force)`);
      skipped += 1;
      continue;
    }
    if (existsSync(dest)) rmSync(dest, { recursive: true, force: true });
    if (link) {
      const rel = relative(dirname(dest), source);
      symlinkSync(rel, dest, 'dir');
    } else {
      cpSync(source, dest, { recursive: true });
    }
    copied += 1;
  }

  writeJson(manifestPath, {
    tool: 'skills-hub',
    owner: 'cristianoleamiranda-dotcom',
    installedAt: new Date().toISOString(),
    mode: link ? 'symlink' : 'copy',
    skills: installed,
  });

  if (gitExclude && target !== 'openclaw') {
    excludeLines.push(`/${relativeDir.replace(/^\//, '')}/`);
  }

  console.log(`✓ ${target}: ${copied} instaladas${skipped ? `, ${skipped} omitidas` : ''} → ${targetDir}`);
}

if (gitExclude && !dryRun) {
  const excludePath = join(project, '.git', 'info', 'exclude');
  if (!existsSync(join(project, '.git'))) {
    console.warn('! --git-exclude: el proyecto no es un repo git, no se tocó .git/info/exclude');
  } else {
    mkdirSync(dirname(excludePath), { recursive: true });
    const current = existsSync(excludePath) ? readFileSync(excludePath, 'utf8') : '';
    const lines = current.split('\n');
    const additions = excludeLines.filter((line) => !lines.includes(line));
    if (additions.length) {
      const suffix = current && !current.endsWith('\n') ? '\n' : '';
      writeFileSync(
        excludePath,
        `${current}${suffix}# skills-hub: skills locales, no versionar\n${additions.join('\n')}\n`,
      );
      console.log(`✓ .git/info/exclude: ${additions.length} rutas añadidas`);
    } else {
      console.log('✓ .git/info/exclude ya estaba al día');
    }
  }
}

function fail(message) {
  console.error(`✗ ${message}`);
  process.exit(1);
}
