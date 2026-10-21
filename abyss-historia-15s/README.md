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
| `cover_hook.jpg` | Portada del Reel (frame 1.30 s) |
| `poster_cta.jpg` | Historia estática de refuerzo (frame 13.60 s) |
| `storyboard.jpg` | Hoja de contacto de 12 momentos |
| `manifest.json` | Peso y SHA-256 de cada archivo |

## Documentación

- [`research/MOTION-DESIGN.md`](research/MOTION-DESIGN.md) — investigación aplicada: qué se
  está viendo en 2026, los cuatro actos, rejilla musical, personalidad de movimiento,
  reglas de composición y qué se descartó.
- [`research/GUION.md`](research/GUION.md) — escaleta plano por plano, texto exacto y datos
  verificados con sus fuentes.
- [`research/FUENTES.md`](research/FUENTES.md) — de dónde sale cada foto, cada video y cada
  dato de contacto.

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
├── research/         # investigación, guion y fuentes
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
