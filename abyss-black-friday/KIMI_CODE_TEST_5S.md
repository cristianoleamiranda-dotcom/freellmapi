# ABYSS · Pindown test 5 s — Kimi Code

## Objetivo
Render local de una prueba de 5 segundos, vertical 9:16, 1080×1920, 30 fps,
con el lenguaje de montaje de la referencia Pindown. No usar servicios de
generación ni créditos externos. No modificar ni sobrescribir originales.

## Fuentes de verdad
- Skill de producción: `.github/skills/abyss-motion-graphics/SKILL.md`
- Pipeline offline: `abyss-black-friday/src/{brand,media,kinetic,timeline,render}.py`
- Transferencia de movimiento: `abyss-black-friday/research/MOTION-TRANSFER.md`
- Nuevo corte de prueba: `abyss-black-friday/src/render_test_5s.py`
- Referencia Pindown y originales: carpeta Dropbox `/ABYSS_BLACK_FRIDAY_ASSETS/material/`

## Montaje aprobado
- 0.00–2.00 s: hook tipográfico agresivo, push-in y lettering recortado.
- 2.00–4.00 s: tres fotografías reales en paneles editoriales, con zoom y entradas escalonadas.
- 4.00–5.00 s: cierre con el texto literal `BLACK FRIDAY · ABYSS TATTOO STUDIO`
  (se compone en dos capas tipográficas: BLACK FRIDAY / ABYSS TATTOO STUDIO).
- 150 fotogramas exactos. Sin audio en esta prueba para evaluar primero el motion.

## Preparación
1. Clona el repo y cambia a la rama `abyss/pindown-test-5s`.
2. Conserva los originales. Coloca los materiales de Dropbox en la estructura
   local que espera `abyss-black-friday/src/render.py`:
   - `abyss-black-friday/dropbox/18.jpg`
   - `abyss-black-friday/dropbox/AV_SEL_27_0180.jpg`
   - `abyss-black-friday/dropbox/1000025791.JPG (1).webp`
   - además de los demás plates requeridos por `build_plates()`.
3. Descarga recursos de marca/fuentes del repositorio de ABYSS:
   `python src/fetch_github.py` ejecutado desde `abyss-black-friday`.
4. Instala las dependencias declaradas por el proyecto. Comprueba que
   `abyss-black-friday/bin/ffmpeg` existe y es ejecutable.

## Render
Desde `abyss-black-friday`:
```bash
python src/render_test_5s.py
```

Salida esperada:
`abyss-black-friday/out/abyss_pindown_test_5s_1080x1920_30fps.mp4`

## Control de calidad obligatorio
- `ffprobe`: 1080×1920, 30/1 fps, 5.00 s, H.264 High, yuv420p, BT.709.
- Decodificar el MP4 completo sin errores.
- Revisar fotogramas 0.0, 0.5, 1.0, 1.9, 2.1, 2.8, 3.5, 3.9, 4.2 y 4.9.
- Verificar anatomía, integridad de tatuajes, contornos y legibilidad.
- Comparar energía y ritmo con la referencia; no declarar réplica exacta sin medición.
- No marcar PASS ni publicar si faltan originales, el texto se corta o hay deformaciones.

Si falta un asset o no se puede acceder a Dropbox, detenerse y reportar el archivo
exacto faltante. No sustituirlo con imágenes inventadas.
