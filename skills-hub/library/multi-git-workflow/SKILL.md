---
name: multi-git-workflow
description: >
  Habilidad para hacer commits estandarizados y empujar tanto a GitHub como a GitLab.
metadata:
  source: cristianoleamiranda-dotcom/webopen
  source-path: .opencode/skills/git-workflow/SKILL.md
  source-commit: a2a87e5e5e2546f3f0462c0b8bcaac41c9cb3bcf
  category: flujo-trabajo
  status: fixed
  original-name: "Multi-Git Workflow"
---
# Flujo de Trabajo Git (GitHub + GitLab)

Cuando el usuario pida "guardar el proyecto", "subir cambios" o "hacer push":

1. Revisa el estado actual con `git status`.
2. Genera un commit siguiendo Conventional Commits (ej: `feat: add new button`, `fix: header padding`).
3. Ejecuta `git push all main` para enviar el código sincronizadamente a las instancias de GitHub y GitLab.
4. Recuerda al usuario que el pipeline de GitLab se disparará automáticamente.
