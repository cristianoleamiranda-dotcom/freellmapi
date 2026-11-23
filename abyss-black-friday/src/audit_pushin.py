"""Auditoría 1b (v2): push-in / pan medidos de verdad en los frames entregados.

La divergencia del flujo a 270 px de ancho de análisis no tiene sensibilidad para un
push-in de ~0,16 %/frame. Aquí se estima el modelo afín del flujo entre dos frames
separados 10 cuadros (v = A·(p-c) + b) por mínimos cuadrados: traza(A)/2 es la tasa de
zoom (expansión) y b la traslación (pan). Se mide en la referencia y en cada pieza con
las mismas ventanas relativas, para que la comparación sea apples-to-apples.

Salida: research/audit_pushin_report.json
"""
from __future__ import annotations
import json
from pathlib import Path
import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
REF = ROOT.parent / "dropbox" / "type_01_pindown.io_1795195281.mp4"
W = 540          # ancho de análisis (sensibilidad 4x mayor que 270)
GAP = 10         # frames entre las dos muestras de cada ventana
N_WIN = 8        # ventanas por pieza


def read(path: Path):
    cap = cv2.VideoCapture(str(path)); frs = []
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        frs.append(fr)
    cap.release()
    return frs


def affine_flow(a, b):
    h = int(round(W * a.shape[0] / a.shape[1]))
    ga = cv2.cvtColor(cv2.resize(a, (W, h), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY)
    gb = cv2.cvtColor(cv2.resize(b, (W, h), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY)
    f = cv2.calcOpticalFlowFarneback(ga, gb, None, 0.5, 3, 21, 3, 7, 1.5, 0)
    ys, xs = np.mgrid[0:h:3, 0:W:3]
    px = (xs - W / 2).astype(np.float32).ravel()
    py = (ys - h / 2).astype(np.float32).ravel()
    vx = f[ys, xs, 0].ravel(); vy = f[ys, xs, 1].ravel()
    n = px.size
    # v = A·p + b  →  columnas [px, py, 1] por componente
    M = np.stack([px, py, np.ones(n)], axis=1)
    cx, *_ = np.linalg.lstsq(M, vx, rcond=None)
    cy, *_ = np.linalg.lstsq(M, vy, rcond=None)
    zoom = (cx[0] + cy[1]) / 2.0            # traza/2: expansión por frame-GAP
    shear = (cx[1] + cy[0]) / 2.0
    resid = float(np.sqrt(np.mean((M @ cx - vx) ** 2 + (M @ cy - vy) ** 2)))
    return {"zoom_per_gap": float(zoom), "pan_x_per_gap": float(cx[2]),
            "pan_y_per_gap": float(cy[2]), "shear_per_gap": float(shear),
            "residual_px": round(resid, 3)}


def measure(path: Path, label: str) -> dict:
    frs = read(path)
    n = len(frs); fps = 30.0
    if n < GAP + 2:
        return {"label": label, "error": "muy corto"}
    idx = [int(i * (n - GAP - 1) / max(N_WIN - 1, 1)) for i in range(N_WIN)]
    rows = [dict(t=round(i / fps, 3), **affine_flow(frs[i], frs[i + GAP])) for i in idx]
    z = np.array([r["zoom_per_gap"] for r in rows])
    # tasa de zoom en %/s: zoom por GAP frames → por frame → por segundo, en % del ancho
    zps = z / GAP * fps * 100.0
    out = {
        "label": label, "frames": n, "ventanas": rows,
        "zoom_pct_per_s_mean": round(float(zps.mean()), 3),
        "zoom_pct_per_s_max": round(float(zps.max()), 3),
        "zoom_pct_per_s_min": round(float(zps.min()), 3),
        "ventanas_expansivas_pct": round(float((z > 0).mean() * 100), 1),
        "pan_px_per_s_mean": round(float(np.mean([np.hypot(r["pan_x_per_gap"], r["pan_y_per_gap"])
                                                  for r in rows]) / GAP * fps), 2),
        "total_zoom_pct_estimado": round(float((np.prod(1 + z / 1.0) ** (1 / len(z)) - 1) * 100 * n / GAP), 2),
    }
    print(f"{label:22} zoom %/s mean={out['zoom_pct_per_s_mean']:+.3f} max={out['zoom_pct_per_s_max']:+.3f} "
          f"min={out['zoom_pct_per_s_min']:+.3f} · ventanas expansivas={out['ventanas_expansivas_pct']}% "
          f"· pan={out['pan_px_per_s_mean']} px/s · residuo={np.mean([r['residual_px'] for r in rows]):.2f}px")
    return out


res = {}
print("== PUSH-IN / PAN MEDIDO EN FRAMES (modelo afín del flujo, ventanas de 10 frames) ==")
res["referencia_type_01"] = measure(REF, "referencia_type_01")
for nm, f in (("reel18", "reel_black_friday_abyss"), ("reel15", "reel_black_friday_abyss_15s"),
              ("story1", "story_1_pre_black_friday"), ("story2", "story_2_categorias"),
              ("story3", "story_3_black_friday_cta")):
    p = OUT / f"{f}_1080x1920_30fps.mp4"
    if p.exists():
        res[nm] = measure(p, nm)
ref = res["referencia_type_01"]
print("\n== COMPARACIÓN DE PUSH-IN vs REFERENCIA ==")
for k, r in res.items():
    if k == "referencia_type_01" or "zoom_pct_per_s_mean" not in r:
        continue
    ratio = r["zoom_pct_per_s_mean"] / ref["zoom_pct_per_s_mean"] if ref["zoom_pct_per_s_mean"] else 0
    print(f"  {k:8} zoom {r['zoom_pct_per_s_mean']:+.3f} %/s vs ref {ref['zoom_pct_per_s_mean']:+.3f} %/s "
          f"→ {ratio:.2f}x · expansivas {r['ventanas_expansivas_pct']}% (ref {ref['ventanas_expansivas_pct']}%)")
(ROOT / "research" / "audit_pushin_report.json").write_text(json.dumps(res, indent=2, ensure_ascii=False))
print("report:", ROOT / "research" / "audit_pushin_report.json")
