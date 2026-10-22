# Estudio de IA local · ¿sirve para la historia, la landing y el motion 3D?

Revisión de los cinco enlaces, con datos sacados de los repos (no de los titulares):
qué hace cada uno, qué hardware pide y para cuál de tus tres objetivos sirve de verdad.

**Veredicto en una línea:** sí para **la historia** (Maestro es el único que la hace de
punta a punta), **no para la landing** (0 de 5: eso es código) y **no para 3D real** (dan
apariencia 3D, no geometría que puedas controlar).

---

## 1. Qué es cada cosa

| Enlace | Qué es | Motor / stack | Hardware | Disco | Licencia | Actividad |
|---|---|---|---|---|---|---|
| [Maestro](https://pinokio.co/apps/github-com-blizaine-maestro) | Estudio local de vídeo, imagen y audio + **Director Mode** + editor multi-pista | WanGP (MiniMax H3, LTX-2.5/2.3, Wan, Flux 3, Qwen Image 2.1, MOSS 5B, LongCat) | **NVIDIA only**, 6 GB VRAM mín., 16 GB RAM | **150 GB mín.** / 500 GB recomendado | WanGP **Non-Commercial Evaluation 1.1** | 805 ★, 148 forks, push hoy |
| [MiniMax H3 ComfyUI](https://pinokio.co/apps/github-com-thomasericb-minimax-h3-pinokio) | ComfyUI con H3 nativo + 5 nodos extra y 3 workflows listos | ComfyUI + H3 FL2VA/Ref2VA en INT8/NVFP4 | NVIDIA, cu130; 32 GB VRAM cómodo, menos con offload | **~75 GB** (63 de pesos + ~10 ComfyUI) | repo sin licencia declarada (los pesos H3 tienen la suya) | 18 ★, launcher de una persona |
| [VideoCrafter 2](https://pinokio.co/apps/github-com-cocktailpeanutlabs-videocrafter2) | Text2Video / Image2Video de 2024 | torch 2.5 cu124, checkpoints **512 px** | GPU 8 GB o CPU/Mac (lento) | ~5 GB | sin declarar | 12 ★, último push mar-2025 |
| [FramePack](https://pinokio.co/apps/github-com-pinokiofactory-frame-pack) | Extiende un keyframe en clips largos, frame a frame | lllyasviel/FramePack vía Gradio | **NVIDIA only**, 6 GB VRAM (probado) | ~30 GB | sin declarar | 22 ★, último push may-2026 |
| [arena-hard-auto](https://github.com/lmarena/arena-hard-auto) | **Benchmark de LLM**, no genera imagen ni vídeo | 500 prompts difíciles + 250 de escritura creativa, jueces GPT-4.1 / Gemini-2.5 | CPU + API keys (cuesta dinero) | — | Apache-2.0 | 1082 ★, push jun-2025 |

### Lo que conviene saber de cada uno

**Maestro** es el único que entiende el trabajo completo: le das un audio o un guion y un LLM
local planifica planos, escribe el guion, genera keyframes con consistencia de personaje y
produce los clips; luego los montas en un editor de varias pistas (vídeo, audio, títulos,
transiciones, velocidad, canvas 21:9) y exportas H.264/H.265/AV1. Tiene auto-tune de memoria
por GPU, RIFE 4.26 para suavizar, Face Refiner, upscaling y TTS con clonación de voz.
Contras duros: **solo NVIDIA en Windows/Linux** (AMD y macOS no soportados, texto literal del
README), **150 GB mínimo** de disco, la primera instalación descarga **50–100 GB** (el modelo
de vídeo por defecto pesa ~18 GB) y la licencia es **no comercial para el software**, aunque el
propio LICENSE aclara que los outputs sí pueden usarse comercialmente con aviso.
Rendimiento declarado: 24 GB → 1–3 min por clip; 12–16 GB → 4–10 min; 6–8 GB → funciona con
offload fuerte y clips cortos (el tramo probado 8 GB / 32 GB arranca en 10,1 s a 720p).

**MiniMax H3 ComfyUI** es la vía cruda a H3: vídeo **con audio estéreo nativo a 32 kHz**,
4–15 s, 24 fps, de 21:9 a 9:16, diálogo en 11 idiomas. Los pesos están podados y cuantizados
(63 GB en vez de ~290 GB), lo que es un acierto, pero sigues necesitando ComfyUI y montar tú
el flujo. Aporta algo que Maestro también tiene (audio), y pierde en comodidad: tres workflows,
cero narrativa automática.

**VideoCrafter 2** es de enero de 2024 y se nota: los checkpoints son de **512 px**
(`base_512_v2`, `i2v_512_v1`) y los clips son de segundos. Hoy no compite con LTX-2.5 ni H3.
Instalarlo solo tiene sentido como curiosidad o por comparar.

**FramePack** resuelve un problema muy concreto: convertir una imagen en un clip largo y
coherente. No tiene audio, no edita y en 6–8 GB tarda minutos por clip. Como pieza de un
pipeline vale; como motor de una historia, no.

**arena-hard-auto** no tiene nada que ver con imagen o vídeo: mide qué LLM responde mejor a
prompts difíciles. Su utilidad aquí es indirecta —elegir con datos qué modelo escribe el guion
o el copy de la landing— y tiene coste real en llamadas a GPT-4.1/Gemini-2.5.

---

## 2. Semáforo por objetivo

| Objetivo | Maestro | H3 ComfyUI | VideoCrafter 2 | FramePack | arena-hard |
|---|---|---|---|---|---|
| **Historia** (guion → planos → clips → montaje → export) | ✅ completo | ⚠️ clips con audio, montas tú | ❌ 512 px, obsoleto | ⚠️ solo image→video | ❌ |
| **Landing page** | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Motion graphics 3D real** (malla, cámara, tipografía extruida) | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Audio / diálogo / voz** | ✅ TTS, clonación, lipsync | ✅ estéreo nativo 32 kHz | ❌ | ❌ | ❌ |
| **Imagen fija (keyframes, stills)** | ✅ Flux 3, Qwen 2.1, MOSS 5B | ❌ | ❌ | ❌ | ❌ |

Traducción: **1 de 5 sirve para la historia, 0 de 5 sirve para la landing o para 3D.**

---

## 3. El malentendido del «3D»

Hay dos cosas distintas y conviene no mezclarlas:

1. **Apariencia 3D** — que es lo que da la IA de vídeo: movimientos de cámara, parallax, luz
   volumétrica, profundidad de campo. Sale bien y es barato. No controlas la escena: si el
   plano 3 se va hacia la izquierda, no puedes pedirle al modelo que vuelva, ni reencuadrar
   después, ni cambiar el ángulo de la misma geometría.
2. **3D de verdad** — geometría, cámara y luces con parámetros: Three.js / React Three Fiber +
   GSAP/Lenis, Spline para prototipar rápido, Blender para modelar y exportar GLB. Ahí sí
   cambias el ángulo y la escena responde.

Ninguna de las cinco herramientas hace lo segundo. Si la landing necesita un hero 3D
interactivo, es código y assets, no generación de vídeo.

Y para un estudio de tatuajes, ojo: el 3D interactivo suele ser la respuesta equivocada —
pesa, tarda y compite con el trabajo real (las fotos y el vídeo del estudio). Lo que mejor
funciona es **vídeo vertical + tipografía cinética + scroll**, que es exactamente lo que ya
tienes montado en `abyss-historia-15s/`.

---

## 4. Recomendación concreta

**Si tu GPU es NVIDIA de 12 GB o más y tienes 150 GB libres:** instala **Maestro** y olvídate
del resto para este trabajo. Flujo:

1. Fotos reales del estudio + el guion de 15 s → referencias en Maestro (Studio → References).
2. Director Mode (o Studio manual si quieres control plano a plano) para generar los clips.
3. Editor: montaje en 9:16, títulos, música; export H.264.
4. El mp4 entra en la landing como pieza central y en el visor existente como calidad nueva.

**Si tu GPU es de 6–8 GB:** mismo camino, pero clips de ~10 s, H3 Pruned o LTX-2.5 Distilled,
y nada de 1080p hasta tener los modelos cacheados.

**Si no tienes NVIDIA:** ninguna de las cinco. Opciones honestas: (a) API en la nube para los
clips que no puedas generar, (b) seguir con el pipeline offline que ya existe
(`abyss-historia-15s/src/`, Pillow + OpenCV, reproducible y sin GPU). No pierdas una tarde
instalando VideoCrafter2 para descubrir que da 512 px.

**Qué no instalar para este proyecto:** VideoCrafter 2 (obsoleto) y FramePack (solo tiene
sentido si un plano concreto necesita prolongarse). **arena-hard-auto** solo si vas a comparar
LLMs para el guion; para eso no hace falta instalarlo, su leaderboard público ya responde.

---

## 5. Encaje con lo que ya está en el repo

| Pieza existente | Qué aporta | Qué falta |
|---|---|---|
| `abyss-historia-15s/` | Render offline 900 frames, rejilla 100 BPM, `brand.py` + `timeline.py`, visor con seek y selector de calidad | Los planos son foto + cámara virtual; Maestro añadiría movimiento real |
| `skills-hub/library/` | `motion-design`, `sender-motion-scroll`, `scroll-craft`, 30 skills de PixiJS, `text-to-lottie`, `sender-qa-verify` | **Ninguna skill de Three.js/Spline**: si la landing lleva 3D, hay que crearla |
| `fooocusplus-pinokio/` | Imágenes fijas locales (SDXL, Flux, Z-Image) + preflight de hardware | Maestro también genera imagen (Flux 3, Qwen 2.1): se solapan, elige **una** base |
| `abyss-historia-15s/preview/` | Visor autónomo y servidor con Range | Solo sirve mp4/H.264; admite el export de Maestro sin cambios |

Nota de solape: FooocusPlus y Maestro cubren la misma necesidad de imagen. FooocusPlus es más
liviano en disco y corre en más hardware; Maestro gana si ya vas a instalar el pipeline de
vídeo, porque comparte modelos y evita duplicar GB.

---

## 6. Coste real en disco y tiempo

| Instalación | Disco | Primera vez |
|---|---|---|
| Maestro (mínimo funcional) | 150 GB | 10–20 min instalar + 50–100 GB de descargas |
| + colección completa de modelos | 500 GB | días de descarga |
| MiniMax H3 ComfyUI | ~75 GB | 63 GB de pesos |
| FramePack | ~30 GB | pesos al primer uso |
| VideoCrafter 2 | ~5 GB | minutos |

Tiempos de generación declarados por Maestro: 24 GB → 1–3 min por clip; 12–16 GB → 4–10 min;
6–8 GB → varios minutos por clip corto. Multiplica por el número de planos de la historia: una
pieza de 15 s con 6 planos en una GPU de 8 GB son fácilmente 30–60 min de generación, más
reintentos.

Antes de instalar nada, corre el chequeo:

```bash
bash scripts/check-video-stack.sh          # Linux / macOS
powershell -ExecutionPolicy Bypass -File scripts\check-video-stack.ps1   # Windows
```

Dice, con tu hardware delante, cuál de las cinco es viable, cuál es «justa» y cuál no deberías
ni intentar. Reutiliza los umbrales de §1. Para la parte de imagen (FooocusPlus) sigue valiendo
`fooocusplus-pinokio/scripts/preflight.sh`.

---

## 7. Lo que no está verificado

- **Velocidad real en tu GPU**: los rangos salen del README de Maestro; no los he medido.
- **Calidad subjetiva** de los modelos: no puedo generarla aquí (ver §8).
- **Licencias de los pesos de terceros**: Qwen Image 2.1 es licencia de investigación/evaluación
  (uso comercial requiere licencia aparte, según el propio README de Maestro), los pesos de H3
  son de MiniMax y los de Flux tienen sus términos. Si el material va a un cliente, revísalo
  antes de publicar.
- **Maestro es «Non-Commercial Evaluation» como software**, con outputs comercializables según
  su LICENSE (exige aviso). Lee `app/LICENSE.txt` de tu instalación antes de facturar un vídeo.
- El star count y las fechas son de la API de GitHub en el momento de esta revisión.

---

## 8. Estado en este entorno

No puedo instalar ni probar ninguno: este sandbox tiene **sin GPU, 3 GB de RAM, 2 vCPU, 19 GB
libres** y la red solo permite GitHub/npm/PyPI (`huggingface.co` bloqueado, y Maestro y H3
descargan de ahí). Se entrega la evaluación verificada contra los repos y el chequeo para tu
máquina, no una instalación a medias.

---

## 9. Siguiente paso

Dime qué tienes (GPU, VRAM, disco libre) y elige una:

1. **Historia con Maestro** — escribo el shot list y los prompts por plano, con las referencias
   reales del estudio, listos para pegar en Director Mode.
2. **Landing con la pieza de 15 s** — esqueleto de landing (Astro/Next) con el mp4, tipografía
   cinética y scroll, usando las skills de `skills-hub`.
3. **3D de verdad** — añado la skill de Three.js/Spline que falta en `skills-hub` y armo un
   hero 3D con GLB propio en vez de vídeo generado.
