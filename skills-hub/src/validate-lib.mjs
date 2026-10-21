// Validaciones de la biblioteca generada. Se usan desde validate.mjs y desde
// el reporte, para que ambos digan exactamente lo mismo.

import { existsSync, readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';

import { splitFrontmatter } from './frontmatter.mjs';
import { isKebab, readJson, readText, walk } from './fs-utils.mjs';

const MAX_DESCRIPTION = 1024;
const MIN_BODY = 120;

export function validateLibrary(libraryDir) {
  const skills = [];
  const errors = [];
  const warnings = [];
  const names = new Map();

  if (!existsSync(libraryDir)) {
    return {
      skills,
      errors: [{ slug: '-', code: 'sin-library', message: 'No existe library/. Ejecuta npm run sync.' }],
      warnings,
    };
  }

  for (const entry of readdirSync(libraryDir, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name))) {
    if (!entry.isDirectory()) continue;
    const slug = entry.name;
    const dir = join(libraryDir, slug);
    const file = join(dir, 'SKILL.md');
    const source = readJson(join(dir, 'SOURCE.json'));
    const record = { slug, errors: [], warnings: [] };

    if (!existsSync(file)) {
      record.errors.push('falta SKILL.md');
      errors.push({ slug, code: 'sin-skill-md', message: 'Falta SKILL.md' });
      skills.push(record);
      continue;
    }

    const text = readText(file);
    const { data, body, hasFrontmatter } = splitFrontmatter(text);
    record.name = data.name || null;
    record.description = data.description || '';
    record.license = data.license || null;
    record.category = data.metadata?.category || source?.category || null;
    record.status = data.metadata?.status || source?.status || null;
    record.source = source?.source || null;

    if (!hasFrontmatter) {
      record.errors.push('sin frontmatter');
      errors.push({ slug, code: 'sin-frontmatter', message: 'SKILL.md no empieza con ---' });
    }
    if (!data.name) {
      record.errors.push('sin name');
      errors.push({ slug, code: 'sin-name', message: 'Falta name en el frontmatter' });
    } else {
      if (!isKebab(data.name)) {
        record.errors.push('name no kebab-case');
        errors.push({ slug, code: 'name-invalido', message: `name «${data.name}» no es kebab-case` });
      }
      if (data.name !== slug) {
        record.errors.push('name ≠ carpeta');
        errors.push({ slug, code: 'name-no-coincide', message: `name «${data.name}» no coincide con la carpeta «${slug}»` });
      }
      names.set(data.name, (names.get(data.name) || 0) + 1);
    }

    if (!data.description) {
      record.errors.push('sin description');
      errors.push({ slug, code: 'sin-description', message: 'Falta description' });
    } else if (data.description.length > MAX_DESCRIPTION) {
      record.errors.push('description > 1024');
      errors.push({
        slug,
        code: 'description-larga',
        message: `description de ${data.description.length} caracteres (máximo ${MAX_DESCRIPTION})`,
      });
    } else if (data.description.length < 20) {
      record.warnings.push('description muy corta');
      warnings.push({ slug, code: 'description-corta', message: 'description de menos de 20 caracteres' });
    }

    if (body.trim().length < MIN_BODY) {
      record.warnings.push('cuerpo muy corto');
      warnings.push({ slug, code: 'cuerpo-corto', message: `cuerpo de ${body.trim().length} caracteres` });
    }

    if (!record.license) {
      record.warnings.push('sin licencia');
      warnings.push({ slug, code: 'sin-licencia', message: 'No declara licencia' });
    }
    if (!source) {
      record.warnings.push('sin SOURCE.json');
      warnings.push({ slug, code: 'sin-source', message: 'Falta SOURCE.json (no se puede rastrear el origen)' });
    }

    for (const missing of brokenLinks(body, dir)) {
      record.warnings.push(`enlace roto: ${missing}`);
      warnings.push({ slug, code: 'enlace-roto', message: `Enlace relativo inexistente: ${missing}` });
    }

    const size = walk(dir).reduce((sum, f) => sum + statSync(f).size, 0);
    record.bytes = size;
    record.files = walk(dir).length;
    skills.push(record);
  }

  for (const [name, count] of names) {
    if (count > 1) errors.push({ slug: name, code: 'name-duplicado', message: `${count} skills usan el mismo name` });
  }

  return { skills, errors, warnings };
}

function brokenLinks(body, skillDir) {
  const missing = new Set();
  const linkPattern = /\]\((?!https?:|mailto:|#|tel:)([^)\s]+)\)/g;
  let match;
  while ((match = linkPattern.exec(body))) {
    const raw = match[1];
    if (raw.includes('{{') || raw.startsWith('/')) continue;
    const clean = raw.split('#')[0].split('?')[0];
    if (!clean || !clean.endsWith('.md')) continue;
    if (!existsSync(join(skillDir, clean))) missing.add(clean);
  }
  return [...missing];
}
