---
name: open-design-sync
description: >
  Flujo de trabajo para integrar artefactos de Open-Design al proyecto local
metadata:
  source: cristianoleamiranda-dotcom/webopen
  source-path: .opencode/skills/design-sync/SKILL.md
  source-commit: a2a87e5e5e2546f3f0462c0b8bcaac41c9cb3bcf
  category: flujo-trabajo
  status: fixed
  original-name: "Open-Design Sync"
---
# Flujo de Integración de Open-Design

Cuando el usuario pida "sincronizar diseños" o "procesar UI":

1. Inspecciona los archivos recientes en la carpeta `src/components/` o las descargas generadas por el plugin de Open-Design.
2. Extrae los tokens visuales (colores, tipografías) y colócalos en `src/design-tokens/`.
3. Informa al usuario: "He adaptado los componentes generados por Open-Design a la estructura del proyecto".
