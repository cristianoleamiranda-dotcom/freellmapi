#!/usr/bin/env node
// Empaqueta la biblioteca para distintos clientes:
//   dist/openclaw/skills/         copia directa a ~/.openclaw/skills
//   dist/cursor-marketplace/      repo con .cursor-plugin/marketplace.json
//   dist/claude-marketplace/      repo con .claude-plugin/marketplace.json
//   dist/*.tar.gz                 archivos listos para subir
//
// Uso: node src/pack.mjs

import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { cpSync, existsSync, mkdirSync, readFileSync, readdirSync, rmSync, statSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

import { CATEGORIES } from './config.mjs';
import { humanBytes, readJson, writeJson } from './fs-utils.mjs';

const hubRoot = join(dirname(fileURLToPath(import.meta.url)), '..');
const libraryDir = join(hubRoot, 'library');
const dist = join(hubRoot, 'dist');
const manifest = readJson(join(hubRoot, 'skills.json'));
const lock = readJson(join(hubRoot, 'registry.lock.json'));

if (!manifest || !lock) fail('Falta skills.json o registry.lock.json. Ejecuta npm run sync.');

const OWNER = 'cristianoleamiranda-dotcom';
const REPO_URL = `https://github.com/${OWNER}/skills`;
const VERSION = '0.1.0';
const DESCRIPTION =
  'Skills de diseño web inmersivo, motion, PixiJS, video y reverse engineering de Cristian Leiva Miranda.';

rmSync(dist, { recursive: true, force: true });
mkdirSync(dist, { recursive: true });

const slugs = readdirSync(libraryDir, { withFileTypes: true })
  .filter((entry) => entry.isDirectory())
  .map((entry) => entry.name)
  .sort();

packOpenClaw();
packCursor();
packClaude();
writeChecksums();

console.log(`✓ dist/ generado con ${slugs.length} skills`);
console.log('  - dist/openclaw/skills/');
console.log('  - dist/cursor-marketplace/');
console.log('  - dist/claude-marketplace/');
console.log('  - dist/*.tar.gz');

function packOpenClaw() {
  const root = join(dist, 'openclaw');
  const skillsDir = join(root, 'skills');
  mkdirSync(skillsDir, { recursive: true });
  for (const slug of slugs) cpSync(join(libraryDir, slug), join(skillsDir, slug), { recursive: true });
  writeFileSync(
    join(root, 'README.md'),
    [
      '# Skills para OpenClaw',
      '',
      `Paquete generado desde \`${OWNER}\` (${slugs.length} skills).`,
      '',
      '## Instalación manual',
      '',
      'Copia cada carpeta a una de estas rutas:',
      '',
      '| Alcance | Ruta |',
      '|---|---|',
      '| Global | `~/.openclaw/skills/` |',
      '| Proyecto | `<proyecto>/skills/` |',
      '',
      '```bash',
      'cp -R skills/* ~/.openclaw/skills/',
      '```',
      '',
      'La prioridad de OpenClaw es: workspace > local > bundled.',
      '',
      '## Publicación',
      '',
      'La lista awesome-openclaw-skills solo acepta skills publicadas en ClawHub.',
      'Publica el paquete con la CLI de ClawHub y luego abre el PR con el enlace',
      '`https://clawhub.ai/<usuario>/<slug>`. Ver `docs/PUBLICAR.md` en el hub.',
      '',
      '## Catálogo',
      '',
      ...slugs.map((slug) => `- \`${slug}\``),
      '',
    ].join('\n'),
  );
}

function packCursor() {
  const root = join(dist, 'cursor-marketplace');
  const plugin = join(root, 'cristian-skills');
  const skillsDir = join(plugin, 'skills');
  mkdirSync(join(root, '.cursor-plugin'), { recursive: true });
  mkdirSync(join(plugin, '.cursor-plugin'), { recursive: true });
  mkdirSync(skillsDir, { recursive: true });
  for (const slug of slugs) cpSync(join(libraryDir, slug), join(skillsDir, slug), { recursive: true });

  writeJson(join(root, '.cursor-plugin', 'marketplace.json'), {
    name: 'cristian-skills',
    owner: { name: OWNER },
    metadata: { description: DESCRIPTION },
    plugins: [
      {
        name: 'cristian-skills',
        source: 'cristian-skills',
        description: DESCRIPTION,
      },
    ],
  });

  writeJson(join(plugin, '.cursor-plugin', 'plugin.json'), {
    name: 'cristian-skills',
    displayName: 'Cristian Skills',
    version: VERSION,
    description: DESCRIPTION,
    author: { name: OWNER },
    homepage: REPO_URL,
    repository: REPO_URL,
    license: 'UNLICENSED',
    keywords: ['skills', 'webgl', 'pixijs', 'motion', 'scroll', 'reverse-engineering'],
    category: 'developer-tools',
    tags: ['agent-skills', 'design', 'motion', 'pixijs', 'video'],
    skills: './skills/',
  });

  writeFileSync(
    join(plugin, 'README.md'),
    [
      '# Cristian Skills (plugin de Cursor)',
      '',
      DESCRIPTION,
      '',
      `\`${slugs.length}\` skills en \`skills/<nombre>/SKILL.md\`.`,
      '',
      '## Instalación',
      '',
      'Este directorio es un marketplace de plugins de Cursor: contiene',
      '`.cursor-plugin/marketplace.json` y un plugin con su propio',
      '`.cursor-plugin/plugin.json`.',
      '',
      'Añádelo como marketplace desde tu editor (Settings → Plugins) apuntando al',
      'repo donde publiques esta carpeta, o copia `cristian-skills/skills/` a',
      '`.cursor/skills/` en el proyecto.',
      '',
      '## Licencias',
      '',
      'Ver `LICENCIAS.md`. Varias skills vienen de repos sin archivo LICENSE.',
      '',
    ].join('\n'),
  );
  writeLicenses(plugin);
}

function packClaude() {
  const root = join(dist, 'claude-marketplace');
  const plugin = join(root, 'cristian-skills');
  const skillsDir = join(plugin, 'skills');
  mkdirSync(join(root, '.claude-plugin'), { recursive: true });
  mkdirSync(join(plugin, '.claude-plugin'), { recursive: true });
  mkdirSync(skillsDir, { recursive: true });
  for (const slug of slugs) cpSync(join(libraryDir, slug), join(skillsDir, slug), { recursive: true });

  writeJson(join(root, '.claude-plugin', 'marketplace.json'), {
    name: 'cristian-skills',
    owner: { name: OWNER },
    plugins: [
      {
        name: 'cristian-skills',
        source: './cristian-skills',
        description: DESCRIPTION,
        version: VERSION,
      },
    ],
  });

  writeJson(join(plugin, '.claude-plugin', 'plugin.json'), {
    name: 'cristian-skills',
    version: VERSION,
    description: DESCRIPTION,
    author: { name: OWNER },
    homepage: REPO_URL,
    repository: REPO_URL,
    license: 'UNLICENSED',
    keywords: ['skills', 'webgl', 'pixijs', 'motion', 'scroll'],
    skills: './skills/',
  });

  writeFileSync(
    join(plugin, 'README.md'),
    [
      '# Cristian Skills (plugin de Claude Code)',
      '',
      DESCRIPTION,
      '',
      'Instalación como marketplace local:',
      '',
      '```bash',
      '/plugin marketplace add /ruta/a/dist/claude-marketplace',
      '/plugin install cristian-skills',
      '```',
      '',
      'O copia `skills/` a `.claude/skills/` del proyecto.',
      '',
    ].join('\n'),
  );
  writeLicenses(plugin);
}

function writeLicenses(dir) {
  const lines = ['# Licencias', ''];
  lines.push('| Skill | Licencia | Origen |');
  lines.push('|---|---|---|');
  for (const skill of manifest.skills) {
    lines.push(`| \`${skill.name}\` | ${skill.license || 'sin declarar'} | \`${skill.source.repo}\` |`);
  }
  lines.push('');
  lines.push('Las skills sin licencia provienen de repos privados del autor sin archivo LICENSE.');
  writeFileSync(join(dir, 'LICENCIAS.md'), `${lines.join('\n')}\n`);
}

function writeChecksums() {
  const archives = [
    ['cristian-skills-openclaw.tar.gz', 'openclaw'],
    ['cristian-skills-cursor.tar.gz', 'cursor-marketplace'],
    ['cristian-skills-claude.tar.gz', 'claude-marketplace'],
  ];
  const rows = [];
  for (const [name, folder] of archives) {
    execFileSync('tar', ['-czf', join(dist, name), '-C', join(dist, folder), '.']);
    const hash = createHash('sha256').update(readFileSync(join(dist, name))).digest('hex');
    const bytes = statSync(join(dist, name)).size;
    rows.push(`| \`${name}\` | ${humanBytes(bytes)} | \`${hash.slice(0, 16)}…\` |`);
  }
  writeFileSync(
    join(dist, 'LEEME.md'),
    [
      '# Paquetes generados',
      '',
      `Generado: ${new Date().toISOString().slice(0, 10)} · ${slugs.length} skills`,
      '',
      '| Archivo | Peso | SHA-256 |',
      '|---|---|---|',
      ...rows,
      '',
      '## Contenido',
      '',
      '- `openclaw/` — carpeta `skills/` para `~/.openclaw/skills/` o `<proyecto>/skills/`.',
      '- `cursor-marketplace/` — repo con `.cursor-plugin/marketplace.json` y el plugin `cristian-skills`.',
      '- `claude-marketplace/` — repo con `.claude-plugin/marketplace.json` y el plugin `cristian-skills`.',
      '',
      'Cada skill conserva su `SOURCE.json` con repo, ruta y commit de origen.',
      '',
    ].join('\n'),
  );
}

function fail(message) {
  console.error(`✗ ${message}`);
  process.exit(1);
}
