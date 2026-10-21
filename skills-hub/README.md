# Skills Hub · cristianoleamiranda-dotcom

Biblioteca personal de **agent skills**. Importa las skills que están repartidas en mis
repos, las normaliza a un `SKILL.md` válido, elimina duplicados, las valida, las instala
en el proyecto que estés usando y las empaqueta para Cursor, Claude Code y OpenClaw.

Todo se genera desde `src/config.mjs` y se reconstruye con un comando. `library/` no se
edita a mano: se regenera desde los repos de origen y cada skill conserva un
`SOURCE.json` con repo, ruta y commit exacto.

## Estado

Hay **6 repos de origen** con skills de distinta época y formato:

| Repo | Qué aporta | Formato original |
|---|---|---|
| `sender-motion-kit` | Departamento de web inmersiva (scroll, film, 3D, QA, Awwwards) | `SKILL.md` válido |
| `sender-design-ops` | Design system, motion scroll, QA y pipeline de video | `.md` sin frontmatter + `AGENTS.md` |
| `Rae` | 32 skills de PixiJS v8, motion design, Lottie y REA | `SKILL.md` válido (duplicado en dos carpetas) |
| `abysstattoo` | Suite de video/imagen para Abyss Tattoo Studio | `SKILL.md` válido |
| `webopen` | Open Design sync, git multi-remoto, diseño UI | `SKILL.md` con `name` inválido |
| `scroll-craft` | Sitio SENDER scroll-driven | sin `SKILL.md` (se generó desde `docs/`) |

El inventario completo, con commits, licencias y hallazgos, se regenera en
[`reports/INVENTARIO.md`](reports/INVENTARIO.md).

## Comandos

```bash
cd skills-hub

npm run sync       # clona/actualiza los repos y reconstruye library/
npm run validate   # valida frontmatter, nombres, enlaces y duplicados
npm run install    # activa las skills en .claude/skills y .agents/skills
npm run pack       # genera dist/openclaw, dist/cursor-marketplace y .tar.gz
npm run all        # sync + validate + pack
```

Sin dependencias: solo Node 20 o superior.

### Instalar en un proyecto

```bash
# Claude Code + agentes que leen .agents/
node src/install.mjs --target claude,agents --project /ruta/al/proyecto

# Cursor (skills de proyecto)
node src/install.mjs --target cursor --project /ruta/al/proyecto

# OpenCode
node src/install.mjs --target opencode --project /ruta/al/proyecto

# OpenClaw: global o por workspace
node src/install.mjs --target openclaw --project ~/.openclaw
node src/install.mjs --target openclaw --project /ruta/al/proyecto
```

Opciones útiles:

- `--link` crea enlaces simbólicos en vez de copiar (la biblioteca queda como fuente única).
- `--only slug,slug` instala solo algunas skills.
- `--git-exclude` añade la carpeta instalada a `.git/info/exclude` (no toca `.gitignore`
  ni ensucia `git status`).
- `--dry-run` muestra qué haría.
- `--force` sobrescribe una carpeta que ya existía sin el marcador del hub.

El instalador es idempotente: guarda un `.skills-hub.json` en cada destino y borra solo
lo que instaló antes.

## Dónde lee cada cliente

| Cliente | Ruta de skills de proyecto |
|---|---|
| Claude Code | `.claude/skills/<slug>/SKILL.md` |
| Cursor | `.cursor/skills/` o plugin con `.cursor-plugin/plugin.json` |
| OpenCode | `.opencode/skills/` |
| OpenClaw | `<proyecto>/skills/` o global `~/.openclaw/skills/` |
| Convención abierta | `.agents/skills/` |

El formato de cada `SKILL.md` cumple lo que piden los tres ecosistemas: `name` en
kebab-case, `description` de máximo 1024 caracteres y cuerpo en Markdown.

## Estructura

