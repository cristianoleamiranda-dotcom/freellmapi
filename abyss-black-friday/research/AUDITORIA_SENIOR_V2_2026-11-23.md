# AUDITORÍA TÉCNICA SENIOR v2 — BLACK FRIDAY ABYSS TATTOO STUDIO
**Fecha:** 2026-11-23 · **Rama:** `arena/9beaffaa-freellmapi` · **PR:** #9 (OPEN, MERGEABLE/CLEAN)
**Alcance:** repo `freellmapi/abyss-black-friday` + Dropbox `/ABYSS_BLACK_FRIDAY_ASSETS`
(referencia `type_01_pindown.io_1795195281.mp4`, `material/` y `ENTREGA_ARENA_2026-11-23/`).
**Segunda pasada:** sustituye las conclusiones de `AUDITORIA_2026-11-23.md` en los puntos 1 y 4c,
donde la instrumentación de la primera pasada medía mal (ver §0).

---

## 0. Método e instrumentación (y los 4 defectos de medición corregidos)

Herramientas usadas en esta pasada, todas en el repo y re-ejecutables:

| Script | Qué mide |
|---|---|
| `src/audit_motion_v2.py` | flujo óptico Farneback con magnitudes **normalizadas al ancho**, cortes por correlación de histograma + salto robusto de MAD, whips por pico de flujo con caída de nitidez (Laplaciano), curvas en **tiempo normalizado** y Pearson vs referencia |
| `src/audit_zoom_validate.py` | curva de zoom que aplica el renderer (por escena) + validación empírica con placa estática y `matchTemplate` multi-escala |
| `src/audit_final_checks.py` | bitstream H.264 real (`trace_headers`: profile/level/chroma/bit depth/aspect), línea de audio completa, grano en **tonos medios**, push-in de la referencia en ventanas libres de cortes |
| `src/audit_grade_v2.py` | negros/saturación/contraste de placas crudas vs piezas entregadas, σ de grano por frame, histograma de tonos con % de tonos **prohibidos** por el manual de marca |
| `src/audit_legibility.py` | altura de mayúscula real (métrica de fuente) y **contraste WCAG medido sobre el frame entregado** por capa de texto |
| `src/audit_safezones.py` | bbox de tinta vs zona segura 72–1008 × 250–1670 |
| `src/audit_copies.py` | 16 strings verbatim + presencia de la URL IG completa en docs/visor/manifest |
| `scripts/dropbox_content_hash.py` | `content_hash` estilo Dropbox local, para integridad sin descargar |

**Defectos de instrumentación detectados y corregidos en esta pasada** (la auditoría también
se audita a sí misma):

1. `analyze_reference.py` / `audit_motion.py` redimensionaban **todo** a 180×225, que es el
   aspecto 4:5 de la referencia: los renders 9:16 se aplastaban y las magnitudes de flujo no
   eran comparables. → v2 usa ancho común 270 px preservando aspecto y normaliza por ancho.
2. Detección de cortes con umbral fijo sobre MAD a esa escala mínima: **perdía eventos**.
   → v2 usa correlación de histograma + mediana/MAD robusta.
3. `audit_legibility.py` v1 aplicaba dos veces la división por 255 en la curva sRGB: daba
   contraste 1.00 en todos los textos (falso FAIL). Además medía capas con `alpha=0`.
   → corregido; ahora sólo mide capas con `alpha ≥ 0.99`.
4. El zoom medido por ajuste afín del flujo sobre el frame completo **no es válido** en estas
   piezas: las placas son vídeo (el sujeto se mueve dentro del encuadre) y el frame lleva
   tipografía, scrim, viñeta y grano estáticos que no hacen zoom. Residuo afín 27–36 px.
   → sustituido por curva declarada del renderer + validación con placa estática (error 0,19 %).

---

## 1. Fidelidad visual y cinemática a la referencia — ⚠️ **WARN**

### 1.1 La referencia, caracterizada (no asumida)
`type_01_pindown.io_1795195281.mp4`: **720×900 (aspecto 0.800 = 4:5)**, 361 frames @ 30 fps,
12.033 s, 1.900.717 B.

- Integridad del contenedor: átomos `ftyp`(32) + `moov`(4.812) + `free`(8) + `mdat`(1.895.865)
  = 1.900.717 B = tamaño del archivo → **contenedor completo**.
- Decodificación: **361/361 frames OK (100 %)** con OpenCV.
- ⚠️ El stream **no es estrictamente conforme**: ffmpeg 9.0.2 emite
  `Invalid NAL unit size (11659 > 11333)`, `partial file`, `Error splitting the input into NAL units`.
  Decodificadores estrictos pueden descartar imágenes. Es un defecto del **archivo fuente**, no de
  nuestra entrega (nuestras 5 piezas: 0 errores de decodificación).
