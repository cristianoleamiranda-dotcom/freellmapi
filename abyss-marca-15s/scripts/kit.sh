#!/usr/bin/env bash
# Empaqueta los entregables de una versión en un ZIP listo para descargar/enviar.
# Uso: bash scripts/kit.sh [--long]
#   --long  empaqueta la versión de 18 s
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

LONG=0
for arg in "$@"; do
  case "$arg" in
    --long) LONG=1 ;;
    *) echo "Argumento no reconocido: $arg"; exit 2 ;;
  esac
done

if [ "$LONG" -eq 1 ]; then
  SLUG=abyss_marca_18s
  SUFFIX=_18s
  DUR=18
else
  SLUG=abyss_marca_15s
  SUFFIX=
  DUR=15
fi

DIST="$ROOT/dist"
NAME="abyss-marca-${DUR}s-kit"
STAGE="$DIST/$NAME"
rm -rf "$STAGE"
mkdir -p "$STAGE"

FILES=(
  "out/${SLUG}_1080x1920_60fps.mp4"
  "out/${SLUG}_1080x1920_30fps.mp4"
  "out/${SLUG}_720x1280_preview.mp4"
  "out/${SLUG}_visor.html"
  "out/cover_emblema${SUFFIX}.jpg"
  "out/poster_cta${SUFFIX}.jpg"
  "out/storyboard${SUFFIX}.jpg"
)
MANIFEST="out/manifest${SUFFIX}.json"
[ -f "$MANIFEST" ] && FILES+=("$MANIFEST")

missing=0
for f in "${FILES[@]}"; do
  if [ -f "$f" ]; then
    cp "$f" "$STAGE/"
  else
    echo "  falta: $f"; missing=1
  fi
done
[ "$missing" -eq 0 ] || { echo "build incompleto: corre bash scripts/build.sh$([ "$LONG" -eq 1 ] && echo ' --long')"; exit 1; }

# LEEME específico de la versión
cat > "$STAGE/LEEME.txt" <<TXT
ABYSS TATTOO STUDIO · pieza de marca ${DUR} s
===============================================

Formato  1080 x 1920 (9:16), H.264 High 4.2, BT.709, AAC 48 kHz estéreo
Duración ${DUR}.00 s exactos · rejilla de 100 BPM
Música   sintetizada para esta pieza (sin samples de terceros, sin licencias que resolver)

Qué archivo usar
----------------
${SLUG}_1080x1920_60fps.mp4    Máster. Es el que se publica en Reels/TikTok y el que
                               conviene entregar a un cliente o subir a una landing.
${SLUG}_1080x1920_30fps.mp4    Misma imagen a 30 fps, ~40 % más liviano: web, correo.
${SLUG}_720x1280_preview.mp4   Previa de ~3 MB: abre al instante, ideal para WhatsApp.
${SLUG}_visor.html             Visor autónomo. Doble clic y funciona sin internet
                               (el video va dentro del HTML en base64).
cover_emblema${SUFFIX}.jpg     Portada del Reel.
poster_cta${SUFFIX}.jpg        Pieza estática de refuerzo (mismo arte, para feed/story).
storyboard${SUFFIX}.jpg        Hoja de contacto con 14 momentos: sirve para revisar el corte.
manifest${SUFFIX}.json         Peso y SHA-256 de cada archivo: comprueba que llegó intacto.

Cómo verificar una copia
------------------------
  shasum -a 256 -c <(python3 - <<'PY'
  import json,pathlib
  m=json.load(open('manifest${SUFFIX}.json'))
  print("\n".join(f"{r['sha256']}  {r['file']}" for r in m['files']))
  PY
  )

Reconstrucción
--------------
Todo el montaje vive en el repo cristianoleamiranda-dotcom/freellmapi, carpeta
abyss-marca-15s/. Las fuentes (logo, fotos y clips) están en el repo abysstattoo
y se bajan con src/fetch_material.py. Ver README.md para el detalle plano a plano.
TXT

(cd "$DIST" && rm -f "${NAME}.zip" && python3 -c "
import pathlib, zipfile
name = '${NAME}'
stage = pathlib.Path(name)
with zipfile.ZipFile(name + '.zip', 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for p in sorted(stage.rglob('*')):
        if p.is_file():
            z.write(p, p.relative_to(stage.parent))
print('zip ok')
")

SIZE=$(du -h "$DIST/${NAME}.zip" | cut -f1)
echo "  dist/${NAME}.zip · ${SIZE}"
python3 - <<PY
import zipfile
z = zipfile.ZipFile("$DIST/${NAME}.zip")
print(f"  {len(z.namelist())} archivos dentro:")
for n in z.namelist():
    print(f"    {n}  ({z.getinfo(n).file_size/1e6:.1f} MB)")
PY
