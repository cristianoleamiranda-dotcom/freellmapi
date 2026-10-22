#!/usr/bin/env python3
"""Manifiesto de entregables: peso y SHA-256 de cada archivo de out/.

Se ejecuta al final del build (después del visor autónomo) para que el hash del
HTML también quede registrado:

    python3 src/manifest.py
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"

SLUG = os.environ.get("ABYSS_SLUG", "abyss_marca_15s")
DURATION = float(os.environ.get("ABYSS_DURATION", "15.0"))
PIECE = SLUG.replace("_", "-")
FORMAT = "1080x1920 · 60 fps · H.264 High 4.2 · AAC 48 kHz · BT.709"
# Sólo los archivos de esta versión: el out/ contiene también la otra duración.
VERSION_TAG = "" if int(round(DURATION)) == 15 else f"_{int(round(DURATION))}s"
FILES = [
    f"{SLUG}_1080x1920_60fps.mp4",
    f"{SLUG}_1080x1920_30fps.mp4",
    f"{SLUG}_720x1280_preview.mp4",
    f"{SLUG}_visor.html",
    f"cover_emblema{VERSION_TAG}.jpg",
    f"poster_cta{VERSION_TAG}.jpg",
    f"storyboard{VERSION_TAG}.jpg",
]


def build(out: Path = OUT) -> dict:
    rows = []
    for name in FILES:
        path = out / name
        if not path.exists():
            continue
        rows.append({
            "file": name,
            "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        })
    data = {
        "piece": PIECE,
        "format": FORMAT,
        "duration_s": DURATION,
        "files": rows,
    }
    target = out / ("manifest.json" if VERSION_TAG == "" else f"manifest{VERSION_TAG}.json")
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    return data


if __name__ == "__main__":
    data = build()
    print(f"manifest.json · {len(data['files'])} archivos")
    sys.exit(0)