- Identidad: `sha256 945c337c3a78743c…`, `content_hash` Dropbox `f59b8fda78298ede…` =
  **idéntico** al de `/ABYSS_BLACK_FRIDAY_ASSETS/material/type_01_pindown.io_1795195281.mp4`
  → el enlace que me pasaste y el material de Dropbox son el mismo archivo.

### 1.2 Gramática de movimiento de la referencia
- 1 corte duro en **t = 2.733 s** (t/dur 0.227) y 1 whip/blur en **t = 2.367 s** (0.197).
- `flow_norm` medio **0.00698** (fracción de ancho por frame), pico **0.06278** en t = 8.7 s;
  a resolución nativa el pico absoluto está en t ≈ 2.73 s (29.46 px/frame) con un segundo
  máximo en t ≈ 4.77 s (25.19) que la instrumentación v1 no reportaba.
- Cámara **no afín** (residuo medio del ajuste 36.24 px) y **no es un push-in sostenido**:
  en ventanas libres de cortes alterna zoom-out y zoom-in —
  `+0.76 %/s` (t0=0), `−10.15` (4 s), `−5.26` (5 s), `−8.41` (6 s), `+2.56` (7 s),
  `+2.06` (8 s), `+1.90` (9 s), `−0.85` (10 s), `+1.29` (11 s); 56 % de ventanas expansivas.

### 1.3 Lo que entregamos, medido
| Pieza | flow_norm medio | ratio vs ref | pico (t) | whips/blurs detectados | cortes duros |
|---|---|---|---|---|---|
| reel18 | 0.00208 | **0.30×** | 0.05329 @ 7.233 s (0.85× del pico ref) | 7 grupos: 2.87–3.13, 3.60, 7.20–7.33, 8.67–8.83, 10.17–10.30, 11.67–11.87, 13.03–13.17 | 0 |
| reel15 | 0.00231 | **0.33×** | 0.05384 @ 6.033 s | 2.40–2.60, 6.00–6.13, 7.23–7.37, 8.47–8.60, 9.70–9.90, 10.90–11.00 | 0 |
| story1 | 0.00091 | 0.13× | 0.01875 @ 3.033 s | 3.00 | 0 |
| story2 | 0.00156 | 0.22× | 0.00941 @ 4.633 s | 1.53, 3.03, 4.53 | 0 |
| story3 | 0.00117 | 0.17× | 0.03085 @ 2.833 s | 2.82 | 0 |

- **Rejilla de eventos: PASS.** Los whips caen sobre la rejilla diseñada (reel18: 3.0 / 7.2 / 13.2
  + los 4 pasos escalonados de categorías; reel15: 2.5 / 6.0 / 11.0). Coincidencia exacta con
  `timeline.py` y con los beats declarados en `manifest.json`.
- **Pearson de la curva de flujo en tiempo normalizado vs referencia:** reel18 `+0.166`,
  reel15 `+0.162`, story1 `+0.057`, story2 `−0.165`, story3 `+0.147` → **correlación débil**.
  Se replica el *vocabulario* (whip-blur, type escalonado, push-in), no la *densidad* de movimiento.
- **Push-in: PASS (verificado de forma determinista).** Curva aplicada por el renderer:
  reel18 S1 1.050→1.200 (**+4.78 %/s**, +14.3 %), S2 1.060→1.240 (+4.48 %/s), S3 1.000→1.100
  (+1.67 %/s, 4 placas); story1 S1 +6.05 %/s, S2 +4.00 %/s; story2 +1.67 %/s; story3 S2 +3.87 %/s.
  Validación empírica con placa estática: zoom **medido 1.1450× vs declarado 1.1429× → error 0.19 %**
  (score `matchTemplate` 0.945). El renderer aplica exactamente el push-in de la escaleta.

### 1.4 Duración variable — ✅ PASS (con 1 defecto de código encontrado y corregido)
Re-escalado proporcional verificado **sin re-editar**, de 10 a 30 s (reel) y de 3 a 12 s (historias):

| `--reel-dur` | cortes resultantes | whip dur |
|---|---|---|
| 10 | 1.6667 / 4.0 / 7.3333 | 0.2222 s |
| 12 | 2.0 / 4.8 / 8.8 | 0.2667 s |
| 15 | 2.5 / 6.0 / 11.0 | 0.3333 s |
| 18 | 3.0 / 7.2 / 13.2 | 0.4000 s |
| 20 | 3.3333 / 8.0 / 14.6667 | 0.4444 s |
| 25 | 4.1667 / 10.0 / 18.3333 | 0.5556 s |
| 30 | 5.0 / 12.0 / 22.0 | 0.6667 s |

