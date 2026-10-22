#!/usr/bin/env bash
# Reconstruye la pieza completa desde cero (material incluido).
# Uso: bash scripts/build.sh [--no-fetch] [--long]
#   --long  monta la versión de 18 s (ABYSS_TIMELINE=timeline_largo, ABYSS_DURATION=18)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

NO_FETCH=0
LONG=0
for arg in "$@"; do
  case "$arg" in
    --no-fetch) NO_FETCH=1 ;;
    --long) LONG=1 ;;
    *) echo "Argumento no reconocido: $arg"; exit 2 ;;
  esac
done

if [ "$LONG" -eq 1 ]; then
  export ABYSS_TIMELINE=timeline_largo
  export ABYSS_DURATION=18
  export ABYSS_SLUG=abyss_marca_18s
  echo "== versión larga · 18.0 s (30 negras a 100 BPM)"
fi

if [ "$NO_FETCH" -eq 0 ]; then
  echo "== material · repo abysstattoo"
  python3 src/fetch_material.py
fi

DUR="${ABYSS_DURATION:-15}"
echo "== audio · 100 BPM, ${DUR} s"
python3 src/audio.py

echo "== render · ${DUR} s, master + derivadas + piezas"
python3 src/render.py

echo "== visor autónomo"
python3 src/standalone.py

echo "== manifiesto"
python3 src/manifest.py

echo
echo "listo. entregables en out/ (versión ${DUR} s):"
ls -lh out/ | awk 'NR>1 {printf "  %-42s %s\n", $9, $5}'
echo
echo "verificación rápida:"
python3 - <<'PY'
import json, hashlib, os, pathlib
out = pathlib.Path("out")
tag = "" if int(float(os.environ.get("ABYSS_DURATION", "15"))) == 15 else f"_{int(float(os.environ.get('ABYSS_DURATION', '15')))}s"
man = json.loads((out / f"manifest{tag}.json").read_text())
bad = 0
for row in man["files"]:
    p = out / row["file"]
    ok = p.exists() and hashlib.sha256(p.read_bytes()).hexdigest() == row["sha256"]
    bad += 0 if ok else 1
print(f"  manifest: {len(man['files'])} archivos, {bad} con hash distinto")
PY
