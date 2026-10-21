#!/usr/bin/env bash
# Publica la pieza como release de GitHub y arma el kit descargable.
#
# Requisitos: gh autenticado con permiso sobre el repo, python3, zip.
# Uso:
#   scripts/publicar.sh                 # crea/actualiza el release con los archivos de out/
#   scripts/publicar.sh --draft         # deja el release en borrador
#
# El release queda en:
#   https://github.com/<owner>/<repo>/releases/tag/abyss-historia-15s

set -euo pipefail

cd "$(dirname "$0")/.."

REPO="${REPO:-cristianoleamiranda-dotcom/freellmapi}"
TAG="${TAG:-abyss-historia-15s}"
NAME="Abyss Tattoo Studio · historia 15 s"
DIST="dist"
KIT="$DIST/abyss-historia-15s-kit.zip"

echo "· verificando piezas"
for f in \
  out/abyss_historia_15s_1080x1920_60fps.mp4 \
  out/abyss_historia_15s_1080x1920_30fps.mp4 \
  out/abyss_historia_15s_720x1280_preview.mp4 \
  out/cover_hook.jpg out/poster_cta.jpg out/storyboard.jpg out/manifest.json
do
  [ -f "$f" ] || { echo "  ✗ falta $f"; exit 1; }
done

echo "· generando visor autónomo"
python3 src/standalone.py

echo "· armando kit"
rm -rf "$DIST/kit" && mkdir -p "$DIST/kit/abyss-historia-15s"
cp -R preview "$DIST/kit/abyss-historia-15s/"
cp -R out "$DIST/kit/abyss-historia-15s/"
cp README.md index.html "$DIST/kit/abyss-historia-15s/"
rm -f "$DIST/kit/abyss-historia-15s/out/manifest.json.tmp"
mkdir -p "$DIST"
( cd "$DIST/kit" && zip -qr "../abyss-historia-15s-kit.zip" abyss-historia-15s )
rm -rf "$DIST/kit"

NOTES="$(mktemp)"
cat > "$NOTES" <<'MD'
Historia vertical de **15.00 s** para **Abyss Tattoo Studio** (José Joaquín Pérez 528, San Bernardo).
Montada desde el material original del repo `abysstattoo`: 5 clips de sesión y 26 fotografías.

| | |
|---|---|
| Formato | 1080 × 1920 (9:16) · 60 fps · H.264 High 4.2 · BT.709 · AAC 48 kHz |
| Duración | 15.00 s exactos (900 frames) |
| Rejilla | 100 BPM · 0.6 s por negra |
| Audio | banda sintetizada, sin muestras de terceros |

## Archivos

| Archivo | Uso |
|---|---|
| `abyss_historia_15s_1080x1920_60fps.mp4` | Máster para publicar (Reels, TikTok, Meta Ads) |
| `abyss_historia_15s_1080x1920_30fps.mp4` | Versión web / WhatsApp |
| `abyss_historia_15s_720x1280_preview.mp4` | Previa ligera para compartir |
| `abyss_historia_15s_visor.html` | **Visor autónomo** (5 MB): el video va dentro del HTML, ábrelo con doble clic |
| `abyss-historia-15s-kit.zip` | Visor + todos los videos + documentos |
| `cover_hook.jpg` · `poster_cta.jpg` · `storyboard.jpg` | Portada, póster y hoja de contacto |

## Cómo verlo

1. Descarga `abyss_historia_15s_visor.html` y ábrelo con el navegador: no necesita internet.
2. O descarga el kit y abre `abyss-historia-15s/index.html`.
3. O reproduce directamente el máster con tu reproductor.

Los datos de contacto del cierre (dirección, WhatsApp e Instagram) están verificados con
fuentes públicas. No se usan años de experiencia, precios ni promociones.
MD

ARGS=(--repo "$REPO" --title "$NAME" --notes-file "$NOTES")
if [ "${1:-}" = "--draft" ]; then ARGS+=(--draft); fi

if gh release view "$TAG" --repo "$REPO" >/dev/null 2>&1; then
  echo "· el release existe: actualizando notas y archivos"
  gh release edit "$TAG" --repo "$REPO" --title "$NAME" --notes-file "$NOTES"
  gh release upload "$TAG" --repo "$REPO" --clobber \
    out/abyss_historia_15s_1080x1920_60fps.mp4 \
    out/abyss_historia_15s_1080x1920_30fps.mp4 \
    out/abyss_historia_15s_720x1280_preview.mp4 \
    out/abyss_historia_15s_visor.html \
    out/cover_hook.jpg out/poster_cta.jpg out/storyboard.jpg \
    "$KIT"
else
  echo "· creando release"
  gh release create "$TAG" "${ARGS[@]}" \
    out/abyss_historia_15s_1080x1920_60fps.mp4 \
    out/abyss_historia_15s_1080x1920_30fps.mp4 \
    out/abyss_historia_15s_720x1280_preview.mp4 \
    out/abyss_historia_15s_visor.html \
    out/cover_hook.jpg out/poster_cta.jpg out/storyboard.jpg \
    "$KIT"
fi

rm -f "$NOTES"
echo "✓ publicado: https://github.com/$REPO/releases/tag/$TAG"