Historias: 3 s → corte 1.5; 6 s → 2.8/3.0; 8 s → 3.73/4.0; 12 s → 5.6/6.0. Las claves se extienden
0.4 s·f más allá de la duración (cola de seguridad inofensiva: el render corta en `duration × FPS`).

🐞 **Defecto encontrado y corregido esta pasada:** `render.scale_piece()` **mutaba in-place** la
escaleta del llamador. Dos llamadas consecutivas sobre el mismo objeto (p. ej. generar varias
variantes de duración en un proceso) **componían el factor f** y corrompían todos los tiempos.
Fix aplicado en `src/render.py` (deepcopy de entrada) y verificado: 3 llamadas encadenadas
(12 → 20 → 15 s) devuelven `[2.5, 6.0, 11.0]` exactos.

### 1.5 Dictamen punto 1: **WARN**
PASS en gramática, rejilla de eventos, whips, push-in (validado al 0.19 %) y duración variable.
**WARN porque la energía de movimiento es 0.30–0.33× la de la referencia y la correlación de
curvas es débil (+0.16)**, y porque la cámara de la referencia (zoom-out de hasta −10 %/s,
movimiento no afín, un corte duro) es más agresiva que nuestro push-in uniforme. Corrección P2.

---

## 2. Requisito NO TRANSABLE: material editado, color de marca y grano — ✅ **PASS**

### 2.1 Ningún plano usa material crudo (medido, no declarado)
Mismos medidores sobre las **placas fuente sin procesar** y sobre las **piezas entregadas**:

| Métrica | Crudo (`material/film/*.mp4`) | Entrega (5 piezas) | Δ |
|---|---|---|---|
| negros (percentil 1) | 4.7 | 2.5 | **−2.2** (negros más profundos) |
| saturación media | 69.7 | 111.5 | **+41.8** |
| contraste (σ luminancia) | 51.4 | 60.7 | **+9.3** |
| blancos (p99.9) | — | 216.6–233.3 | altas luces controladas, sin clipping masivo |

Por pieza: reel18 negros 2.71 / sat 109.6 / σlum 65.3; reel15 2.61 / 109.9 / 65.4;
story1 2.43 / 115.1 / 50.0; story2 2.43 / 116.2 / 61.4; story3 2.37 / 106.6 / 61.6.

### 2.2 Film grain consistente y natural
σ del residuo de alta frecuencia medida **sólo en tonos medios** (40 ≤ lum ≤ 210), cada 5 frames:

| Pieza | frames | σ min | σ media | σ max | CV | % frames con σ ≥ 2.0 |
|---|---|---|---|---|---|---|
| reel18 | 107 | 0.93 | **9.66** | 21.20 | 0.42 | 98.1 % |
| reel15 | 87 | 0.88 | **10.07** | 21.29 | 0.43 | 97.7 % |
| story1 | 34 | 1.33 | 8.37 | 9.74 | **0.18** | 97.1 % |
| story2 | 35 | 5.63 | 9.27 | 20.16 | 0.40 | **100 %** |
| story3 | 35 | 1.88 | 9.60 | 15.94 | 0.35 | 97.1 % |

CV 0.18–0.43 → grano **estable** (no parpadea). Los frames por debajo de σ 2.0 son sombras casi
planas con pocos píxeles de tono medio, donde el encoder H.264 (crf 21) suaviza el ruido: es una
limitación de la medición/codec, no ausencia de grano (el grano se genera por frame en
`kinetic.py`, σ≈3.6 + flicker ±0.6 % + gate weave).

### 2.3 Teoría de color de marca y colores prohibidos
Histograma de tonos sobre píxeles saturados (S > 90, V > 40), OpenCV H 0–179:

| Pieza | cobre (H 5–20) | crema (H 20–35) | amarillo retail | rojo retail | neón verde/cian | magenta |
|---|---|---|---|---|---|---|
| reel18 | **98.9 %** | 0.35 % | 0.21 % | 0.73 % | 0.11 % | **0.0 %** |
| reel15 | 98.4 % | 0.66 % | 0.27 % | 0.69 % | 0.29 % | 0.0 % |
| story1 | 99.2 % | 0.02 % | 0.0 % | 0.75 % | 0.0 % | 0.0 % |
| story2 | 94.2 % | 2.70 % | **2.05 %** | 0.69 % | **2.14 %** | 0.0 % |
| story3 | 96.4 % | 0.43 % | 0.0 % | 0.06 % | 0.0 % | 0.0 % |

