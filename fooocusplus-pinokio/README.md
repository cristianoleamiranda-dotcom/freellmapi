# FooocusPlus con Pinokio · guía de instalación

Runbook para instalar y usar **FooocusPlus** (fork independiente de Fooocus, vía SimpleSDXL2)
con el launcher de **Pinokio**, a partir del post
<https://pinokio.co/posts/01m5fw6vp3wfpysv4ryf2jhq12>.

FooocusPlus es generación de imágenes pura: sin nodos, sin grafos. Se instala, se elige un
preset y se escribe el prompt. Los modelos se descargan solos la primera vez que se usan.

---

## 1. Qué se instala exactamente

Dos repos, y conviene no confundirlos:

| Pieza | Repo | Qué es |
|---|---|---|
| Launcher | [`6Morpheus6/FooocusPlus`](https://github.com/6Morpheus6/FooocusPlus) (12 archivos, JS) | Script de Pinokio: instala, arranca, actualiza, borra y elige idioma |
| Aplicación | [`DavidDragonsage/FooocusPlus`](https://github.com/DavidDragonsage/FooocusPlus) (GPL-3.0, ~131 ★) | El programa real (Python + Gradio + Comfy embebido) |

El launcher hace esto, en orden (`install.js`):

1. `git clone https://github.com/DavidDragonsage/FooocusPlus app` (la app vive en `app/`).
2. Instala `requirements_{windows,linux,macos}.txt` y luego `requirements_versions.txt` con `uv`.
3. Ejecuta `torch.js`: elige la rueda de PyTorch según GPU detectada
   (CUDA 12.8 para GTX 10/16, RTX 20, RTX 30/40; CUDA 13.0 para sm_120/121 — RTX 50/60 Pro,
   DGX Spark; ROCm nightlies para AMD; `--gpu-type none` en macOS).
4. Crea `UserDir/models/{checkpoints,clip_vision,prompt_expansion}` y comparte el resto de
   carpetas de modelos con otras apps de Pinokio (ver §5).
5. Descarga lo mínimo para arrancar: un checkpoint SDXL (`elsewhereXL_v10`), el VAE
   `ae.safetensors`, `openai/clip-vit-large-patch14` y `LykosAI/GPT-Prompt-Expansion-Fooocus-v2`.
6. Pregunta el idioma y lo guarda en `language.json`.

Al arrancar (`start.js`) ejecuta
`python entry_with_update.py --gpu-type none <flags> --language <código>` en `app/`, escucha en
**http://127.0.0.1:7860** y espera la señal `Comfy loading complete!` para considerarse listo.
Si no hay GPU acelerada, el menú añade `--always-cpu`, y `--disable-in-browser` evita que la app
intente abrir un navegador fuera del de Pinokio.

> Detalle que sorprende: `entry_with_update.py` hace `git fetch` + fast-forward **en cada arranque**
> con `pygit2` (y si la historia divergió, resetea a `origin/main`). Necesita internet al iniciar.
> Si falla, imprime `Update failed` y continúa con la copia local.

---

## 2. Requisitos reales

Según el README oficial:

| | Mínimo | Recomendado |
|---|---|---|
| VRAM | 6 GB | 8 GB para SDXL, 12 GB para Flux |
| RAM | 16 GB | 32 GB (SDXL), 48 GB (Flux) |
| Disco | 50 GB | 80–120 GB si vas a probar varios presets |
| Swap | — | ~40 GB en SSD (es la causa nº 1 de cuelgues) |

Plataformas: NVIDIA en Windows/Linux (incluye Blackwell 50xx nativo), Apple Silicon, AMD en
Linux (experimental). AMD en Windows: soporte parcial. Sin GPU dedicada funciona con
`--always-cpu`, pero a segundos/minutos por imagen.

Antes de instalar, ejecuta el chequeo incluido:

```bash
# Linux / macOS
bash scripts/preflight.sh

# Windows (PowerShell)
powershell -ExecutionPolicy Bypass -File scripts\preflight.ps1
```

Comprueba GPU y modelo, RAM, swap, disco libre, puerto 7860, `git`/`curl`/`uv` y salida a
GitHub + Hugging Face. Devuelve código 0 si puede instalar, 1 si falta algo bloqueante.

---

## 3. Instalación

### 3.1 Vía Pinokio (la del post)

1. Instala Pinokio 3.x desde <https://pinokio.computer> (Windows/macOS/Linux).
2. Abre Pinokio → pestaña **Discover** → busca `FooocusPlus`
   (también vale la URL directa: <https://pinokio.co/apps/github-com-6morpheus6-fooocusplus>).
3. **Install**. El launcher instala el bundle `ai` (uv + Python) si hace falta.
4. Espera: clone + dependencias + PyTorch + descargas iniciales. Son entre **15 y 40 min**
   según conexión; la descarga inicial ronda los **10–15 GB**.
5. Cuando pregunte **Select Language**, elige `Spanish`. Se guarda en
   `<carpeta del launcher>/language.json` y se aplica en cada arranque vía `--language es`.
6. Pulsa **Start**. Cuando el log diga `Comfy loading complete!`, el menú cambia a
   **Open Web UI** (o pestaña **Terminal** si prefieres el log a la vista).

Para cambiar el idioma después: **Stop** → **Select Language** → **Start**.

### 3.2 Vía manual (sin Pinokio)

El proyecto publica scripts de instalación en su wiki
([Linux](https://github.com/DavidDragonsage/FooocusPlus/wiki/Installation-Script-for-Linux),
[Windows](https://github.com/DavidDragonsage/FooocusPlus/wiki/Installation-Procedure-for-Windows)).
Sin Pinokio pierdes dos cosas: la elección automática de la rueda de PyTorch por GPU y el
`fs.share` de modelos con otras apps. Si ya tienes ComfyUI/Forge/Fooocus instalados, la vía
Pinokio sale más barata en disco.

---

## 4. Primeros pasos dentro de la app

1. **Preset** en la barra superior del lienzo (o *Settings → Presets*). Cada preset fija modelo,
   sampler y resolución; el modelo se descarga al generar la primera imagen con ese preset.
2. **Prompt** en tu idioma: FooocusPlus traduce automáticamente al inglés antes de pasar el
   texto al modelo.
3. **Advanced → Extras** para crear presets propios y **Favorite Preset Control** para fijar los
   que uses a diario.
4. Pestaña **Image** para img2img, **Inpaint/Outpaint**, **IP Adapter**, **IC Light**, face swap,
   background removal, control de VAE y el **Realtime Image Editor** (editas sobre el lienzo y
   el cambio se ve al instante).

Rendimiento: en SDXL con 8 GB de VRAM, 1024×1024 en ~20 pasos es cuestión de segundos;
Flux es bastante más lento y consume mucho más disco.

---

## 5. Compartir modelos con ComfyUI / Forge / Fooocus

`install.js` monta `UserDir/models/*` con `fs.share` y declara como *peers* a fluxgym,
automatic1111, comfyui, fooocus, comfy (pinokiofactory), MagicQuill y
stable-diffusion-webui-forge. En la práctica: **un solo `pinokio/drive` de modelos para todas
esas apps**, sin duplicar GB.

Ruta de trabajo: `<carpeta del launcher>/UserDir/models/…`

| Quiero usar… | Dónde va | Nota |
|---|---|---|
| SDXL / Pony / SD1.5 | `checkpoints/` | Se seleccionan directo en la UI |
| Flux, SD3.5, Hunyuan, Kolors (UNET) | `unet/` | Solo UNET; la app baja VAE y text encoder que falten |
| VAE propio | `vae/` | Útil para efectos concretos (control de VAE en la UI) |
| Text encoder propio | `clip/` | |
| LoRA | `loras/` | Multiselección de LoRA en Advanced |

Después de arrastrar archivos: **Refresh models** en la UI y seleccionar. Los modelos que
añadas siguen disponibles para las otras apps: es la misma carpeta compartida.

Si vienes de Forge/ComfyUI, copiar (o enlazar) ahí los checkpoints ya descargados evita bajar
otra vez 6–12 GB por modelo.

---

## 6. Modelos y presets

Soportados según la documentación oficial:

- SDXL y variantes amplias de SDXL · Pony Diffusion XL
- Flux (Black Forest Labs)
- Hunyuan-DiT · Kwai Kolors · Playground 2.5
- SD 1.5 · SD 3.5 Large & Medium
- Z-Image Base & Turbo
- Segmind-Vega (anunciado, aún no)

Orden de magnitud de disco (verifica el tamaño exacto en el log: la app imprime URL y destino
de cada descarga):

| Familia | Peso aproximado | Cuándo conviene |
|---|---|---|
| SD 1.5 | 2–4 GB | VRAM baja (<7 GB), iteración rápida |
| SDXL / Pony | 6–7 GB | Caballo de batalla, calidad/velocidad equilibradas |
| Flux (dev/schnell, fp8) | 12–25 GB con T5 + VAE | Realismo y texto en imagen; necesita 12 GB VRAM |
| SD 3.5 Large | ~8–16 GB según precisión | Alternativa a Flux con otra estética |

Regla práctica: **un preset SDXL + uno Flux** cubre el 90 % de los casos. No instales todo el
catálogo "por si acaso": cada familia añade decenas de GB.

---

## 7. Problemas típicos

| Síntoma | Causa / arreglo |
|---|---|
| Cuelgue al cargar modelo, `Killed`, `Segmentation fault`, `Connection errored out` | Falta swap. ~40 GB en SSD (el troubleshoot oficial lo repite para casi todo) |
| `Model corrupted` / `PytorchStreamReader failed` | Descarga incompleta: la app la repite sola; si no, borra el archivo en `UserDir/models/...` y regenera |
| `Torch not compiled with CUDA enabled` | Se instaló la rueda CPU. Reinstala con Pinokio (usa `torch.js`) o fuerza GPU + `uv pip install` de la rueda CUDA correcta |
| Puerto 7860 ocupado | Cierra la otra instancia (ComfyUI/Forge también usan 7860) o cambia el puerto en `start.js` |
| `Update failed` en cada arranque | Sin acceso a GitHub desde esa máquina; la app sigue funcionando con la copia local |
| Muy lento sin GPU | Es CPU: baja resolución y pasos, o usa SD1.5. `--always-cpu` lo pone el launcher solo |
| UI en inglés pese a elegir español | El idioma se aplica al arrancar: **Stop** → **Select Language** → **Start** |
| Se queda sin disco | `Reset` borra `app/env`; los modelos en `UserDir` y en `pinokio/drive` hay que limpiarlos a mano |

Troubleshooting original completo:
<https://github.com/DavidDragonsage/FooocusPlus/blob/main/troubleshoot.md>

---

## 8. Licencia y uso comercial

FooocusPlus es **GPL-3.0** y el README añade condiciones: algunos modelos incluidos son
**solo para uso comunitario no comercial**, y el usuario debe comprar la licencia
correspondiente antes de distribuir comercialmente imágenes generadas con ellos. Si las
imágenes van a un cliente (por ejemplo, material para Abyss Tattoo Studio), revisa la licencia
del modelo concreto antes de publicar: SDXL y SD1.5 suelen ser permisivos; Flux dev tiene sus
propios términos; algunos checkpoints comunitarios, no.

---

## 9. Estado de esta entrega

En este sandbox **no se puede ejecutar FooocusPlus**: no hay GPU (`nvidia-smi` ausente, 3 GB de
RAM, 2 vCPU) y la red solo permite `github.com`, `codeload.github.com`, `api.github.com`,
`registry.npmjs.org` y `pypi.org` — **`huggingface.co` está bloqueado**, así que ni siquiera se
podrían bajar los modelos iniciales. Por eso esta carpeta entrega el procedimiento verificable
(preflight + runbook) y no una instalación a medias.

Qué está verificado contra los repos (no contra el post):

- contenido real de `pinokio.js`, `install.js`, `start.js`, `torch.js` del launcher;
- `requirements_linux.txt` / `requirements_versions.txt` y readme de la app;
- puerto 7860, flags `--language`, `--gpu-type none`, `--always-cpu`, `--disable-in-browser`;
- carpetas compartidas y peers de `fs.share`.

Qué **no** está verificado: los pesos exactos de cada modelo (cambian con las actualizaciones) y
el rendimiento real en tu GPU. Ambos se confirman en el log de la primera generación.

Siguiente paso sugerido: correr `scripts/preflight.sh` en la máquina donde vayas a generar
(o el `.ps1` en Windows) y, si sale verde, instalar desde Pinokio. Si prefieres seguir la
instalación en vivo sobre esa máquina, dime qué GPU y cuánto disco tiene y lo hacemos paso a paso.
