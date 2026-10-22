#!/usr/bin/env bash
# Reconstruye la pieza completa desde cero (material incluido).
# Uso: bash scripts/build.sh [--no-fetch]
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [ "${1:-}" != "--no-fetch" ]; then
  echo "== material · repo abysstattoo"
  python3 src/fetch_material.py
fi

echo "== audio · 100 BPM, 15.0 s"
python3 src/audio.py

echo "== render · 900 frames, master + derivadas + piezas"
python3 src/render.py

echo "== visor autónomo"
python3 src/standalone.py

echo "== manifiesto"
python3 src/manifest.py

echo
echo "listo. entregables en out/:"
ls -lh out/ | awk 'NR>1 {printf "  %-42s %s\n", $9, $5}'
echo
echo "verificación rápida:"
python3 - <<'PY'
import json, hashlib, pathlib
out = pathlib.Path("out")
man = json.loads((out / "manifest.json").read_text())
bad = 0
for row in man["files"]:
    p = out / row["file"]
    ok = p.exists() and hashlib.sha256(p.read_bytes()).hexdigest() == row["sha256"]
    bad += 0 if ok else 1
print(f"  manifest: {len(man['files'])} archivos, {bad} con hash distinto")
PY