Manual de marca (`feat/abyss-black-friday-hyperframes`, dirección "02 — CORTE"): prohibidos
amarillo/rojo retail, neón/cyberpunk, magenta. **Máximo observado 2.14 % (story2) → muy por
debajo del umbral de auditoría (12 %)**; el resto es cobre/ámbar cálido sobre obsidiana.
Clústeres k-means del frame de cierre (auditoría v1, re-verificados): black (10,7,5) w 0.513 ·
obsidian (22,14,11) w 0.310 · cream (240,230,222) w 0.106 · chrome (212,203,195) w 0.036 ·
copper (179,135,106) w 0.028 → **5/5 tokens de paleta**, Δ ≤ 25.6.

**Observación menor:** story2 concentra el mayor desvío (2.05 % amarillo + 2.14 % neón), aportado
por los reflejos cromo de la placa de joyería. Corrección opcional P5.

---

## 3. Copys, fechas, rubros y CTAs exactos — ✅ **PASS** (1 observación de copy no textual)

- **16/16 strings obligatorios verbatim** en `timeline.py` + `brand.py`, y por pieza
  (`audit_copies.py` re-ejecutado sobre el estado actual): reel18 OK · reel15 OK · story1 OK ·
  story2 OK · story3 OK. Incluye `♦`, `26/11`, `27/11`, `INSCRIPCIÓN POR DM.`,
  `ELIGE QUE PROMOCIÓN QUIERES.`, los 4 rubros y `wa.me/56947786839`.
- **CTA Instagram:** en pantalla `@abyss_tattoo_studio` (handle, por legibilidad) y la URL
  completa `https://www.instagram.com/abyss_tattoo_studio` en `README.md`, `out/visor.html` y
  `manifest.json → cta.instagram` → verificación `OK`. El parámetro `?fqnt=MWZvZHQxdTV2MHVmbA==`
  no se muestra en pantalla (observación O3, con comando si se quiere literal).
- ⚠️ **Observación (copy no textual en pantalla):** el pie de la escena 1 del reel decía
  `"PRE BLACK FRIDAY 26/11 · BLACK FRIDAY 27/11 / INSCRIPCIÓN POR DM · ELIGE TU PROMOCIÓN"`.
  `ELIGE TU PROMOCIÓN` **no es el copy del brief** (`ELIGE QUE PROMOCIÓN QUIERES.`). El texto
  exacto sí aparece en S2 del reel y en story1, pero convivía con una paráfrasis no autorizada.
  El manual de marca prohíbe inventar texto comercial → **corrección P1** (el parche ya la incluye:
  el pie pasa a dos strings textuales del brief, `PRE BLACK FRIDAY ABYSS: 26/11.` y
  `BLACK FRIDAY ABYSS: 27/11`).

---

## 4. Especificaciones técnicas, zonas seguras y legibilidad — ✅ PASS / ⚠️ WARN (legibilidad)

### 4.1 Especificaciones — **PASS en las 5 piezas** (leídas del bitstream, no del contenedor)
`trace_headers` + decodificación completa + orden de átomos:

| Pieza | Resolución | fps | Perfil@Nivel | Chroma | Bits | Color | faststart | Frames | Err. decode | GOP | Audio |
|---|---|---|---|---|---|---|---|---|---|---|---|
| reel18 | 1080×1920 | 30.0 | **High@4.2** | 4:2:0 | 8 | `yuv420p(tv, bt709, progressive)` | ✅ moov<mdat | 540 = 18.00 s | **0** | 3.6 s | AAC-LC 48 kHz estéreo 189 kb/s |
| reel15 | 1080×1920 | 30.0 | High@4.2 | 4:2:0 | 8 | bt709 completo | ✅ | 450 = 15.00 s | 0 | 3.0 s | AAC-LC 48 kHz estéreo 189 kb/s |
| story1 | 1080×1920 | 30.0 | High@4.2 | 4:2:0 | 8 | bt709 completo | ✅ | 180 = 6.00 s | 0 | 3.0 s | — (sin pista) |
| story2 | 1080×1920 | 30.0 | High@4.2 | 4:2:0 | 8 | bt709 completo | ✅ | 180 = 6.00 s | 0 | 3.0 s | — |
| story3 | 1080×1920 | 30.0 | High@4.2 | 4:2:0 | 8 | bt709 completo | ✅ | 180 = 6.00 s | 0 | 2.0 s | — |

