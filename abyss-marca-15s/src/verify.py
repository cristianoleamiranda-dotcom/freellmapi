#!/usr/bin/env python3
"""QA del entregable: valida los MP4 reales, no los frames en memoria.

Motivo: en la primera pasada el máster salió con rojo y azul intercambiados
(se escribía BGR en un pipe RGB) y el storyboard, generado en memoria, se veía
correcto. Este script decodifica el archivo publicado y lo compara contra un
render fresco del mismo instante, así ese error no puede volver a pasar.

Uso:
    python3 src/verify.py            # informe + código 0/1
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import cv2
import imageio_ffmpeg
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
FF = imageio_ffmpeg.get_ffmpeg_exe()

SLUG = os.environ.get("ABYSS_SLUG", "abyss_marca_15s")
EXPECTED = float(os.environ.get("ABYSS_DURATION", "15.0"))
VERSION_TAG = "" if int(round(EXPECTED)) == 15 else f"_{int(round(EXPECTED))}s"
MANIFEST = OUT / ("manifest.json" if VERSION_TAG == "" else f"manifest{VERSION_TAG}.json")

MASTER = f"{SLUG}_1080x1920_60fps.mp4"
DERIVADAS = [
    (f"{SLUG}_1080x1920_30fps.mp4", 1080, 1920, 30),
    (f"{SLUG}_720x1280_preview.mp4", 720, 1280, 60),
]
CHECK_TIMES = [round(EXPECTED * f, 2) for f in (0.08, 0.32, 0.51, 0.83, 0.95)]
MAX_DIFF = 12.0           # diferencia media admitida frente al render fresco
MAX_CHANNEL_SHIFT = 6.0   # |media(canal) archivo − render fresco| máximo


def probe(path: Path) -> dict:
    p = subprocess.run([FF, "-hide_banner", "-i", str(path)], capture_output=True, text=True)
    info: dict = {"dur": None, "w": None, "h": None, "fps": None, "audio": False}
    for line in p.stderr.splitlines():
        if "Duration:" in line:
            hh, mm, ss = line.split("Duration:")[1].split(",")[0].strip().split(":")
            info["dur"] = int(hh) * 3600 + int(mm) * 60 + float(ss)
        if "Video:" in line:
            parts = line.split(",")
            size = [x.strip() for x in parts if "x" in x and x.strip().replace("x", "").isdigit()]
            if size:
                w, h = size[0].split("x")
                info["w"], info["h"] = int(w), int(h)
            fps = [x.strip() for x in parts if x.strip().endswith("fps")]
            if fps:
                info["fps"] = float(fps[0].split(" ")[0])
        if "Audio:" in line:
            info["audio"] = True
    return info


def frame_from(path: Path, t: float) -> np.ndarray:
    raw = subprocess.run(
        [FF, "-v", "error", "-ss", f"{t}", "-i", str(path), "-frames:v", "1",
         "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        capture_output=True,
    ).stdout
    if not raw:
        raise RuntimeError(f"no pude decodificar {path.name} en {t}s")
    return np.frombuffer(raw, dtype=np.uint8).reshape(info_shape(path))


def info_shape(path: Path) -> tuple[int, int, int]:
    pr = probe(path)
    return pr["h"], pr["w"], 3


def main() -> int:
    ok = True
    print("QA · entregables")

    manifest_path = MANIFEST
    if manifest_path.exists():
        man = json.loads(manifest_path.read_text())
        bad = [r["file"] for r in man["files"]
               if not (OUT / r["file"]).exists()
               or hashlib.sha256((OUT / r["file"]).read_bytes()).hexdigest() != r["sha256"]]
        print(f"  manifest: {len(man['files'])} archivos · hash distintos: {bad or 'ninguno'}")
        ok &= not bad
    else:
        print("  manifest: FALTA"); ok = False

    for name, w, h, fps in [(MASTER, 1080, 1920, 60)] + DERIVADAS:
        path = OUT / name
        if not path.exists():
            print(f"  {name}: FALTA"); ok = False; continue
        pr = probe(path)
        good = (pr["w"], pr["h"]) == (w, h) and abs((pr["fps"] or 0) - fps) < 0.5 \
            and pr["dur"] is not None and abs(pr["dur"] - EXPECTED) <= 0.07 and pr["audio"]
        print(f"  {name}: {pr['w']}x{pr['h']} {pr['fps']}fps {pr['dur']:.2f}s "
              f"audio={'sí' if pr['audio'] else 'NO'} → {'ok' if good else 'REVISAR'}")
        ok &= bool(good)

    # comparación contra un render fresco: detecta canales invertidos, LUT, etc.
    from render import Resources, frame_at  # import tardío: sólo aquí hace falta

    res = Resources()
    try:
        diffs, shifts = [], []
        for t in CHECK_TIMES:
            fresh = cv2.cvtColor(frame_at(t, res), cv2.COLOR_BGR2RGB).astype(np.int16)
            shipped = frame_from(OUT / MASTER, t).astype(np.int16)
            diffs.append(float(np.abs(fresh - shipped).mean()))
            # desfase por canal: si R y B se intercambian, ambos se disparan
            shifts.append(max(abs(float(shipped[..., c].mean() - fresh[..., c].mean())) for c in range(3)))
        worst = max(diffs)
        shift = max(shifts)
        good = worst <= MAX_DIFF and shift <= MAX_CHANNEL_SHIFT
        print(f"  máster vs render fresco: peor diferencia media {worst:.2f} (límite {MAX_DIFF}) · "
              f"desfase por canal {shift:.2f} (límite {MAX_CHANNEL_SHIFT}) → {'ok' if good else 'REVISAR'}")
        ok &= bool(good)
    finally:
        res.close()

    # idempotencia: un frame no puede depender de qué frames se renderizaron antes
    from render import Resources as R2, frame_at as fa2

    probe_res = R2()
    try:
        probe_t = round(EXPECTED * 0.03, 2)   # dentro del primer bloque de texto
        isolated = cv2.cvtColor(fa2(probe_t, probe_res), cv2.COLOR_BGR2RGB).astype(np.int16)
        for t in (0.0, 0.1, 0.2, 0.3, 0.4):
            fa2(t, probe_res)
        after = cv2.cvtColor(fa2(probe_t, probe_res), cv2.COLOR_BGR2RGB).astype(np.int16)
    finally:
        probe_res.close()
    drift = float(np.abs(isolated - after).mean())
    good = drift <= 0.5
    print(f"  idempotencia del render (t={probe_t:.2f} aislado vs tras una secuencia): "
          f"{drift:.3f} → {'ok' if good else 'REVISAR (estado mutado entre frames)'}")
    ok &= bool(good)

    print("resultado:", "TODO OK" if ok else "HAY QUE REVISAR")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
