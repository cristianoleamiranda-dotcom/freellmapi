# ABYSS Tattoo Studio — reel 9:16 (HyperFrames)

Reel vertical de 24 s armado con material real del repo
[`cristianoleamiranda-dotcom/abysstattoo`](https://github.com/cristianoleamiranda-dotcom/abysstattoo)
(fotos de trabajos + clips de proceso) usando las skills de HyperFrames.

## Salida

`renders/abyss-reel.mp4` — 1080×1920 · 30 fps · 24.0 s · H.264 · 720 frames.

## Estructura

```
index.html                     # stage 1080×1920, progreso + viñeta/grano, 6 slots
compositions/
  scene-open.html              #  0.0 –  4.0  hook: video de proceso + logotipo ABYSS
  scene-gallery.html           #  4.0 – 11.0  Lobo → Cristo → Cráneo (Ken Burns)
  scene-process-a.html         # 11.0 – 13.8  "Del trazo a la piel" (detalle)
  scene-process-b.html         # 13.8 – 16.4  "Tu diseño se queda" (pierna)
  scene-gallery-2.html         # 16.4 – 20.0  Lobo samurái → Septum
  scene-cta.html               # 20.0 – 24.0  "Tu idea merece piel" + CTA
assets/clips/                  # 4 clips 1080×1920 recortados de film/*.mp4
assets/photos/                 # 12 fotos 1400×2490 para el Ken Burns
assets/fonts/                  # Cinzel + Montserrat (woff2 locales, sin red)
```

## Identidad usada

Tomada de `abysstattoo/index.html`: `#14100d` tinta, `#eae3dd` crema,
`#9ec4ba` salvia, Cinzel (títulos) + Montserrat (textos).
CTA: `@abyss_tattoo_studio` · `abysstattoo.cl`.

## Comandos

```bash
source ../env.sh          # Chrome + ffmpeg del sandbox
npx hyperframes lint
npx hyperframes check     # 0 errores · 20/20 textos WCAG AA
npx hyperframes snapshot --at 1.4,5.2,9,12.4,16.8,18.6,21.5
npx hyperframes render . --quality looks -o ./renders/abyss-reel.mp4
```

## Notas de edición

- Los MP4 originales venían a 720×1280 / 854×1518 / 960×1706 (verticales);
  se reescalaron y recortaron a 1080×1920.
- El centrado de los media se ancla con `inset: 0` para que GSAP pueda
  animar `scale` sin romper el `translate(-50%,-50%)`.
- Los `.heif` de la entrega original no eran alcanzables desde el sandbox
  (tmpfiles.org fuera del allowlist de red); se usó el material del repo.
