#!/usr/bin/env node
// Valida library/ y escribe reports/VALIDACION.md. Sale con código 1 si hay
// errores (no si solo hay avisos).

import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

import { validateLibrary } from './validate-lib.mjs';
import { humanBytes, writeFileSyncSafe } from './fs-utils.mjs';

const hubRoot = join(dirname(fileURLToPath(import.meta.url)), '..');
const libraryDir = join(hubRoot, 'library');

const { skills, errors, warnings } = validateLibrary(libraryDir);
const bytes = skills.reduce((sum, skill) => sum + (skill.bytes || 0), 0);

console.log(`Skills revisadas: ${skills.length} (${humanBytes(bytes)})`);
console.log(`Errores: ${errors.length}`);
console.log(`Avisos: ${warnings.length}`);

if (errors.length) {
  console.log('\nErrores:');
  for (const error of errors) console.log(`  ✗ ${error.slug}: ${error.message}`);
}
if (warnings.length) {
  console.log('\nAvisos:');
  const grouped = new Map();
  for (const warning of warnings) {
    if (!grouped.has(warning.code)) grouped.set(warning.code, []);
    grouped.get(warning.code).push(warning);
  }
  for (const [code, items] of grouped) {
    console.log(`  ! ${code} (${items.length}): ${items.map((item) => item.slug).join(', ')}`);
  }
}

writeFileSyncSafe(
  join(hubRoot, 'reports', 'VALIDACION.md'),
  [
    '# Validación de la biblioteca',
    '',
    `Skills revisadas: ${skills.length} (${humanBytes(bytes)})`,
    '',
    `- Errores: ${errors.length}`,
    `- Avisos: ${warnings.length}`,
    '',
    ...(errors.length ? ['## Errores', '', ...errors.map((error) => `- \`${error.slug}\` — ${error.message}`), ''] : []),
    ...(warnings.length
      ? [
          '## Avisos',
          '',
          ...warnings.map((warning) => `- \`${warning.slug}\` — ${warning.message}`),
          '',
        ]
      : []),
  ].join('\n'),
);

process.exit(errors.length ? 1 : 0);