- `aspect_ratio_info_present_flag = 0` → píxel cuadrado, **DAR 9:16 exacto**; sin metadata de
  rotación (`rotate`/`displaymatrix` ausente) → IG no reencuadrará.
- Bitrate 12.99–13.92 Mb/s, átomos `ftyp, moov, free, mdat` (streaming progresivo OK).
- Historias sin pista de audio: decisión de diseño (IG Stories añade música/stickers); si se
  prefieren mudas-con-silencio o con bed, ver P6.

### 4.2 Zonas seguras — **PASS** (0 violaciones)
Bbox de tinta de todo texto esencial dentro de **72–1008 × 250–1670**. Las 5 violaciones de la
primera pasada (12–69 px) siguen corregidas; re-run actual: `SIN VIOLACIONES`.
El display type (Anton ≥ 200 px) desborda a propósito: es gramática de la referencia, no texto esencial.

### 4.3 Legibilidad móvil — ⚠️ **WARN** (2 contrastes bajos + 5 micro-líneas pequeñas)
29 textos medidos sobre los frames entregados (cap height con métricas reales de fuente;
contraste WCAG entre p90 y p25 de luminancia relativa en el bbox):

- Contraste mediano por pieza: reel18 10.21:1 · story1 11.04:1 · story2 7.22:1 · story3 11.17:1 → bien.
- **Incumplimientos de contraste (mínimo 4.5:1):**
  - reel18 `CAMPAÑA NOVIEMBRE 2026 / SAN BERNARDO · CHILE / INK. METAL. SKIN.` → **2.21:1**
  - reel18 `PRE BLACK FRIDAY 26/11 · … / INSCRIPCIÓN POR DM · ELIGE TU PROMOCIÓN` → **3.76:1**
- **Cap height por debajo de 30 px** (criterio del auditor para texto informativo a 1080×1920):
  `ABYSS TATTOO Y PIERCING ♦ SAN BERNARDO` con 18–24 px en reel18 (×2), story1 (23 px), story3 (21 y 24 px).
  Es micro-copy de firma de marca, no información operativa.
- Límite físico medido: esa línea de 38 caracteres necesita **951 px** a 39 pt de cuerpo para
  alcanzar 30 px de altura de mayúscula, y la zona segura dispone de **936 px** → no cabe en una
  sola línea. Opciones en P1b (split en dos líneas) u O2 (aceptar la desviación documentada).

### 4.4 Sala de revisión y entregables — **PASS**
- `GET /` → 302 `/visor.html`; `Range: bytes=0-1023` → **206** con `video/mp4` en las 5 piezas,
  `application/zip` en el paquete y `200 text/html` en `/visor.html` (`serve_preview.py`).
- Entregables presentes: 5 mp4 + 12 pósters + 5 storyboards + `manifest.json` (con `cta`) +
  `qc.json` (**QC PASS ×5**) + `visor.html` + README + `MOTION-TRANSFER.md` +
  `AUDITORIA_2026-11-23.md` + `ENLACES_DESCARGA.md` + `INTEGRIDAD_hashes.txt` + ZIP (31 archivos).

---

## 5. Código, Git/GitHub, integridad Dropbox y PR — ✅ PASS / ⚠️ WARN (peso del repo)

### 5.1 Código
- `src/`: **3.196 LOC en 22 módulos**; `python3 -m compileall src scripts` → OK;
  `src/smoke.py` → OK; docstring de módulo **22/22**; docstring de función **22/97 (~23 %)** → WARN (P4).
- Pipeline limpio y data-driven: `brand.py` (tokens) → `media.py` (placas/grade) →
  `kinetic.py` (composición) → `timeline.py` (escaleta) → `audio.py` → `render.py` →
  `verify.py` (QC) → `serve_preview.py`.
- Defectos encontrados y **corregidos** esta pasada: `scale_piece()` mutaba su entrada (§1.4).
- Defecto encontrado **pendiente**: `bin/ffprobe` es un **symlink a ffmpeg**
  (`imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v9.0.2`), así que `-show_format`/`-show_streams`
  fallan; `verify.py` funciona porque parsea `ffmpeg -i`. Nombre engañoso → P4.

### 5.2 Git / GitHub
- **Nada prohibido trackeado:** 0 coincidencias de `out/masters/`, `__pycache__`, `*.pyc`,
  `*.wav`, `material/`, `bin/`, `*.zip`, `frames_*`, `audit_frames_*` (`.gitignore` ampliado esta pasada).
