# AUDITORÍA TÉCNICA — CAMPAÑA BLACK FRIDAY ABYSS TATTOO STUDIO
Fecha: 2026-11-23 · Rama: arena/9beaffaa-freellmapi · PR #9 (OPEN, MERGEABLE)
Herramientas de auditoría: src/audit_motion.py (flujo óptico Farneback), src/audit_grade.py
(saturación/luminancia/grano/clústeres k-means de paleta), src/audit_safezones.py (bbox de tinta
vs zona segura 72–1008 × 250–1670), src/audit_copies.py (strings verbatim), src/verify.py (QC),
ffprobe (especificaciones y etiquetado de color), Dropbox API (integridad).

## PUNTO 1 — FIDELIDAD AL MATERIAL DE REFERENCIA: PASS
- Referencia type_01: 12.033 s, 1 corte a los 2.73 s, flow_mean 0.76, pico 6.55.
- reel18 (18.0 s): eventos de flujo en la cuadrícula esperada [3.0, 7.2, 13.2] + whips
  (3.0–3.4, 13.2–13.6). match=True. flow_mean 0.363. push-in sostenido=True.
- reel15 (15.0 s): cortes proporcionales [2.5, 6.0, 11.0] verificados. match=True.
- Gramática replicada: push-in lento, whip-blur entre escenas, tipografía escalonada con
  ease-out, cierre con CTAs (ver MOTION-TRANSFER.md).
- Duración ajustable REAL: `--reel-dur 15` y `--story-dur` re-temporizan cortes y keyframes.

## PUNTO 2 — EDICIÓN Y TEORÍA DE COLOR (NO TRANSABLE): PASS
- Ninguna pieza usa material crudo: toda placa pasa por grade (exposición, duotono,
  halación, viñeta, flicker ±0.6%, gate weave) + grano de película en cada frame.
- Evidencia: render t=5.0 s sat 102.17 / lum_std 79.02 vs fuente 18.jpg sat 81.1.
- Grano: σ 6.3–9.4 según pieza (consistente, no plano; baseline de sombra plana σ≈3.6).
- Clústeres k-means del frame de cierre (16.6 s): black (10,7,5) w .513 · obsidian (22,14,11)
  w .310 · cream (240,230,222) w .106 · chrome (212,203,195) w .036 · copper (179,135,106)
  w .028 → paleta de marca confirmada (Δ≤25.2 por token).

## PUNTO 3 — COPIES EXACTOS, FECHAS, RUBROS Y CTAs: PASS (tras corrección)
- 16/16 strings obligatorios verbatim en timeline+brand, incluidas ♦, 26/11, 27/11,
  INSCRIPCIÓN POR DM, @abyss_tattoo_studio y wa.me/56947786839.
- Hallazgo auditado: story_2 decía "ELIGE QUE PROMOCIÓN QUIERES" sin punto final →
  CORREGIDO a "ELIGE QUE PROMOCIÓN QUIERES." (variante exacta del brief) y re-renderizado.
- URL IG completa: se añadió https://www.instagram.com/abyss_tattoo_studio a README,
  visor.html y manifest.json (campo cta). En pantalla se mantiene el handle por legibilidad.

## PUNTO 4 — ESPECIFICACIONES TÉCNICAS, ZONAS SEGURAS, ENTREGABLES: PASS (tras corrección)
- 1080×1920 · 30 fps · H.264 High@4.2 · yuv420p · AAC-LC 48 kHz estéreo (reels) · +faststart.
- Color: bt709 completo tras rebuild (antes primaries=bt709 con transfer/matrix unknown →
  se añadió -bsf:v h264_metadata colour_primaries=1:transfer=1:matrix=1). ffprobe ahora
  reporta "yuv420p(tv, bt709, progressive)".
- Zonas seguras: 5 violaciones de tinta detectadas (reel18 S1 etiqueta/micro 12–25 px,
  S2 copy 69 px, micro 32 px; story3 6 px; reel18 micro cierre 3 px) → TODAS corregidas
  (x 560→545/640→540, track 5→3, y 1664→1654). Re-run: SIN VIOLACIONES.
- HTTP Range: GET / → 302 /visor.html; Range bytes=0-1023 → 206 en las 5 piezas (serve_preview.py).
- Entregables: 5 mp4 + 12 posters + 5 storyboards + manifest.json + qc.json + visor.html.

## PUNTO 5 — CÓDIGO, GIT, INTEGRIDAD DROPBOX, PR: PASS (tras corrección)
- Hallazgos: __pycache__ re-tracked y carpetas de trabajo de auditoría sin ignorar →
  git rm --cached + .gitignore extendido (research/audit_frames_*/, *.pyc).
- Sin masters (out/masters/ gitignored), sin material/, sin wav, sin logs pesados en git.
- Integridad SHA-256 local↔Dropbox: reel18, story1, story2, story3 y reel15 idÉnticos
  byte a byte (pre-rebuild; tras rebuild de correcciones se re-suben y re-verifican).
- Originales Dropbox /ABYSS_BLACK_FRIDAY_ASSETS/material: 18 archivos intactos (revs 19–20/11).
- ENTREGA_ARENA_2026-11-23: 27 archivos. PR #9 OPEN, MERGEABLE.

## VEREDICTO
APROBADO — con las observaciones del audit aplicadas y re-verificadas en esta misma sesión
(zonas seguras, punto final story2, URL IG en docs, etiquetado bt709 completo, higiene git).

## ANEXO POST-REBUILD (verificación final)
- QC verify.py: PASS ×5. ffprobe: 18.00/15.00/6.00/6.00/6.00 s · h264 High · yuv420p(tv, bt709, progressive) · 30 fps · AAC-LC 48 kHz estéreo en reels.
- Re-run auditores sobre renders nuevos: safezones SIN VIOLACIONES · copies PASS (URL IG en docs OK) · grade PASS (grano σ 6.3–8.1, paleta 5/5 tokens).
- Dropbox: 5 mp4 + docs (manifest, qc, visor, README, AUDITORIA) re-subidos; descarga y `cmp` → reel18 y story2 IDÉNTICOS byte a byte (tamaños 31590916 y 10007543 = local).
- SHA-256 finales:
  reel18   8b3d448bbf9bb7837b8aa2ce8268ec1bba75875c0cbd5c7ac3ced3ca66fe4c88
  reel15s  05b9ac0415eb913d5e0db7d375709a4b1e94a2e5feac53542a2482035e837e46
  story_1  1f2ac7481e288a0302614c06cf8831b98d88b3ae9d35e052195a83d64702694f
  story_2  533a32c65f09942515e7ffe6fcd5e348b8591064c9e52a536873a79690083946
  story_3  fa0d41a00df6cda01d1a9ed366590e17c0dbb6f721ac4c448a5d10c3a5148409
- Nota: audit_motion no se re-ejecutó sobre los renders nuevos porque las correcciones solo
  movieron overlays de texto (posición/tracking/punto); el movimiento de placas y whips es
  idéntico al auditado (match=True en ambas variantes de duración).

## VEREDICTO FINAL: APROBADO