```
skills-hub/
├── src/
│   ├── config.mjs        # repos, rutas, slugs, categorías y descripciones curadas
│   ├── sync.mjs          # clona, normaliza, deduplica y escribe library/
│   ├── validate.mjs      # valida la biblioteca
│   ├── install.mjs       # activa en .claude, .agents, .cursor, .opencode, OpenClaw
│   ├── pack.mjs          # genera los paquetes de dist/
│   ├── report.mjs        # inventario y reporte de validación
│   └── frontmatter.mjs   # parser/serializador YAML mínimo
├── curated/              # skills redactadas a mano (scroll-craft)
├── library/              # GENERADO: una carpeta por skill
├── reports/              # GENERADO: INVENTARIO.md y VALIDACION.md
├── docs/PUBLICAR.md      # cómo llevarlo a un repo propio y a los marketplaces
├── templates/            # CI de validación para cuando sea repo independiente
├── registry.lock.json    # GENERADO: commits, duplicados y hallazgos
└── skills.json           # GENERADO: manifiesto plano para otros scripts
```

## Cómo añadir una skill

1. Añade la entrada en `src/config.mjs` (`repo`, `source`, `slug`, `category`, `tags`).
2. Si el archivo no trae frontmatter, escribe `description` en la entrada.
3. Ejecuta `npm run sync && npm run validate && npm run install`.
4. Revisa `reports/INVENTARIO.md` y haz commit.

Si la skill vive en un repo nuevo, añade el repo completo a `REPOS`; `sync` lo clona en
`.cache/repos/` (ignorado por git) y registra el commit en el lock.

## Normalizaciones que aplica

- `name` y carpeta en kebab-case; renombra `Ultimate Web Designer` → `ultimate-web-designer`.
- Frontmatter canónico con `name`, `description`, `license` y `metadata` de origen.
- `description` recortada a 1024 caracteres (una sola skill la superaba).
- Duplicados exactos omitidos y registrados (`Rae` vs `abysstattoo`).
- Copia de `references/` y archivos hermanos; omite assets de más de 5 MB.
- Enlaces relativos rotos detectados en la validación.

## Licencias

`scroll-craft` es MIT. Los demás repos **no tienen archivo LICENSE**. Las skills se
pueden usar en local, pero antes de publicarlas en un marketplace conviene añadir una
licencia a cada repo de origen. El detalle por skill está en `reports/INVENTARIO.md` y
en los `LICENCIAS.md` de cada paquete.

## Publicar

Ver [`docs/PUBLICAR.md`](docs/PUBLICAR.md). Resumen:

- **OpenClaw/ClawHub**: la lista `awesome-openclaw-skills` solo acepta skills publicadas
  en ClawHub; hay que publicarlas con su CLI y enviar el enlace.
- **Cursor**: `dist/cursor-marketplace/` ya tiene el `marketplace.json` y el
  `plugin.json` que pide el formato de `cursor/plugins`.
- **Claude Code**: `dist/claude-marketplace/` funciona con `/plugin marketplace add`.

## Nota sobre este checkout

Este hub vive dentro del fork `freellmapi` porque la sesión de Arena está fijada a esa
rama. Es autocontenido: para llevarlo a su propio repo, copia la carpeta o usa
`git subtree split -P skills-hub -b skills-hub`.

## Referencias de formato

- [`cursor/plugins`](https://github.com/cursor/plugins) — estructura `.cursor-plugin/marketplace.json`
  y `plugin.json` que replica `dist/cursor-marketplace/`.
- [`VoltAgent/awesome-openclaw-skills`](https://github.com/VoltAgent/awesome-openclaw-skills) —
  ubicaciones de instalación de OpenClaw (`~/.openclaw/skills/` y `<proyecto>/skills/`) y regla
  de publicación: solo skills que ya estén en ClawHub.
- [`sindresorhus/awesome`](https://github.com/sindresorhus/awesome) y
  [`vinta/awesome-python`](https://github.com/vinta/awesome-python) — criterios de curación de
  listas que conviene imitar: una entrada por recurso, descripción breve y enlace directo.
