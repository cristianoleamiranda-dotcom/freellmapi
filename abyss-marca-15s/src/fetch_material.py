"""Descarga el material fuente desde el repo abysstattoo por SHA.

raw.githubusercontent puede estar bloqueado; la API de blobs sí funciona y
devuelve el binario con Accept: application/vnd.github.raw.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path

REPO = "cristianoleamiranda-dotcom/abysstattoo"
REF = "main"
OUT = Path(__file__).resolve().parent.parent / "material"

FILES = [
    # video real
    "film/hero_film.mp4",
    "film/proceso_filmacion.mp4",
    "film/proceso_detalle.mp4",
    "film/proceso_pierna.mp4",
    "film/loop_film.mp4",
    # marca
    "assets/logo_abyss_256.png",
    "assets/reel_plates/emblema_abyss_alpha.png",
    "assets/skull_mark_crema.png",
    # trabajos
    "assets/trabajos/trabajo_hombro_real.jpg",
    "assets/trabajos/trabajo_cristo_manga.jpg",
    "assets/trabajos/trabajo_lobo_rugido.jpg",
    "assets/trabajos/trabajo_lobo_luna.jpg",
    "assets/trabajos/helice.jpg",
    "assets/trabajos/septum.jpg",
    "assets/trabajos/proceso_hombro.jpg",
    # estudio
    "assets/estudio/fachada.jpg",
    "assets/estudio/vitrina.jpg",
    "assets/estudio/maestro.jpg",
    # tipografía
    "assets/fonts/cinzel-700.ttf",
    "assets/fonts/cinzel-800.ttf",
    "assets/fonts/montserrat-500.ttf",
    "assets/fonts/montserrat-600.ttf",
    "assets/fonts/montserrat-700.ttf",
]

API = "https://api.github.com"


def gh_json(path: str) -> dict:
    req = urllib.request.Request(
        f"{API}/{path}",
        headers={"Accept": "application/vnd.github+json", "User-Agent": "abyss-marca-15s"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def main() -> int:
    tree = gh_json(f"repos/{REPO}/git/trees/{REF}?recursive=1")
    by_path = {t["path"]: t for t in tree.get("tree", [])}
    OUT.mkdir(parents=True, exist_ok=True)
    missing: list[str] = []
    total = 0
    for rel in FILES:
        node = by_path.get(rel)
        if not node:
            missing.append(rel)
            continue
        dst = OUT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists() and dst.stat().st_size == node.get("size"):
            total += dst.stat().st_size
            continue
        req = urllib.request.Request(
            f"{API}/repos/{REPO}/git/blobs/{node['sha']}",
            headers={"Accept": "application/vnd.github.raw", "User-Agent": "abyss-marca-15s"},
        )
        with urllib.request.urlopen(req, timeout=180) as r:
            data = r.read()
        dst.write_bytes(data)
        total += len(data)
        print(f"  {len(data) / 1e6:6.2f} MB  {rel}")
    print(f"material: {len(FILES) - len(missing)}/{len(FILES)} archivos, {total / 1e6:.1f} MB en {OUT}")
    if missing:
        print("faltan:", ", ".join(missing))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
