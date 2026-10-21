---
name: scroll-craft
description: >
  Método y stack del sitio SENDER scroll-driven de scroll-craft (React 19 + Vite +
  GSAP + Lenis + Three.js): una sola narrativa, el scroll como cámara, WebGL solo en
  escritorio con puntero fino, datos reales sin inventar, i18n ES/EN completo y
  verificación con npm run build y npm run qa. Úsala como referencia al construir o
  auditar un sitio inmersivo con este stack.
license: MIT
metadata:
  category: diseno-web
  status: generated
  generated: from-docs
---

# ScrollCraft · sitio inmersivo SENDER

Esta skill se generó desde la documentación y los scripts del repo
[`cristianoleamiranda-dotcom/scroll-craft`](https://github.com/cristianoleamiranda-dotcom/scroll-craft).
No es una copia de un `SKILL.md` original: el repo se describe como «agent skill» pero
no incluye ese archivo, y su `README.md` está corrupto (contiene el código compilado de
`App.tsx`). Requiere revisión humana antes de publicarse.

## Cuándo usarla

- Vas a construir o rediseñar un sitio editorial inmersivo con scroll como eje.
- Necesitas el stack y las decisiones de arquitectura del sitio SENDER.
- Tienes que auditar que un sitio de este tipo no invente datos ni rompa móvil/reduced motion.

## Stack real del repo

- React 19 + Vite 7 + TypeScript.
- GSAP 3.13 y Lenis 1.3 para scroll suave y scrub.
- Three.js 0.180 con un solo renderer e import dinámico.
- `react-router-dom` 7 para rutas ES/EN.
- Fuentes self-hosted: `@fontsource/instrument-sans` e `@fontsource/ibm-plex-mono`.

## Arquitectura

Del `docs/ARCHITECTURE.md` del repo:

- Una sola narrativa con rutas de catálogo; el scroll es la cámara.
- `src/data` concentra los hechos: empresa, catálogo, proyectos, ingeniería.
- `src/sections`: Hero, Signal, About, Engineering, Products, Projects, Contact.
- `src/three/scenes`: SignalScene (WebGL), EngineeringScene (dibujo), ProjectScene (profundidad).
- `src/components/immersive` contiene el sistema de imagen; `src/components/motion` Lenis + canvas 2D.
- WebGL: un renderer, import dinámico, solo escritorio con puntero fino, dispose al desmontar.
  Móvil y `prefers-reduced-motion` usan canvas 2D.

## Invariantes

1. **Nada se inventa.** El contenido factual viene del repo `sender` y de sender.cl. El
   catálogo conserva `sourceUrl` por ficha. No se simulan cifras, premios ni instalaciones.
2. **El scroll manda.** Cada bloque es una escena; no hay secciones sueltas.
3. **Un solo contexto WebGL.** Nada de loops 3D en móvil ni con movimiento reducido.
4. **i18n completo.** ES y EN son capas completas; catálogo y proyectos viven como pares
   `{ es, en }` para que una clave no quede sin traducción.
5. **Imágenes reales.** Solo archivos presentes en el repo fuente; el alt describe el
   archivo y no afirma que sea una instalación concreta si la fuente no lo dice.
6. **Rutas espejo.** `/`, `/en`, `/productos`, `/productos/:categoria`, `/producto/:slug`
   y sus equivalentes en inglés.

## Comandos

```bash
npm install
npm run dev      # vite --host 0.0.0.0 --port 5173
npm run build    # tsc --noEmit + vite build + scripts/seo.mjs
npm run qa       # node qa/check.mjs
npm run seo      # regenera sitemap/SEO
```

## Verificación antes de entregar

- `npm run build` sin errores de TypeScript ni de Vite.
- `npm run qa` en verde.
- Revisar la preview en escritorio y en móvil; confirmar que reduced motion apaga el 3D.
- Confirmar que ningún dato del catálogo quedó sin `sourceUrl`.

## Referencias del repo

- `docs/ARCHITECTURE.md` — capas, rutas y presupuesto WebGL.
- `docs/CONTENT-INVENTORY.md` — qué contenido existe y qué se decidió no inventar.
- `docs/SKILLS.md` — skills y referencias usadas, y lo que se rechazó.
- `qa/check.mjs` — comprobaciones automáticas del sitio.
