# Transferencia de motion — referencia `type_01_pindown.io_1795195281.mp4`

Ingeniería inversa fotograma a fotograma (361 frames @ 30 fps, 720×900 4:5)
con `ffmpeg` + `cv2.calcOpticalFlowFarneback` (`src/analyze_reference.py`).
Salidas: `research/motion_type_01.json`, `research/motion_type_01.png`
(curva de energía cinética + cortes), `research/contact_type_01.jpg`,
`research/key_frames.jpg`.

## Qué es la referencia

Póster cinético de exposición («Aleksi Perälä · SPATIAL · Sound installation ·
25 to 27 November 2022»): papel blanco, bloque fotográfico duotono rojo,
tipografía grotesca gigante recortada en los bordes, micro-tipografía de
créditos y un logotipo pequeño. Ningún elemento "de video": todo es retícula
de póster que respira.

## Gramática medida

| Rasgo | Medición / observación | Decisión ABYSS |
|---|---|---|
| Duración | 12.03 s @ 30 fps | reel 18 s + historias 6 s (misma gramática) |
| Cortes duros | 1 corte franco (2.73 s) + cambios de retícula por barrido | cortes en la rejilla; 2 whips (3.00 y 13.20) |
| Whip / flujo óptico | 2.73–3.20 s: barrido oscuro rojizo con blur direccional | `whip_mix()`: salida acelera con blur creciente, entrada frena, streak cobre en el punto medio |
| Push-in continuo | cada plano escala ≈ 1.00 → 1.10–1.15 sin rebote | claves `zoom`/`s` con `easeInOutCubic` por capa (parallax) |
| Barrido de glifos | 4.6–6.4 s: glifos gigantes rotan/barren el cuadro | capa `type` gigante con `blur` y traslado (reel 5.55–6.75 «26/11») |
| Retícula A | foto arriba-izq + type gigante medio/abajo + etiqueta arriba-der + fecha abajo-izq + micro-créditos | plano INTRO del reel |
| Retícula B | type gigante arriba y abajo, foto pequeña al centro con copy encima | plano PRE BLACK FRIDAY |
| Retícula C | cuadro negro + foto centro + type a la derecha | plano CIERRE (panel obsidiana + BLACK/FRIDAY) |
| Sangrado | el type display siempre toca o cruza los bordes | Anton 250–470 px con bleed en los 4 planos |
| Jerarquía | 1 concepto por plano, máx. 2 líneas fuertes | igual |

## Adaptación de dirección de arte

La referencia es papel blanco + rojo. La campaña aprobada de ABYSS
(`A VISTA / BLACK · 02 CORTE`, repo `abysstattoo`, rama
`feat/abyss-black-friday-hyperframes`, SPEC.md) fija: fondo BLACK `#080808` /
OBSIDIAN `#14100D`, tipo CREAM `#EAE3DD` / BONE `#B5A295`, cromo sólo como
reflejo, sin amarillo/rojo retail, sin bursts de oferta. Por tanto la
gramática cinética se conserva **invirtiendo el valor**: obsidiana en vez de
papel, duotono cobre/champán en vez de rojo, y la mecánica aprobada
«BLACK sólido / FRIDAY contorneado» + diagonal −9° como firma del cierre.

## Material real editado (NO TRANSABLE)

Todo plano fotográfico entra etalonado (`media.grade` + `media.duotone`):
contraste 1.02–1.10, hombro de altas luces, saturación 0.80–0.88 y duotono
metálico cálido (sombras obsidiana → medios cobre → altos champán); las
joyas usan duotono cromo neutro. Ningún fotograma usa el material crudo.
Sobre todo el video: grano de película σ≈3.6, viñeta, halación cálida,
flicker ±0.6 % y gate weave sub-píxel (`brand.finish`).
