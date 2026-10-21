# Abyss Tattoo Studio · historia de 15 s

Historia vertical de **15.00 s** para Reels, TikTok y Meta Ads, montada desde el material
real del estudio con una línea de tiempo propia. No reutiliza el reel que ya existía en el
repo: otro guion, otros planos, otro audio.

| | |
|---|---|
| Formato | 1080 × 1920 (9:16), 60 fps, H.264 High 4.2, BT.709, AAC 48 kHz |
| Duración | 15.00 s exactos (900 frames) |
| Rejilla | 100 BPM · 0.6 s por negra · 25 negras |
| Tipografía | Cinzel 700/800 (display) + Montserrat 500/600/700 (metadatos) |
| Paleta | Obsidiana `#14100D` · Hueso `#B5A295` · Crema `#EAE3DD` · Salvia `#556C65` · Teal `#9EC4BA` |

## Entregables (`out/`)

| Archivo | Uso |
|---|---|
| `abyss_historia_15s_1080x1920_60fps.mp4` | Máster para publicar (Reels, TikTok, Meta Ads) |
| `abyss_historia_15s_1080x1920_30fps.mp4` | Versión liviana para web y WhatsApp |
| `abyss_historia_15s_720x1280_preview.mp4` | Previa de 3 MB: abre rápido en cualquier navegador |
| `abyss_historia_15s_visor.html` | Visor autónomo: el video de 3 MB va dentro del HTML |
| `cover_hook.jpg` | Portada del Reel (frame 1.30 s) |
| `poster_cta.jpg` | Historia estática de refuerzo (frame 13.60 s) |
| `storyboard.jpg` | Hoja de contacto de 12 momentos |
| `manifest.json` | Peso y SHA-256 de cada archivo |

## Verlo en el navegador

Hay tres caminos, del más simple al más completo.

**1. Un solo archivo, sin servidor.** Descarga `visor/index.html` (5 MB) y ábrelo con doble
clic. El video de 720×1280 va dentro del HTML en base64, así que funciona sin internet y se
puede enviar por correo o WhatsApp. Es la vía recomendada para mostrar la pieza.

```bash
python3 src/standalone.py     # regenera out/abyss_historia_15s_visor.html
```

**2. Servidor local** (viewport real, todas las calidades, descargas):

```bash
python3 preview/serve.py --port 8000
# http://localhost:8000/preview/
```

El visor incluye reproductor con seek, escaleta clicable, selector de calidad (previa de
3 MB / 1080p 30 / 1080p 60) y storyboard. El servidor soporta `Range` (necesario para el seek
en mp4), sirve las tipografías en local y tolera cortes de conexión a mitad de descarga.
También responde `/health` para comprobar que está vivo.

**3. GitHub Pages** (enlace público propio, un ajuste manual):

1. En el repo, **Settings → Pages**.
2. *Source*: **Deploy from a branch**; *Branch*: `arena/a95742be-freellmapi`, carpeta **`/`**.
3. En 1–2 minutos queda en `https://cristianoleamiranda-dotcom.github.io/freellmapi/abyss-historia-15s/`.

La portada `index.html` de esta carpeta redirige a `preview/`, así que la URL de la carpeta
ya funciona sola.

**4. Kit para descargar.** `scripts/publicar.sh` arma `dist/abyss-historia-15s-kit.zip` (visor
+ los tres mp4 + portadas + README) y, si el entorno tiene acceso a `uploads.github.com`,
intenta publicarlo como release. En este sandbox esa subida está bloqueada, por eso el zip
se entrega como archivo local.

## Documentación

- [`research/MOTION-DESIGN.md`](research/MOTION-DESIGN.md) — investigación aplicada: qué se
  está viendo en 2026, los cuatro actos, rejilla musical, personalidad de movimiento,
  reglas de composición y qué se descartó.
- [`research/GUION.md`](research/GUION.md) — escaleta plano por plano, texto exacto y datos
  verificados con sus fuentes.
- [`research/FUENTES.md`](research/FUENTES.md) — de dónde sale cada foto, cada video y cada
  dato de contacto.
- [`research/REPOS-MOTION-GRAPHICS.md`](research/REPOS-MOTION-GRAPHICS.md) — repositorios de
  motion graphics verificados (estrellas, licencia, último commit) y cuál conviene en cada caso.
- [`research/MINIMAX-DESIGN.md`](research/MINIMAX-DESIGN.md) — qué existe realmente del
  «repositorio de MiniMax Design» y qué es oficial.

## Del research a la pieza

Cada hallazgo terminó en un parámetro concreto del render. Esta tabla es la trazabilidad.