- Peso: **92.2 MB trackeados en 67 archivos**; `.git` = **404 MB** por los re-commits sucesivos de
  mp4 de 30 MB (cada re-render añade un blob nuevo). → WARN, corrección P3.
- **PR #9: OPEN · MERGEABLE · mergeState CLEAN**, +24.716/−0 en 68 archivos.
  CI: `Build (linux/amd64)` pass 2m42s · `Build (linux/arm64)` pass 1m55s ·
  `Test & build (Node 20)` pass 6m17s · `Test & build (Node 22)` pass 6m9s ·
  `Merge manifest and push` skipping.

### 5.3 Integridad local ↔ Dropbox — **PASS tras corregir 2 documentos desactualizados**
Receta validada contra el servidor: `content_hash = sha256(concat(sha256(bloques de 4 MiB)))`
(verificada con un archivo de 31 MB, uno de 94 MB y varios pequeños; coincide bit a bit).

- **31 archivos comparados: 29 idénticos** en la primera corrida.
- **2 desactualizados en Dropbox** (detectados por esta auditoría y re-subidos):
  `docs/visor.html` (servidor 7.294 B vs local 7.705 B — faltaba el botón de descarga del ZIP) y
  `docs/AUDITORIA_2026-11-23.md` (4.150 B vs 5.371 B — faltaba el anexo post-rebuild).
  Tras re-subir: `86d4d8e386d0bb77…` y `f0bd66c71bb2869c…` = **idénticos** → **31/31**.
- Videos (verificación adicional por descarga + `cmp`): reel18 y story2 **idénticos byte a byte**;
  storyboard story3 descargado y comparado → idéntico.
- `content_hash` de las 5 piezas + ZIP coinciden con los del servidor:
  reel18 `59b06a98…`, reel15 `b1b59b19…`, story1 `a6a8aff7…`, story2 `9cc3f343…`,
  story3 `cc0b2627…`, ZIP `bbfea8d6…`.
- **Originales intactos:** `/ABYSS_BLACK_FRIDAY_ASSETS/material` = 18 archivos con `rev` del
  19–20/11/2026 (sin modificaciones de esta sesión); la referencia del enlace del usuario =
  idéntica a la de `material/` (§1.1).
- ENTREGA: 31 archivos (5 videos + ZIP + 12 pósters + 5 storyboards + 8 docs).

---

## VEREDICTO GLOBAL: ✅ **APROBADO CON OBSERVACIONES**

Las 5 piezas cumplen **todas** las especificaciones duras (1080×1920, 30 fps, H.264 High@4.2,
4:2:0 8 bits, BT.709 completo, faststart, 0 errores de decodificación, audio AAC-LC 48 kHz en los
reels), los copys son verbatim (16/16), la paleta es la de marca (5/5 tokens, ≤2.14 % de tonos
prohibidos), el grano es consistente (σ media 8.4–10.1, CV ≤0.43), las zonas seguras están limpias,
la duración es variable de forma proporcional y verificada (10–30 s), la integridad local↔Dropbox
es 31/31 y el PR #9 está verde y mergeable.

Quedan **observaciones no bloqueantes**, en este orden de prioridad:
**P1** legibilidad (2 contrastes por debajo de WCAG AA) + copy no textual en el pie de S1;
**P2** energía de movimiento 0.30× la referencia; **P3** peso del repo (404 MB de `.git`);
**P4** higiene de código (`bin/ffprobe` falso, docstrings 23 %); **P5** story2 tonos cálidos;
**P6** archivo de referencia no conforme y decisiones de audio/copy opcionales.

---

## CORRECCIONES PRIORIZADAS (comandos exactos)

### P1 — Legibilidad + copy textual (30 min; **parche ya validado**) · severidad ALTA
El parche `research/P1_legibilidad.patch` añade `stroke` a `para_canvas` (misma técnica que
`text_canvas`), pone `outline=2` por defecto en `micro_lines`, pasa a `CREAM` los dos bloques de
bajo contraste, refuerza el bloque superior (size 24→26, track 5→4, outline 3, x 535→522) y
sustituye la paráfrasis del pie de S1 por dos strings **textuales** del brief.

**Validación ya realizada en copia de trabajo** (`/tmp/proj`), midiendo frames renderizados:
contraste `2.21 → 5.78:1` y `3.76 → 6.74:1`; resto de textos 6.65–15.39:1;
`audit_safezones.py` → `SIN VIOLACIONES`; `audit_copies.py` → `RESULT: PASS`.
Nota: subir el cuerpo de esos textos sin bajar el tracking **rompía** la zona segura hasta 177 px
(medido); por eso el parche no toca tamaños salvo el bloque superior, que se re-ubicó 13 px.

