"""Ingeniería inversa de la referencia de motion design.

Extrae fotograma a fotograma con ffmpeg, calcula flujo óptico
(cv2.calcOpticalFlowFarneback), detecta cortes y eventos cinéticos, y
exporta la curva de energía de movimiento + hojas de contacto.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
FFMPEG = str(ROOT / "bin" / "ffmpeg")


def extract(video: Path, out: Path, fps: int | None = None, scale: str | None = None) -> list[Path]:
    out.mkdir(parents=True, exist_ok=True)
    vf = []
    if scale:
        vf.append(f"scale={scale}")
    if fps:
        vf.append(f"fps={fps}")
    cmd = [FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-i", str(video)]
    if vf:
        cmd += ["-vf", ",".join(vf)]
    cmd += ["-q:v", "3", str(out / "f_%05d.jpg")]
    subprocess.run(cmd, check=True)
    return sorted(out.glob("f_*.jpg"))


def analyze(frames: list[Path], out_json: Path, fps: float) -> dict:
    prev = None
    rows = []
    for i, fp in enumerate(frames):
        img = cv2.imread(str(fp))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        small = cv2.resize(gray, (180, 225))
        rec = {"i": i, "t": round(i / fps, 4)}
        if prev is not None:
            mad = float(np.mean(cv2.absdiff(small, prev[0])))
            flow = cv2.calcOpticalFlowFarneback(
                prev[0], small, None,
                pyr_scale=0.5, levels=3, winsize=21,
                iterations=3, poly_n=7, poly_sigma=1.5, flags=0,
            )
            mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
            dx, dy = float(np.mean(flow[..., 0])), float(np.mean(flow[..., 1]))
            rec.update(
                mad=round(mad, 3),
                flow_mean=round(float(mag.mean()), 3),
                flow_p95=round(float(np.percentile(mag, 95)), 3),
                flow_max=round(float(mag.max()), 2),
                dx=round(dx, 3), dy=round(dy, 3),
                moving=round(float((mag > 0.5).mean()), 4),
                lum=round(float(gray.mean()), 2),
            )
        rows.append(rec)
        prev = (small, gray)

    # cortes: pico de MAD muy por encima de la mediana
    mads = np.array([r.get("mad", 0.0) for r in rows])
    med = np.median(mads[1:]) if len(mads) > 1 else 0.0
    thr = max(12.0, med * 6)
    cuts = [r["t"] for r in rows if r.get("mad", 0) > thr]
    fm = np.array([r.get("flow_mean", 0.0) for r in rows])
    whip_thr = float(np.percentile(fm[1:], 90)) if len(fm) > 2 else 0.0
    whips = [{"t": r["t"], "flow": r["flow_mean"], "dx": r["dx"], "dy": r["dy"]}
             for r in rows if r.get("flow_mean", 0) > whip_thr]

    data = {
        "frames": len(rows),
        "fps": fps,
        "duration": round(len(rows) / fps, 3),
        "mad_median": round(float(med), 3),
        "cut_threshold": round(float(thr), 3),
        "cuts": cuts,
        "n_cuts": len(cuts),
        "whip_threshold": round(whip_thr, 3),
        "whips": whips,
        "flow_peak": round(float(fm.max()), 3),
        "flow_mean_global": round(float(fm[1:].mean()), 3),
        "per_frame": rows,
    }
    out_json.write_text(json.dumps(data, indent=1))
    return data


def plot(data: dict, out_png: Path, fps: float):
    from PIL import Image, ImageDraw
    W, H = 1600, 520
    im = Image.new("RGB", (W, H), (10, 10, 12))
    d = ImageDraw.Draw(im)
    rows = [r for r in data["per_frame"] if "flow_mean" in r]
    n = len(rows)
    fmax = max(r["flow_mean"] for r in rows) or 1
    mmax = max(r["mad"] for r in rows) or 1
    def X(i): return 40 + int(i / max(n - 1, 1) * (W - 80))
    # flujo óptico (energía cinética)
    pts = [(X(i), H - 60 - int(r["flow_mean"] / fmax * (H - 140))) for i, r in enumerate(rows)]
    d.line(pts, fill=(158, 196, 186), width=2)
    # MAD (cortes)
    pts2 = [(X(i), H - 60 - int(r["mad"] / mmax * (H - 140))) for i, r in enumerate(rows)]
    d.line(pts2, fill=(181, 162, 149), width=1)
    for t in data["cuts"]:
        x = X(int(round(t * fps)))
        d.line([(x, 30), (x, H - 55)], fill=(234, 227, 221), width=2)
        d.text((x + 4, 32), f"{t:.2f}", fill=(234, 227, 221))
    d.text((40, 8), "teal = flow_mean (energía cinética) · hueso = MAD (cambio de píxel) · líneas blancas = cortes detectados", fill=(234, 227, 221))
    for s in range(0, int(data["duration"]) + 1):
        x = X(int(s * fps))
        d.line([(x, H - 60), (x, H - 52)], fill=(120, 120, 120))
        d.text((x - 6, H - 45), f"{s}s", fill=(150, 150, 150))
    im.save(out_png)


def contact(frames: list[Path], out_png: Path, step: int, cols: int = 6, thumb=(180, 225)):
    from PIL import Image
    idx = list(range(0, len(frames), step))
    rows = (len(idx) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb[0] + 10, rows * (thumb[1] + 16) + 10), (14, 12, 11))
    from PIL import ImageDraw
    d = ImageDraw.Draw(sheet)
    for k, i in enumerate(idx):
        im = Image.open(frames[i]).convert("RGB").resize(thumb)
        x = 5 + (k % cols) * thumb[0]
        y = 5 + (k // cols) * (thumb[1] + 16)
        sheet.paste(im, (x, y))
        d.text((x + 3, y + thumb[1] + 1), f"#{i} {i/30:.2f}s", fill=(230, 224, 218))
    sheet.save(out_png)
    return len(idx)


if __name__ == "__main__":
    src = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT.parent / "dropbox" / "type_01_pindown.io_1795195281.mp4")
    fps = float(sys.argv[2]) if len(sys.argv) > 2 else 30.0
    tag = src.stem.split("_pindown")[0]
    fdir = ROOT / "research" / f"frames_{tag}"
    frames = extract(src, fdir)
    data = analyze(frames, ROOT / "research" / f"motion_{tag}.json", fps)
    plot(data, ROOT / "research" / f"motion_{tag}.png", fps)
    contact(frames, ROOT / "research" / f"contact_{tag}.jpg", step=max(1, len(frames) // 42))
    print(f"{tag}: {data['frames']} frames · {data['duration']}s · cortes={data['n_cuts']} en {data['cuts']}")
    print(f"  flow peak={data['flow_peak']} media={data['flow_mean_global']}")
