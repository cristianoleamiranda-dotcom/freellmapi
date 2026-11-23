# BLACK FRIDAY ABYSS · reel + 3 historias (9:16)

Pieza de campaña para **ABYSS TATTOO Y PIERCING ♦ San Bernardo**:
**1 reel de 18 s** y **3 historias de 6 s**, 1080×1920 · 30 fps, H.264 High 4.2 ·
BT.709, con cama sonora de 120 BPM en el reel. Render offline y reproducible:
Python + Pillow + OpenCV + ffmpeg estático, sin servicios externos.

| Pieza | Archivo | Duración |
|---|---|---|
| Reel principal | `out/reel_black_friday_abyss_1080x1920_30fps.mp4` | 18.00 s (540 f) |
| Historia 1 · Pre Black Friday 26/11 | `out/story_1_pre_black_friday_1080x1920_30fps.mp4` | 6.00 s (180 f) |
| Historia 2 · Categorías | `out/story_2_categorias_1080x1920_30fps.mp4` | 6.00 s (180 f) |
| Historia 3 · Black Friday 27/11 + CTA | `out/story_3_black_friday_cta_1080x1920_30fps.mp4` | 6.00 s (180 f) |

Sala de revisión: **`out/visor.html`** · Escaleta y medidas: `out/manifest.json` ·
Transferencia de la referencia: [`research/MOTION-TRANSFER.md`](research/MOTION-TRANSFER.md).

## Referencia de motion (replicada)

`dropbox/type_01_pindown.io_1795195281.mp4` (póster cinético 12.03 s @ 30 fps) se
analizó fotograma a fotograma con `ffmpeg` + `cv2.calcOpticalFlowFarneback`
(`src/analyze_reference.py` → `research/motion_type_01.json` / `.png`):
push-in continuo por capa, cortes duros en la rejilla, un whip con desenfoque
direccional, un barrido de glifos gigantes y retículas de póster con tipografía
desbordada. Esa gramática se recrea 1:1 con la dirección de arte aprobada de
ABYSS (obsidiana, crema/hueso, cobre metálico, «BLACK sólido / FRIDAY
contorneado», diagonal −9°).

## Copy (suministrado por el estudio, sin inventar)

- `BLACK FRIDAY ABYSS TATTOO STUDIO` · `ABYSS TATTOO Y PIERCING ♦ San Bernardo`
- `PRE BLACK FRIDAY ABYSS: 26/11. INSCRIPCIÓN POR DM. ELIGE QUE PROMOCIÓN QUIERES.`
- `TATUAJE · JOYERÍA · PERFORACIONES · MÁQUINAS DE TATUAJE`
- `BLACK FRIDAY ABYSS: 27/11`
- CTA: `@abyss_tattoo_studio` (DM Instagram) y `wa.me/56947786839` (WhatsApp)

## Material y edición (NO TRANSABLE)

Todo el material es real y entra **editado**: etalonaje hiperrealista
(contraste + hombro de altas luces + saturación 0.80–0.88), duotono metálico
cálido (obsidiana → cobre → champán) o cromo para joyas/perforaciones, y sobre
el video completo grano de película, viñeta, halación cálida, flicker ±0.6 % y
gate weave sub-píxel. Fuentes: carpeta Dropbox `ABYSS_BLACK_FRIDAY_ASSETS`
(fotos, joyas, perforaciones, fachada, emblema) y repo `abysstattoo`
(clips reales de máquina/proceso, emblema alpha, tipografías).

| Plano | Material | Uso |
|---|---|---|
| Intro / sesión | `hero_film.mp4` t≈0.7 (still) | tatuador trabajando |
| Pre 26/11 | `18.jpg` | tatuaje floral black & grey |
| TATUAJE | `AV_SEL_27_0180.jpg` | manga realismo |
| JOYERÍA | `Meta_AI_…_170329.webp` (recorte central) | anillo mariposa |
| PERFORACIONES | `1000025791.JPG (1).webp` | hélix/lobe |
| MÁQUINAS | `hero_film.mp4` t≈2.1–3.9 (macro aguja) | video real |
| Cierre | `Meta_AI_…_170334.webp` (recorte central) | joya cromo |
| Marca | `emblema_abyss_alpha.png` | roundel |

## Zonas seguras

Texto esencial dentro de x ∈ [72, 1008], y ∈ [250, 1670] (UI de Instagram
reservada). La tipografía display puede desbordar el cuadro: es parte de la
gramática de la referencia.

## Pipeline

```
src/brand.py      paleta, tipografías (Anton + Montserrat), easing, grano/viñeta/halación
src/media.py      plates, etalonaje, duotono, cámara virtual afín, blur direccional
src/kinetic.py    capas (type/outline/photo/label/para/roundel/rule/box/sweep), whip_mix
src/timeline.py   escaletas del reel y las 3 historias
src/audio.py      cama 120 BPM (kick/hat/sub/riser/impacto en cortes y whips)
src/render.py     ensamblaje, encode x264 crf 17, posters, storyboards, manifest
src/analyze_reference.py  ingeniería inversa de la referencia (flujo óptico, cortes)
src/fetch_github.py       baja clips/tipografías/marca vía api.github.com
src/smoke.py              fotogramas de revisión rápidos (research/smoke_*.jpg)
```

Render completo:

```bash
PYTHONPATH=src python3 src/render.py all      # reel + 3 historias + posters + manifest
PYTHONPATH=src python3 src/render.py reel     # sólo el reel
PYTHONPATH=src python3 src/smoke.py reel      # revisión visual sin encodear

# duración ajustable (la escaleta es data-driven: se re-escalan claves y cortes)
PYTHONPATH=src python3 src/render.py reel --reel-dur 15      # → out/reel_black_friday_abyss_15s_…mp4
PYTHONPATH=src python3 src/render.py stories --story-dur 8   # historias de 8 s
```

El material fuente vive en `material/` y `../dropbox/` y está excluido de Git
(`.gitignore`); los entregables (`out/*.mp4`, posters, storyboards, visor y
manifest) sí se versionan, siguiendo la convención de `abyss-marca-15s`.