```bash
cd /home/user/freellmapi/abyss-black-friday
git apply --check research/P1_legibilidad.patch      # debe pasar sin errores
git apply research/P1_legibilidad.patch
PYTHONPATH=src python3 src/audit_safezones.py        # esperado: SIN VIOLACIONES
PYTHONPATH=src python3 src/audit_copies.py           # esperado: RESULT: PASS
bash scripts/rebuild_audit.sh                        # re-render 5 piezas + bt709 + QC + manifest
PYTHONPATH=src python3 src/audit_legibility.py       # esperado: 0 incumplimientos de contraste
PYTHONPATH=src python3 src/audit_grade_v2.py         # esperado: VEREDICTO 2 PASS/WARN por grano
```
Después: re-subir las 5 piezas + pósters/storyboards regenerados + docs a Dropbox y recalcular
`python3 scripts/dropbox_content_hash.py out/*.mp4 out/*.zip` (o pedírmelo y lo hago yo).

### P1b — Cap height ≥ 30 px en la firma de marca (opcional) · severidad MEDIA
No cabe en una línea dentro de la zona segura (951 px necesarios vs 936 disponibles). Split en dos
líneas, en las 4 apariciones (`src/timeline.py` líneas ~114, ~199, ~243, ~326):

```bash
cd /home/user/freellmapi/abyss-black-friday
python3 - <<'PY'
import pathlib
p = pathlib.Path("src/timeline.py"); s = p.read_text()
s = s.replace('micro_lines(540, 1330, ["ABYSS TATTOO Y PIERCING ♦ SAN BERNARDO"], size=26,',
              'micro_lines(540, 1322, ["ABYSS TATTOO Y PIERCING ♦", "SAN BERNARDO"], size=39,')
s = s.replace('micro_lines(540, 1654, ["ABYSS TATTOO Y PIERCING ♦ SAN BERNARDO"], size=24,',
              'micro_lines(540, 1640, ["ABYSS TATTOO Y PIERCING ♦", "SAN BERNARDO"], size=39,')
p.write_text(s)
PY
PYTHONPATH=src python3 src/audit_safezones.py && PYTHONPATH=src python3 src/audit_legibility.py
```
Alternativa: aceptar la desviación como micro-copy decorativo y documentarla (observación O2).

### P2 — Acercar la energía de movimiento a la referencia (decisión creativa) · severidad MEDIA
Objetivo medible: `flow_norm` medio ≥ 0.0042 (≥0.60× ref) y Pearson ≥ 0.45 en
`src/audit_motion_v2.py`. Palancas, en orden de impacto:

```bash
cd /home/user/freellmapi/abyss-black-friday
python3 - <<'PY'
import pathlib, re
p = pathlib.Path("src/timeline.py"); s = p.read_text()
# (a) push-in más largo: mismo punto final, más recorrido → más flujo sostenido
s = s.replace("cam=[K(0.0, zoom=1.05, cx=0.5, cy=0.50), K(3.0, zoom=1.20, cx=0.52, cy=0.52)]",
              "cam=[K(0.0, zoom=1.02, cx=0.49, cy=0.49), K(3.0, zoom=1.26, cx=0.53, cy=0.53)]")
# (b) entradas de type más rápidas (ease-out más agresivo en menos tiempo)
s = re.sub(r"K\((\d+\.\d+), s=0\.9\d, a=0\.0\), K\((\d+\.\d+), s=0\.9[78], a=1\.0", lambda m:
           f"K({m.group(1)}, s=0.86, a=0.0), K({float(m.group(2))-0.12:.2f}, s=0.99, a=1.0", s)
p.write_text(s)
PY
PYTHONPATH=src python3 src/audit_safezones.py     # (b) desplaza claves: re-verificar zonas
bash scripts/rebuild_audit.sh
PYTHONPATH=src python3 src/audit_motion_v2.py     # comprobar ratios y Pearson
```
Opcional, para calcar la cámara de la referencia: insertar un **zoom-out** de ~1 s en S3
(la referencia hace −10 %/s en t≈4–6 s) y un **corte duro** además de los whips:
`{"kind": "cut", "at": 10.2}` en la lista de transiciones de `reel_scenes()`.
⚠️ Cambia el feel aprobado: requiere tu OK antes de re-entregar.