| Hallazgo | Dónde está en la pieza |
|---|---|
| Cámara whip-pan continua 57 % / cortes en negras 43 % (tendencias 2026) | Cortes secos en 1.8 · 3.6 · 5.4 · 7.2 s, justo en negras de 100 BPM; el mosaico final acelera con micro-cortes de 0.45 s en 10.05 · 10.5 · 10.95 s |
| Tipografía cinética de palabra única controla la velocidad de lectura | Un concepto por bloque y dos líneas como máximo (`ES UNA FIRMA` + `REALISMO BLACK & GREY`) |
| «Diseñar para el primer segundo» | P1 abre con el macro de aguja (0–1.8 s); la primera línea entra en 0.12 s y la segunda en 0.34 s |
| Texto +30–40 % para vertical | Cinzel 800 a 76–104 px en los titulares y Montserrat 500/600 a 26–34 px en los apoyos, con tracking de 1.5 a 6.0 |
| Grano analógico sobre la hiperrealidad | Banco de grano propio en `media.grain_bank` + viñeta por plano |
| Easing de `anime.js` / GSAP (curvas custom en vez de `ease-in-out`) | `brand.ease_out_expo` y `ease_in_out_cubic` en todas las entradas de texto |
| Stagger de 1–3 frames de `mojs` / Motion | Las dos líneas de cada bloque entran escalonadas (≈0.18 s de diferencia), nunca a la vez |
| Rejilla de 0.6 s de Motion Canvas aplicada a edición | Timeline completa montada en múltiplos de 0.6 s; 25 negras exactas |

**MiniMax Design** no se usó para renderizar: es un producto propietario (video, voz y música)
y el único repo oficial es un plugin de ComfyUI con licencia GPL-3, sin modelos incluidos. No
aportaba nada a una pieza de 15 s renderizada con Pillow y OpenCV. Lo que sí se tomó de su
ecosistema fue el criterio de `MiniMax-AI/skills` (`motion-recipes.md`): movimientos cortos,
una idea por plano, sin rebotes ni física decorativa.

Los repos de motion graphics se usaron como **criterio**, no como dependencia: la pieza se
renderizó offline para controlar cada frame. `Remotion` queda como la vía natural si más
adelante quieres variantes 4:5 y 1:1 desde el mismo código.

## Cómo se reconstruye

```bash
python3 -m pip install --user --break-system-packages opencv-python-headless numpy pillow imageio-ffmpeg
python3 src/audio.py      # render/soundtrack.wav (sintetizado, sin material de terceros)
python3 src/render.py     # 900 frames + mux + derivadas + piezas
```

Sin After Effects, sin Premiere y sin assets de pago: todo el render es reproducible
desde los archivos del repo.

## Estructura

```
abyss-historia-15s/
├── src/
│   ├── brand.py      # paleta, tipografías, easing, texto con tracking y shimmer
│   ├── timeline.py   # LA LÍNEA DE TIEMPO: planos, cámara, texto, eventos de audio
│   ├── media.py      # lectura de material, cámara virtual afín, etalonaje, grano
│   ├── audio.py      # banda sonora sintetizada a 100 BPM
│   └── render.py     # composición frame a frame + mux + piezas
├── preview/          # visor local con soporte de Range + tipografías
├── research/         # investigación, guion, fuentes y repos
├── work/             # contact sheets y previews de control
└── out/              # entregables
```

Para cambiar el montaje se edita `src/timeline.py`: cada plano declara material, entrada y
salida, keyframes de cámara y textos. `render.py` no sabe de contenido.

## Decisiones de montaje

1. **Hook sin promesas**: «ESTO NO ES UN TATUAJE / ES UNA FIRMA». Abre con un macro real de
   aguja en cámara lenta, no con un logo.
2. **El scroll es enemigo**: cada corte cae en la rejilla de 100 BPM; no hay planos
   «a ojo».
3. **Cero datos inventados**: solo dirección, WhatsApp e Instagram, los tres verificados.
   Sin años de experiencia, sin número de artistas, sin precios, sin promociones.
4. **Premium, no circense**: easing `easeOutCubic`, 0 % de overshoot, grano fino y viñeta.
   Los rebotes de plantilla se descartaron a propósito.
5. **Legibilidad primero**: banda de degradado bajo cada bloque de texto y eje único
   `x = 120` para todo lo alineado a la izquierda.

## Audio

Banda sonora sintetizada (numpy): kick en cada negra con ducking del pad, hats en
contratiempo, riser de 9.6 a 11.4 s, sub-boom y campana en el cierre. Sin samples de
terceros, así que no hay licencia de música que resolver.

## Lo que falta para publicar

- [ ] Revisar el corte con el estudio (nombres, tono, si quieren mostrar más piercing).
- [ ] Decidir si el CTA es WhatsApp o DM de Instagram (ahora dice WhatsApp).
- [ ] Si se publica como colaboración, etiquetar `@abyss_tattoo_studio`.
- [ ] Considerar una variante 4:5 para el feed (`1080×1350`); el máster se recorta sin
      perder los bloques de texto.
