# Publicar el hub y las skills

Orden recomendado. Los pasos 1 y 2 son requisito para los demás.

## 1. Resolver licencias

Ninguno de estos repos tiene archivo `LICENSE`:

- `sender-motion-kit`
- `sender-design-ops`
- `Rae`
- `abysstattoo`
- `webopen`

Sin licencia, un marketplace puede rechazar el paquete y nadie puede reutilizarlo con
claridad. Añade un `LICENSE` (MIT es lo más simple para skills) a cada repo antes de
publicar. `scroll-craft` ya es MIT.

Además, las skills `pixijs-*` de `Rae` son material derivado de la documentación de
PixiJS (MIT). Conserva la atribución en el `SKILL.md` o en un `NOTICE`.

## 2. Mover el hub a su propio repo

El hub es autocontenido. Dos opciones:

```bash
# Opción A: historial propio desde este checkout
git subtree split -P skills-hub -b skills-hub-export
# crea el repo vacío `skills` en GitHub y luego:
git push https://github.com/cristianoleamiranda-dotcom/skills.git skills-hub-export:main

# Opción B: copiar la carpeta tal cual a un repo nuevo
```

El repo debería llamarse `skills` para que coincidan las URLs de `dist/` y del
`plugin.json` (`https://github.com/cristianoleamiranda-dotcom/skills`).

Activa la validación en CI copiando `templates/skills-ci.yml` a `.github/workflows/`.

## 3. Publicar en ClawHub (OpenClaw)

`awesome-openclaw-skills` **no acepta enlaces a repos personales**: solo skills que ya
estén en ClawHub.

1. Instala la CLI: `npx clawhub --help` para ver los comandos disponibles en tu versión.
2. Publica cada skill (o el paquete) desde la CLI de ClawHub. El slug debe coincidir con
   el `name` del `SKILL.md`.
3. Verifica que la ficha quede en `https://clawhub.ai/<usuario>/<slug>`.
4. Abre el PR en `VoltAgent/awesome-openclaw-skills` añadiendo el enlace en la categoría
   correspondiente (`categories/coding-agents-and-ides.md`, `browser-and-automation.md`,
   etc.) y sigue su `CONTRIBUTING.md`.

Candidatas con más valor para esa lista: `sender-immersive-web-department`,
`scrollcraft-arena`, `motion-design`, `text-to-lottie`, `reverse-engineer-anything`,
`sender-video-pipeline`.

## 4. Publicar el marketplace de Cursor

`npm run pack` deja `dist/cursor-marketplace/` con la estructura que usa
`cursor/plugins`:

```
.cursor-plugin/marketplace.json
cristian-skills/.cursor-plugin/plugin.json
cristian-skills/skills/<slug>/SKILL.md
```

1. Copia el contenido a la raíz de un repo público (por ejemplo `skills`).
2. Comprueba que `plugin.json` tenga `name`, `version`, `description`, `author` y
   `skills: "./skills/"`.
3. Sigue el proceso de revisión de `cursor/plugins` (su README explica cómo se añaden
   plugins al marketplace oficial).

Mientras no haya revisión, cualquier persona puede usar el plugin localmente apuntando
Cursor al repo.

## 5. Publicar el marketplace de Claude Code

`dist/claude-marketplace/` incluye `.claude-plugin/marketplace.json` y el plugin:

```bash
/plugin marketplace add cristianoleamiranda-dotcom/skills
/plugin install cristian-skills
```

Funciona igual con una ruta local para probar:

```bash
/plugin marketplace add /ruta/a/dist/claude-marketplace
```

## 6. Instalación directa (sin marketplace)

```bash
# Claude Code / agentes compatibles
node src/install.mjs --target claude,agents --project /ruta/al/proyecto --git-exclude

# Cursor, como skills de proyecto
node src/install.mjs --target cursor --project /ruta/al/proyecto

# OpenClaw, global
node src/install.mjs --target openclaw --project ~/.openclaw
```

## Checklist antes de anunciar

- [ ] Cada repo de origen tiene `LICENSE`.
- [ ] `npm run validate` sin errores.
- [ ] `reports/INVENTARIO.md` revisado (duplicados y hallazgos).
- [ ] `scroll-craft` revisada por una persona: la skill se generó desde docs y el README
      del repo está corrupto.
- [ ] `dist/` regenerado con `npm run pack`.
- [ ] Los `SOURCE.json` apuntan al commit correcto.