### P3 — Peso del repo (`.git` 404 MB) · severidad MEDIA
Opción A (recomendada, entrega binaria fuera de git; Dropbox ya es la fuente de verdad):
```bash
cd /home/user/freellmapi
git rm -r --cached abyss-black-friday/out/*.mp4
printf '\n# binarios de entrega: se distribuyen por Dropbox, no por git\nabyss-black-friday/out/*.mp4\n' >> abyss-black-friday/.gitignore
git add abyss-black-friday/.gitignore && git commit -m "chore: entrega de video fuera de git (Dropbox como fuente de verdad)"
git push origin arena/9beaffaa-freellmapi
```
Opción B (mantener los mp4 en git, con LFS):
```bash
cd /home/user/freellmapi
git lfs install && git lfs track "abyss-black-friday/out/*.mp4"
git add .gitattributes && git lfs migrate import --include="abyss-black-friday/out/*.mp4" --everything
```
Opción C (sólo al mergear): `gh pr merge 9 --squash` para no arrastrar los blobs intermedios a `main`.

### P4 — Higiene de código · severidad BAJA
```bash
cd /home/user/freellmapi/abyss-black-friday
rm bin/ffprobe                                   # symlink engañoso a ffmpeg
grep -rn "bin.*ffprobe" src/ scripts/ || echo "✓ nada depende de bin/ffprobe"
python3 - <<'PY'
import pathlib, ast
# docstrings en las funciones públicas de los módulos de pipeline (no de auditoría)
mods = ["brand.py","media.py","kinetic.py","timeline.py","audio.py","render.py","verify.py","serve_preview.py"]
for m in mods:
    p = pathlib.Path("src")/m; t = ast.parse(p.read_text())
    sin = [n.name for n in t.body if isinstance(n, ast.FunctionDef) and not ast.get_docstring(n)]
    print(f"{m}: {len(sin)} funciones sin docstring → {sin[:6]}")
PY
```
Y añadir a CI una corrida de los auditores (`pytest`-style) para que cada re-render se auto-verifique:
```bash
printf '\naudit:\n\tPYTHONPATH=src python3 src/audit_safezones.py\n\tPYTHONPATH=src python3 src/audit_copies.py\n\tPYTHONPATH=src python3 src/audit_legibility.py\n\tPYTHONPATH=src python3 src/verify.py\n' >> Makefile
```

### P5 — story2: 2.05 % amarillo + 2.14 % neón (reflejos cromo de joyería) · severidad BAJA
```bash
cd /home/user/freellmapi/abyss-black-friday
grep -n "duotone\|grade(" src/render.py | head          # localizar la placa de joyería
# bajar el canal cálido de esa placa: sat .80 → .72 y warm .07 → .04, y re-renderizar sólo story2
PYTHONPATH=src python3 src/render.py stories && PYTHONPATH=src python3 src/audit_grade_v2.py
```

### P6 — Archivo de referencia y decisiones opcionales · severidad BAJA
```bash
cd /home/user/freellmapi
# re-mux de la referencia a un MP4 conforme, para archivo y para que cualquier decoder la lea
abyss-black-friday/bin/ffmpeg -hide_banner -loglevel error -y \
  -i dropbox/type_01_pindown.io_1795195281.mp4 -c:v libx264 -preset slow -crf 18 \
  -pix_fmt yuv420p -profile:v high -level 4.2 -colorspace bt709 -color_primaries bt709 \
  -color_trc bt709 -movflags +faststart dropbox/type_01_reference_remux.mp4
abyss-black-friday/bin/ffmpeg -hide_banner -i dropbox/type_01_reference_remux.mp4 2>&1 | grep -i "error\|invalid" || echo "✓ stream conforme"
```
Opcionales: (O3) mostrar la URL IG literal con `?fqnt=` en pantalla en vez del handle;
(O4) añadir bed de audio a las 3 historias (`render_piece(..., audio={...})`), hoy van sin pista.

---

## ÍNDICE DE EVIDENCIA (rutas)
- Informes: `research/AUDITORIA_SENIOR_V2_2026-11-23.md` (éste), `research/AUDITORIA_2026-11-23.md` (v1)
- Datos crudos: `research/audit_motion_v2_report.json`, `research/audit_pushin_report.json`,
  `research/audit_specs_report.json`, `research/audit_grade_v2_report.json`,
  `research/audit_legibility_report.json`, `research/audit_safezones.json`,
  `research/audit_final_checks_report.json`, `research/integrity_check.json`
- Logs: `research/audit_motion_v2.log`, `research/audit_v2_chain.log`, `research/rebuild_audit.log`
- Parche validado: `research/P1_legibilidad.patch` (62 líneas, `git apply --check` OK)
- QC de entrega: `out/qc.json` (PASS ×5) · manifiesto: `out/manifest.json` · hashes: `out/INTEGRIDAD_hashes.txt`
