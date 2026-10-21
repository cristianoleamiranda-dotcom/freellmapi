// Parser y serializador YAML mínimo, suficiente para frontmatter de skills.
// Soporta: escalares, comillas simples/dobles multilínea, bloques `|` y `>`,
// y un nivel de mapas anidados (metadata). No pretende ser YAML completo.

const DELIMITER = /^---\s*$/;

/** Separa frontmatter y cuerpo. Normaliza CRLF a LF. */
export function splitFrontmatter(input) {
  const text = String(input).replace(/\r\n?/g, '\n');
  if (!text.startsWith('---\n') && text.trimStart().slice(0, 3) !== '---') {
    return { data: {}, body: text, raw: '', hasFrontmatter: false };
  }
  const lines = text.split('\n');
  if (lines[0].trim() !== '---') {
    return { data: {}, body: text, raw: '', hasFrontmatter: false };
  }
  let closing = -1;
  for (let i = 1; i < lines.length; i += 1) {
    if (DELIMITER.test(lines[i])) {
      closing = i;
      break;
    }
  }
  if (closing === -1) {
    return { data: {}, body: text, raw: '', hasFrontmatter: false };
  }
  const raw = lines.slice(1, closing).join('\n');
  return {
    data: parseFrontmatter(raw),
    body: lines.slice(closing + 1).join('\n').replace(/^\n+/, ''),
    raw,
    hasFrontmatter: true,
  };
}

/** Convierte el bloque YAML (sin delimitadores) en un objeto plano. */
export function parseFrontmatter(raw) {
  const lines = String(raw).replace(/\r\n?/g, '\n').split('\n');
  const data = {};
  let currentKey = null;
  let currentIndent = 0;

  const isIndented = (line) => /^\s+\S/.test(line);
  const unquote = (value) => {
    const v = value.trim();
    if (v.length >= 2 && v.startsWith('"') && v.endsWith('"')) {
      return v
        .slice(1, -1)
        .replace(/\\"/g, '"')
        .replace(/\\n/g, '\n')
        .replace(/\\\\/g, '\\');
    }
    if (v.length >= 2 && v.startsWith("'") && v.endsWith("'")) {
      return v.slice(1, -1).replace(/''/g, "'");
    }
    return v;
  };

  for (let i = 0; i < lines.length; i += 1) {
    const line = lines[i];
    if (!line.trim() || /^\s*#/.test(line)) continue;

    const top = line.match(/^([A-Za-z0-9_-]+):\s*(.*)$/);
    if (top) {
      currentKey = top[1];
      currentIndent = 0;
      const value = top[2].trim();
      if (value === '' || value === '>' || value === '>-' || value === '|' || value === '|-') {
        // Bloque o mapa anidado: recolectar líneas más indentadas.
        const collected = [];
        let j = i + 1;
        while (j < lines.length) {
          const next = lines[j];
          if (!next.trim()) {
            collected.push('');
            j += 1;
            continue;
          }
          if (!/^\s/.test(next)) break;
          collected.push(next);
          j += 1;
        }
        i = j - 1;
        if (value.startsWith('>') || value.startsWith('|')) {
          const literal = value.startsWith('|');
          const dedented = dedent(collected);
          data[currentKey] = literal
            ? dedented.join('\n').replace(/\n+$/, '')
            : fold(dedented);
        } else {
          const nested = {};
          for (const entry of collected) {
            const m = entry.match(/^\s+([A-Za-z0-9_-]+):\s*(.*)$/);
            if (m) nested[m[1]] = unquote(m[2]);
          }
          data[currentKey] = nested;
        }
        continue;
      }

      if (value.startsWith('"') && !isClosedQuote(value)) {
        const parts = [value.slice(1)];
        let j = i + 1;
        while (j < lines.length) {
          const next = lines[j];
          parts.push(next.trim());
          if (isClosedQuote(parts.join(' '))) {
            j += 1;
            break;
          }
          j += 1;
        }
        i = j - 1;
        data[currentKey] = unquote(parts.join(' '));
        continue;
      }

      data[currentKey] = unquote(value);
      continue;
    }

    // Continuación de un valor multilínea sin comillas.
    if (currentKey && isIndented(line)) {
      const piece = line.trim();
      const prev = data[currentKey];
      data[currentKey] = typeof prev === 'string' && prev ? `${prev} ${piece}` : piece;
    }
  }

  return data;
}

function isClosedQuote(value) {
  const v = value.trim();
  if (!v.startsWith('"')) return true;
  // Cuenta comillas no escapadas.
  let count = 0;
  for (let i = 0; i < v.length; i += 1) {
    if (v[i] === '"' && v[i - 1] !== '\\') count += 1;
  }
  return count % 2 === 0;
}

function dedent(lines) {
  const nonEmpty = lines.filter((l) => l.trim());
  if (!nonEmpty.length) return [];
  const indent = Math.min(...nonEmpty.map((l) => l.match(/^\s*/)[0].length));
  return lines.map((l) => l.slice(indent));
}

function fold(lines) {
  const parts = [];
  let buffer = [];
  for (const line of lines) {
    if (line.trim() === '') {
      if (buffer.length) {
        parts.push(buffer.join(' '));
        buffer = [];
      }
      parts.push('');
    } else {
      buffer.push(line.trim());
    }
  }
  if (buffer.length) parts.push(buffer.join(' '));
  return parts.join('\n').replace(/\n{3,}/g, '\n\n').trim();
}

/** Serializa un frontmatter canónico. La descripción va como bloque `>`. */
export function stringifyFrontmatter(data) {
  const out = ['---'];
  const order = ['name', 'description', 'license'];
  for (const key of order) {
    const value = data[key];
    if (value === undefined || value === null || value === '') continue;
    if (key === 'description') {
      out.push('description: >');
      for (const line of wrap(String(value), 96)) out.push(`  ${line}`);
    } else {
      out.push(`${key}: ${scalar(value)}`);
    }
  }
  if (data.metadata && Object.keys(data.metadata).length) {
    out.push('metadata:');
    for (const [key, value] of Object.entries(data.metadata)) {
      if (value === undefined || value === null || value === '') continue;
      out.push(`  ${key}: ${scalar(value)}`);
    }
  }
  out.push('---', '');
  return out.join('\n');
}

function scalar(value) {
  const s = String(value);
  if (/^[A-Za-z0-9_./@+-]+$/.test(s)) return s;
  return `"${s.replace(/\\/g, '\\\\').replace(/"/g, '\\"')}"`;
}

function wrap(text, width) {
  const single = text.replace(/\s+/g, ' ').trim();
  const words = single.split(' ');
  const lines = [];
  let line = '';
  for (const word of words) {
    if (!line) line = word;
    else if ((line + ' ' + word).length <= width) line += ` ${word}`;
    else {
      lines.push(line);
      line = word;
    }
  }
  if (line) lines.push(line);
  return lines.length ? lines : [''];
}
