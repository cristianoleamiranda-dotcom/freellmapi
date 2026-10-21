# ¿Existe el repositorio de MiniMax Design?

**Sí, existe, pero no es lo que parece.** No hay un repositorio de "design system" ni de
motion graphics de MiniMax. Hay un **producto** llamado MiniMax Design y un **plugin de
ComfyUI** publicado en la organización oficial, con el nombre mal escrito.

Datos consultados en la API de GitHub el 2026-10-21.

## Lo oficial

| Repo | Qué es | Licencia | Estado |
|---|---|---|---|
| [`MiniMax-AI/minimax-desgin-plugin`](https://github.com/MiniMax-AI/minimax-desgin-plugin) | Plugin de ComfyUI para MiniMax Design (frontend + backend) | GPL-3.0 (derivado de ComfyUI) | 10 ★ · último push 2026-08-20 · ~35 MB |
| [`MiniMax-AI/skills`](https://github.com/MiniMax-AI/skills) | Skills de agente de MiniMax (frontend, Android, Flutter, iOS, React Native…) | MIT | 13.719 ★ · último push 2026-04-18 |
| [`MiniMax-AI/MiniMax-H3`](https://github.com/MiniMax-AI/MiniMax-H3) | El modelo de video H3 que alimenta el producto | sin licencia declarada | 10.279 ★ |

El propio README del plugin aclara qué es:

> «Este repositorio contiene **MiniMax Design Plugin for ComfyUI** […] se aplica a
> **MiniMax Design**: [design.minimax.cn](https://design.minimax.cn/) y
> [design.minimax.io](https://design.minimax.io/).»

Es decir: MiniMax Design es un producto de creación audiovisual (video, voz, música) que
usa ComfyUI por debajo. El repo oficial publica **solo el plugin**, como snapshot de
código abierto; no incluye modelos, binarios, dependencias ni herramientas internas.

## Ojo con el nombre

El repo oficial está escrito **`minimax-desgin-plugin`** (falta la «a» de *design*). Si
buscas `minimax-design` en GitHub encuentras sobre todo terceros, no la fuente oficial:

| Repo | Qué es | Señal de alerta |
|---|---|---|
| `MiniMax-design-H3/minimax-design` | «MiniMax Design Desktop… Download for Windows & Mac» | 7 ★, topics de *downloader/installer*, no pertenece al org oficial |
| `Minimax-Design/Minimax-Design.github.io` | «Public-facing site» | 0 ★, sin licencia, último push 2025-12 |
| varios `*-design-plugin`, `*-api`, `*-on-wine` | bridges, reverse proxies, instaladores | no oficiales |

Regla simple: si el repo no está bajo `github.com/MiniMax-AI/` o `design.minimax.io`, no
es la fuente. No instales ejecutables de terceros que dicen ser «MiniMax Design Desktop».

## Lo que sí sirve para tu trabajo

1. **`MiniMax-AI/skills`** tiene material directamente reutilizable para tu `skills-hub`:
   - `skills/frontend-dev/references/motion-recipes.md` — recetas de animación
     (scroll reveal con Framer Motion, springs, stagger).
   - `skills/android-native-dev/references/motion-system.md` — sistema de motion.
   - `skills/flutter-dev/references/animations.md` y
     `skills/react-native-dev/references/animations.md`.
   - `plugins/pptx-plugin/skills/design-style-skill/SKILL.md` — skill de estilo.
   Es MIT, así que se puede importar sin fricción. Si quieres, lo agrego como fuente en
   `skills-hub/src/config.mjs` y queda versionado con su commit, igual que tus repos.

2. **MiniMax Design (el producto)** sirve para generar B-roll o imágenes con H3, no para
   motion graphics con control de timeline. Para esta pieza no se usó: el montaje es
   determinista y reproducible en Python, y meter un modelo generativo habría roto esa
   propiedad.

3. **Para motion graphics de verdad**, el ecosistema útil es otro. Está en
   [`REPOS-MOTION-GRAPHICS.md`](REPOS-MOTION-GRAPHICS.md).

## Resumen en una línea

Existe el repo, pero es **un plugin GPL-3.0 de ComfyUI con el nombre mal escrito**, no un
design system: el producto se llama MiniMax Design y vive en `design.minimax.io`.
