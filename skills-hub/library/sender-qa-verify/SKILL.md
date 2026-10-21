---
name: sender-qa-verify
description: >
  Protocolo de QA duro antes de publicar: curl a producción con tag BUILD, conteo de marcadores,
  parse check de JS, rescates git sin force-push y CI con html-validate + Lighthouse. Úsala antes
  de anunciar o empujar un cambio.
metadata:
  source: cristianoleamiranda-dotcom/sender-design-ops
  source-path: sender-design-ops/skills/SKILL-qa-verify.md
  source-commit: 639aed9b21eb54a0c8a1a007d0d21d1a6512bd91
  category: diseno-web
  status: fixed
---
# SKILL · QA y verificación dura
1. Ningún cambio se anuncia sin curl de producción: tag BUILD, contadores de marcadores (clases nuevas, data-*), HTTP 200 de cada asset crítico.
2. Parse check de JS antes del push (vm.SourceTextModule) + grep de bare imports ('from gsap/lenis') en sitios sin bundler.
3. Rescates git: fetch + reset --hard FETCH_HEAD + re-aplicar ediciones con asserts; binarios a /tmp antes de rebase; NUNCA force-push.
4. CI: html-validate + LHCI (a11y ≥.85 error, perf warn) en cada push; leer logs del job por API.
5. Cache del usuario: entregar siempre URL con parámetro fresco (?v=N) y decir qué tag BUILD mirar; si el tag no coincide → es cache, no el sitio.
6. Deuda: lo que no se cumple se documenta con estado y plan (perf headless), no se oculta.
