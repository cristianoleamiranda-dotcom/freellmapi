#!/usr/bin/env python3
"""Manifiesto de entregables: peso y SHA-256 de cada archivo de out/.

Se ejecuta al final del build (después del visor autónomo) para que el hash del
HTML también quede registrado:

    python3 src/manifest.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"

PIECE = "abyss-marca-15s"
FORMAT = "1080x1920 · 60 fps · H.264 High 4.2 · AAC 48 kHz · BT.709"
DURATION = 15.0


def build(out: Path = OUT) -> dict:
    rows = []
    for path in sorted(out.iterdir()):
        if path.name == "manifest.json" or not path.is_file():
            continue
        rows.append({
            "file": path.name,
            "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        })
    data = {
        "piece": PIECE,
        "format": FORMAT,
        "duration_s": DURATION,
        "files": rows,
    }
    (out / "manifest.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    return data


if __name__ == "__main__":
    data = build()
    print(f"manifest.json · {len(data['files'])} archivos")
    sys.exit(0)
