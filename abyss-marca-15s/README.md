# Abyss · pieza de marca 9:16 (15 s y 18 s)

Pieza de marca para **Abyss Tattoo Studio** hecha con el material real del estudio:
el emblema como referencia visual, planos de tatuador, proceso, trabajos, piercing y
local. Render offline, reproducible, sin material de terceros.

| | |
|---|---|
| Formato | 1080 × 1920 (9:16), 60 fps, H.264 High 4.2, BT.709, AAC 48 kHz |
| Duración | **15.00 s** (900 frames) y **18.00 s** (1080 frames) |
| Rejilla | 100 BPM · 0.6 s por negra · 25 negras |
| Tipografía | Cinzel 700/800 + Montserrat 500/600 |
| Paleta | Obsidiana `#14100D` · Hueso `#B5A295` · Crema `#EAE3DD` · Salvia `#556C65` · Teal `#9EC4BA` |
| Material | repo [`abysstattoo`](https://github.com/cristianoleamiranda-dotcom/abysstattoo) (23 archivos, 14.2 MB) |

## Dos versiones

| | 15 s | 18 s |
|---|---|---|
| Rejilla | 25 negras | 30 negras |
| Bloques | 12 planos | 13 planos |
| Proceso | 3 planos (3.0–5.4) | **4 planos** (3.0–7.2), +1.8 s de sesión real |
| Lugar | 0.9 s de fachada | 1.2 s de fachada |
| Cierre | 3.6 s | 4.8 s |
| Uso | Reels/TikTok (límite corto) | YouTube Shorts, landing, presentación al cliente, descarga |

La versión de 18 s no es la de 15 estirada: añade material nuevo
(`film/proceso_pierna.mp4`, el tatuador trabajando) con su propio texto
(**TRAZO A TRAZO** / SESIÓN EN CURSO) y da más aire al emblema y al CTA.

```bash
bash scripts/build.sh --no-fetch        # 15 s
bash scripts/build.sh --no-fetch --long # 18 s (timeline_largo.py)
bash scripts/kit.sh                     # dist/abyss-marca-15s-kit.zip
bash scripts/kit.sh --long              # dist/abyss-marca-18s-kit.zip
```

## Escaleta (15 s)

| # | In–Out | Material | Cámara | Texto |
|---|---|---|---|---|
| S1 | 0.00–1.80 | `film/hero_film.mp4` 0.12 s · 0.55× | push-in 1.06 → 1.19 | **HECHO** / **A MANO** |
| S2 | 1.80–3.00 | `film/hero_film.mp4` 2.45 s · 0.60× | pull-back 1.16 → 1.03 | PUNTO POR PUNTO |
| S3 | 3.00–4.20 | `film/proceso_detalle.mp4` 1.20 s | push-in 1.10 → 1.02 | — |
| S4 | 4.20–5.40 | `film/proceso_filmacion.mp4` 2.60 s | push-in 1.04 → 1.15 | — |
| S5 | 5.40–6.30 | `trabajos/trabajo_hombro_real.jpg` | pull-back 1.20 → 1.07 | **REALISMO** / BLACK & GREY |
| S6 | 6.30–7.20 | `trabajos/trabajo_cristo_manga.jpg` | pan vertical 1.14 → 1.04 | — |
| S7 | 7.20–8.10 | `trabajos/trabajo_lobo_rugido.jpg` | crash zoom 1.26 → 1.08 | — |
| S8 | 8.10–9.00 | `trabajos/septum.jpg` | push-in 1.10 → 1.22 | — |
| S9 | 9.00–9.90 | `estudio/fachada.jpg` (plate apaisado) | paneo real 0.22 → 0.46 | **SAN BERNARDO** / JOSÉ JOAQUÍN PÉREZ 528 |
| S10 | 9.90–10.80 | `estudio/vitrina.jpg` | push-in 1.02 → 1.14 | — |
| S11 | 10.80–11.40 | `film/loop_film.mp4` 3.70 s | push-in 1.12 → 1.22 | — |
| S12 | 11.40–15.00 | `reel_plates/emblema_abyss_alpha.png` | settle 0.86 → 1.00, −7° → 0° | **AGENDA TU HORA** · WhatsApp · @abyss_tattoo_studio |

Los cortes caen en negras: 1.8 · 3.0 · 4.2 · 5.4 · 6.3 · 7.2 · 8.1 · 9.0 · 9.9 · 10.8 · 11.4.

### Escaleta (18 s)

Cambios respecto a la de 15 s; el resto de planos y textos es idéntico.

| # | In–Out | Material | Cámara | Texto |
|---|---|---|---|---|
| S5 | 5.40–7.20 | `film/proceso_pierna.mp4` 0.90 s · 0.78× | push-in 1.05 → 1.16 | **TRAZO A TRAZO** / SESIÓN EN CURSO |
| S6–S9 | 7.20–10.80 | hombro, manga, lobo, septum | igual que 15 s | REALISMO / BLACK & GREY |
| S10 | 10.80–12.00 | fachada (paneo más largo) | 0.20 → 0.50 | SAN BERNARDO / JOSÉ JOAQUÍN PÉREZ 528 |
| S11–S12 | 12.00–13.20 | vitrina, mural | igual que 15 s | — |
| S13 | 13.20–18.00 | emblema | settle + brillo a 14.45 | AGENDA TU HORA (desde 14.20) |

Cortes: 1.8 · 3.0 · 4.2 · 5.4 · 7.2 · 8.1 · 9.0 · 9.9 · 10.8 · 12.0 · 12.6 · 13.2.

## Decisiones de montaje

- **El emblema manda.** No es sólo el cierre: el revelado (barrido angular de 360° desde
  las 12, anillo que se traza, barrido especular a 12.55 s) es el momento más cuidado y el
  poster de la campaña sale de ahí.
- **Arco en cinco actos**: manos → proceso → obra → lugar → marca. Un concepto por bloque,
  dos líneas como máximo, un solo eje de texto a x = 108.
- **Cámara virtual sub-píxel**: cada plano se muestrea del original con zoom, centro y
  rotación interpolados con `easeInOutCubic`; nada de rebotes ni overshoot.
- **La fachada se panea, no se recorta**: se carga a altura fija (`load_plate_height`) para
  conservar todo el ancho y recorrer el mural con la cámara en vez de encajonar un 9:16
  sobre una foto apaisada.
- **Etalonaje único**: LUT propia (contraste 1.10, sombras salvia, altas cálidas),
  saturación 0.86, viñeta y banco de grano. Cada plano sólo corrige exposición.
- **Banda de lectura automática**: se oscurece únicamente la franja que ocupan los textos
  visibles, no todo el cuadro.
- **Cero datos sin fuente**: sólo dirección, WhatsApp e Instagram (verificados en
  `abyss-historia-15s/research/FUENTES.md`). Sin años, precios ni promociones.
- **Audio sintetizado**: kick en negra con ducking del pad, hats a contratiempo, riser de
  10.8 a 11.4 y sub-boom + campana en el revelado del emblema. Sin samples de terceros.

## Entregables

Kit descargable (ZIP con LEEME y verificación de hashes):
`dist/abyss-marca-15s-kit.zip` (46 MB) y `dist/abyss-marca-18s-kit.zip` (53 MB).

En `out/`:

| Archivo | Uso |
|---|---|
| `abyss_marca_15s_1080x1920_60fps.mp4` | máster 15 s (900 frames, 25 MB) |
| `abyss_marca_15s_1080x1920_30fps.mp4` | derivada 15 s a 30 fps (15 MB) |
| `abyss_marca_15s_720x1280_preview.mp4` | previa 15 s (2.5 MB) |
| `abyss_marca_15s_visor.html` | visor autónomo 15 s |
| `abyss_marca_18s_1080x1920_60fps.mp4` | **máster 18 s (1080 frames, 30 MB)** |
| `abyss_marca_18s_1080x1920_30fps.mp4` | derivada 18 s a 30 fps (17.5 MB) |
| `abyss_marca_18s_720x1280_preview.mp4` | previa 18 s (2.9 MB) |
| `abyss_marca_18s_visor.html` | visor autónomo 18 s |
| `cover_emblema.jpg` · `cover_emblema_18s.jpg` | portada del Reel (frame 1.25 s) |
| `poster_cta.jpg` · `poster_cta_18s.jpg` | pieza estática de refuerzo |
| `storyboard.jpg` · `storyboard_18s.jpg` | hoja de contacto |
| `manifest.json` · `manifest_18s.json` | peso y SHA-256 de cada archivo |

## QA de los entregables

`python3 src/verify.py` audita los archivos publicados (no los frames en memoria):

- duración 15.00 s, 1080×1920 / 720×1280, 60 / 30 fps, pista de audio presente;
- pesos y SHA-256 contra `out/manifest.json`;
- **comparación del máster decodificado contra un render fresco** del mismo instante
  (diferencia media y desfase por canal), que detecta canales invertidos o LUT aplicada dos veces;
- **idempotencia**: renderizar un `t` aislado debe dar el mismo frame que renderizarlo después
  de una secuencia.

Dos errores reales que esta QA encontró y que ya están corregidos:

1. **Rojo y azul intercambiados en el MP4.** Las capas se componen en BGR (OpenCV) y se
   escribían tal cual en el pipe RGB de ffmpeg. El storyboard, generado en memoria, se veía
   bien; el archivo publicado, no. Fix: `cv2.cvtColor(frame, COLOR_BGR2RGB)` antes de escribir.
2. **Textos que se apagaban para siempre.** `paste_text` aplicaba el fade mutando el bitmap de
   `text_bitmap`, que está en `lru_cache`: el primer frame atenuaba el texto del resto del video.
   Sólo se notaba en el render secuencial (en frames sueltos salía perfecto). Fix: copiar antes
   de tocar el alfa, más el test de idempotencia para que no vuelva.

## Cómo se reconstruye

```bash
python3 -m pip install --user --break-system-packages opencv-python-headless numpy pillow imageio-ffmpeg
python3 src/fetch_material.py   # material/ desde el repo abysstattoo (por SHA, vía API de blobs)
python3 src/audio.py            # render/soundtrack.wav (sintetizado, 100 BPM)
python3 src/render.py           # 900 frames + mux + derivadas + piezas
python3 src/standalone.py       # out/abyss_marca_15s_visor.html
python3 src/manifest.py         # out/manifest.json (pesos + SHA-256)
python3 src/verify.py           # QA de los mp4 publicados
```

Para la versión larga, las mismas tres órdenes con prefijo:

```bash
export ABYSS_TIMELINE=timeline_largo ABYSS_DURATION=18 ABYSS_SLUG=abyss_marca_18s
python3 src/audio.py && python3 src/render.py && python3 src/standalone.py
python3 src/manifest.py && python3 src/verify.py
```

O todo en un paso: `bash scripts/build.sh` (sin `--no-fetch` vuelve a bajar el material).

`material/` no se versiona (14 MB de binarios que viven en `abysstattoo`); se reconstruye
con `fetch_material.py`, que fija los archivos por ruta y baja el blob exacto.

Para cambiar el montaje basta `src/timeline.py`: cada plano declara material, entrada y
salida, keyframes de cámara y textos. `render.py` no sabe de contenido.

## Encaje con las skills del repo

| Skill | Qué se aplicó |
|---|---|
| `abyss-video-image-studio` | auditoría del material antes de montar, masterización H.264 + AAC 48 kHz, zonas seguras 9:16 |
| `motion-design` | easing custom (`easeOutCubic`/`easeOutExpo`), stagger de 0.18 s entre líneas, 0 % overshoot |
| `sender-motion-scroll` | rejilla rítmica y criterio de «un plano, una idea» llevado a vídeo vertical |
| `sender-qa-verify` | `manifest.json` con SHA-256 + storyboard de control para revisar el corte |
| `text-to-lottie` (criterio) | entrada de texto por wipe/scale contenida, sin física decorativa |

## Qué falta para publicar

- Revisar el corte con el estudio (nombres, tono, si quieren mostrar más piercing).
- Decidir el CTA final: ahora WhatsApp, alternativa DM de Instagram.
- Etiquetar `@abyss_tattoo_studio` si se publica como colaboración.
- Versión de 18 s: ya está hecha (`timeline_largo.py`). Si se quiere una de 21 s, la rejilla
  llega a 35 negras y el material da para otros dos planos de proceso de 1.5 s.
- Variante 4:5 (1080 × 1350) para feed: el máster se reencuadra sin perder bloques de texto
  porque todo el texto vive dentro de x = 108…972.

## Sobre el pedido original

Pediste un vídeo «con la técnica» de IA local (Maestro, H3, FramePack, VideoCrafter2). Ninguna
de esas cinco apps corre aquí: sin GPU, 3 GB de RAM y `huggingface.co` bloqueado (ver
`estudio-ia-local/README.md`). Se resolvió con el pipeline determinista que ya existía en el
repo, que además es el adecuado para una pieza de marca: cámara, rejilla y tipografía bajo
control exacto, sin depender de lo que invente un modelo. Las cinco apps siguen sirviendo para
*otra* cosa: clips generados con movimiento real, cuando haya una NVIDIA de 12 GB o más.
