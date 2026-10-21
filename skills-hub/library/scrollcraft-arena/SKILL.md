---
name: scrollcraft-arena
description: >
  Flujo ScrollCraft-Arena para construir landings premium scroll-driven/3D: entrevista obligatoria
  antes de codificar, principios anti-template, scroll como interfaz, assets reales, verificación
  previa a entregar y feedback por rondas. Úsala al iniciar un sitio nuevo o un rediseño
  inmersivo.
metadata:
  source: cristianoleamiranda-dotcom/sender-design-ops
  source-path: AGENTS.md
  source-commit: 639aed9b21eb54a0c8a1a007d0d21d1a6512bd91
  category: diseno-web
  status: fixed
---
# SKILL: ScrollCraft-Arena

Construye landing pages premium scroll-driven / 3D. Este archivo es el "skill" versionado:
cualquier agente que lo lea al inicio de sesión debe seguir estas reglas.

## 1. Entrevista obligatoria ANTES de escribir código
Usa `ask_user` (o preguntas en chat) con estas 6 preguntas y guarda las respuestas en `docs/brief.md`:
1. **Scroll journey:** ¿qué ve el visitante primero y en qué orden después?
2. **Creencia final:** ¿qué debe creer el visitante al terminar? (1 oración, no features)
3. **Assets reales:** ¿qué fotos/branding/copy existen ya (en el repo o adjuntos)?
4. **Signature move:** una cosa que este sitio haga y ningún otro sitio hace.
5. **Calmo vs. intenso:** ¿dónde debe sentirse calmo y dónde intenso?
6. **Vibe:** editorial / energético / minimalista / oscuro / corporativo…

## 2. Principios de diseño (nunca template fijo)
- Espaciado generoso, jerarquía tipográfica clara, paleta de marca consistente.
- Instrucción emocional por sección ("debe sentirse confiable/premium/urgente").
- Cada sitio debe salir único según el brief. Prohibido el "AI slop" genérico.

## 3. Scroll como interfaz
- Stack: GSAP + ScrollTrigger, Lenis (smooth scroll), Three.js / React Three Fiber para 3D.
- El progreso del scroll controla el estado de la animación: reversible adelante/atrás sin romperse.
- Velocidad perceptible: si la animación termina antes de que el usuario entienda qué pasó, está mal.
- Máximo 2–3 momentos intensos por página; el resto calmo.
- Respetar `prefers-reduced-motion` (degradar a fades simples).
- Móvil: las animaciones complejas degradan a versiones simples.

## 4. Assets
- Generar lo que falte con `generate_image`, incluyendo SIEMPRE la paleta de marca y el estilo en el prompt.
- Guardar en `public/assets/`; comprimir a WebP; videos < 5 MB.
- Modelos 3D: primitivas por código o GLB comprimido (Draco).
- Datos vivos: usar `fetch_page`/`web_search`/APIs públicas para números reales cuando el brief lo pida.

## 5. Verificación antes de entregar
- `npm run build` sin errores.
- `curl` a rutas y assets → sin 404.
- Screenshots por sección/keyframe (Playwright headless si está disponible).
- Reportar al usuario qué se verificó y qué debe revisar él en el live preview.

## 6. Feedback iterativo
- Cada ronda de feedback = un commit con mensaje descriptivo (`fix: hero + velocidad globo (feedback r1)`).
- Responder punto por punto; confirmar lo que se elimina y lo que se conserva.

## 7. Deploy
- `git push` a GitHub → GitHub Pages / Vercel / Netlify con CI (build + Lighthouse + link checker).
