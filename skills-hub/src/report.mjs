// Genera reports/INVENTARIO.md a partir de registry.lock.json y la validación.
import { join } from 'node:path';

import { validateLibrary } from './validate-lib.mjs';
import { humanBytes as defaultHumanBytes, readJson, writeFileSyncSafe } from './fs-utils.mjs';

const STATUS_LABEL = {
  ok: 'normal',
  fixed: 'corregida',
  generated: 'generada',
  trimmed: 'recortada',
};

export function writeReports({ hubRoot, libraryDir, lock, humanBytes = defaultHumanBytes }) {
  const validation = validateLibrary(libraryDir);
  const byCategory = new Map();
  for (const skill of lock.skills) {
    if (!byCategory.has(skill.category)) byCategory.set(skill.category, []);
    byCategory.get(skill.category).push(skill);
  }
  for (const list of byCategory.values()) list.sort((a, b) => a.slug.localeCompare(b.slug));

  const totalBytes = lock.skills.reduce((sum, skill) => sum + skill.bytes, 0);
  const withLicense = lock.skills.filter((skill) => skill.license).length;
  const lines = [];

  lines.push('# Inventario de skills');
  lines.push('');
  lines.push(`Generado: ${lock.generatedAt.slice(0, 10)} · dueño: \`${lock.owner}\``);
  lines.push('');
  lines.push('Este archivo lo regenera `npm run sync`. No editar a mano.');
  lines.push('');
  lines.push('## Resumen');
  lines.push('');
  lines.push('| Métrica | Valor |');
  lines.push('|---|---|');
  lines.push(`| Skills importadas | ${lock.skillCount} |`);
  lines.push(`| Repos de origen | ${lock.sources.length} |`);
  lines.push(`| Categorías | ${byCategory.size} |`);
  lines.push(`| Peso de la biblioteca | ${humanBytes(totalBytes)} |`);
  lines.push(`| Con licencia declarada | ${withLicense} de ${lock.skillCount} |`);
  lines.push(`| Duplicados omitidos | ${lock.duplicates.length} |`);
  lines.push(`| Errores de validación | ${validation.errors.length} |`);
  lines.push(`| Avisos de validación | ${validation.warnings.length} |`);
  lines.push('');
  lines.push('## Origen');
  lines.push('');
  lines.push('| Repo | Commit | Licencia | Skills | Tamaño |');
  lines.push('|---|---|---|---:|---:|');
  for (const source of lock.sources) {
    const size = source.sizeKb ? humanBytes(source.sizeKb * 1024) : '—';
    lines.push(
      `| [${source.repo}](${source.url}) | \`${source.commit.slice(0, 7)}\` | ${source.license || 'sin LICENSE'} | ${source.imported} | ${size} |`,
    );
  }
  lines.push('');
  lines.push('## Catálogo');
  lines.push('');
  for (const [category, skills] of [...byCategory.entries()].sort((a, b) => a[0].localeCompare(b[0]))) {
    lines.push(`### ${category} (${skills.length})`);
    lines.push('');
    lines.push('| Skill | Estado | Licencia | Descripción |');
    lines.push('|---|---|---|---|');
    for (const skill of skills) {
      lines.push(
        `| [\`${skill.slug}\`](../library/${skill.slug}/SKILL.md) | ${STATUS_LABEL[skill.status] || skill.status} | ${skill.license || '—'} | ${escape(skill.description, 110)} |`,
      );
    }
    lines.push('');
  }

  lines.push('## Hallazgos');
  lines.push('');
  if (!lock.findings.length && !lock.duplicates.length && !validation.errors.length && !validation.warnings.length) {
    lines.push('Sin hallazgos.');
  } else {
    for (const finding of lock.findings) {
      lines.push(`- **${finding.level.toUpperCase()} · ${finding.repo}** — ${finding.message}`);
    }
    for (const duplicate of lock.duplicates) {
      lines.push(
        `- **DUPLICADO · ${duplicate.repo}** — \`${duplicate.slug}\` no se importó: ${duplicate.reason || `igual a \`${duplicate.duplicateOf}\``}.`,
      );
    }
    for (const error of validation.errors) {
      lines.push(`- **ERROR · ${error.slug}** — ${error.message}`);
    }
    const grouped = new Map();
    for (const warning of validation.warnings) {
      if (!grouped.has(warning.code)) grouped.set(warning.code, []);
      grouped.get(warning.code).push(warning);
    }
    for (const [code, items] of grouped) {
      const slugs = items.map((item) => `\`${item.slug}\``).join(', ');
      lines.push(`- **AVISO · ${code}** — ${items[0].message} (${items.length}): ${slugs}`);
    }
  }
  lines.push('');
  lines.push('## Activación');
  lines.push('');
  lines.push('```bash');
  lines.push('# Claude Code, Cursor, OpenCode y agentes compatibles con .agents/');
  lines.push('node src/install.mjs --target claude,agents,cursor --git-exclude');
  lines.push('');
  lines.push('# OpenClaw: instala en <proyecto>/skills/ o en ~/.openclaw/skills/');
  lines.push('node src/install.mjs --target openclaw --project ~/.openclaw');
  lines.push('```');
  lines.push('');
  lines.push('Los detalles de uso están en [README.md](../README.md).');
  lines.push('');

  writeFileSyncSafe(join(hubRoot, 'reports', 'INVENTARIO.md'), lines.join('\n'));
  writeFileSyncSafe(
    join(hubRoot, 'reports', 'VALIDACION.md'),
    renderValidation(validation),
  );
  return { validation };
}

function renderValidation(validation) {
  const lines = ['# Validación de la biblioteca', ''];
  lines.push(`Skills revisadas: ${validation.skills.length}`);
  lines.push('');
  lines.push(`- Errores: ${validation.errors.length}`);
  lines.push(`- Avisos: ${validation.warnings.length}`);
  lines.push('');
  if (validation.errors.length) {
    lines.push('## Errores');
    lines.push('');
    for (const error of validation.errors) lines.push(`- \`${error.slug}\` — ${error.message}`);
    lines.push('');
  }
  if (validation.warnings.length) {
    lines.push('## Avisos');
    lines.push('');
    const grouped = new Map();
    for (const warning of validation.warnings) {
      if (!grouped.has(warning.code)) grouped.set(warning.code, []);
      grouped.get(warning.code).push(warning);
    }
    for (const [code, items] of grouped) {
      lines.push(`### ${code} (${items.length})`);
      lines.push('');
      for (const item of items) lines.push(`- \`${item.slug}\` — ${item.message}`);
      lines.push('');
    }
  }
  return lines.join('\n');
}

function escape(text, max) {
  const clean = String(text || '').replace(/\s+/g, ' ').replace(/\|/g, '\\|');
  return clean.length > max ? `${clean.slice(0, max - 1)}…` : clean;
}
