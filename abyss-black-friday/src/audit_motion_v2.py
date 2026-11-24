"""Auditoría de movimiento v2 (segunda pasada, método independiente).

Corrige dos defectos metodológicos de analyze_reference.py / audit_motion.py:
  1. Aquéllos redimensionaban TODO a 180x225 (aspecto 4:5 de la referencia), así que los
     renders 9:16 se aplastaban y las magnitudes de flujo no eran comparables.
  2. La detección de cortes usaba un umbral fijo sobre MAD a esa escala mínima y perdía
     eventos (la referencia tiene un segundo evento cinemático fuerte en t≈4.8 s).

Aquí: ancho común de análisis preservando el aspecto de cada fuente, magnitudes de flujo
NORMALIZADAS al ancho (fracción de ancho por frame, adimensional), cortes por correlación
de histograma + salto robusto de MAD, whips por pico de flujo sostenido con caída de
nitidez (varianza del Laplaciano = motion blur), y push-in por DIVERGENCIA del campo de
flujo (no por heurística de zoom). Compara además las curvas en tiempo normalizado
(t/duración) con correlación de Pearson, que es lo único comparable entre una referencia
de 12.033 s y piezas de 18/15/6 s.

Uso: PYTHONPATH=src python3 src/audit_motion_v2.py
Salida: research/audit_motion_v2_report.json
"""
from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
REF = ROOT.parent / "dropbox" / "type_01_pindown.io_1795195281.mp4"
ANALYSIS_W = 270  # ancho común de análisis; el aspecto de cada fuente se preserva

PIECES = {
    "referencia_type_01": REF,
    "reel18": OUT / "reel_black_friday_abyss_1080x1920_30fps.mp4",
    "reel15": OUT / "reel_black_friday_abyss_15s_1080x1920_30fps.mp4",
    "story1": OUT / "story_1_pre_black_friday_1080x1920_30fps.mp4",
    "story2": OUT / "story_2_categorias_1080x1920_30fps.mp4",
    "story3": OUT / "story_3_black_friday_cta_1080x1920_30fps.mp4",
}


def _robust(v: np.ndarray) -> tuple[float, float]:
    med = float(np.median(v))
    mad = float(np.median(np.abs(v - med))) * 1.4826 or 1e-6
    return med, mad


def analyze(path: Path, label: str) -> dict:
    cap = cv2.VideoCapture(str(path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    w_src, h_src = int(cap.get(3)), int(cap.get(4))
    h = max(2, int(round(ANALYSIS_W * h_src / w_src)))
    prev = None
    rows = []
    n = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        n += 1
        g = cv2.cvtColor(cv2.resize(frame, (ANALYSIS_W, h), interpolation=cv2.INTER_AREA),
                         cv2.COLOR_BGR2GRAY)
        rec = {"t": round((n - 1) / fps, 4)}
        if prev is not None:
            flow = cv2.calcOpticalFlowFarneback(
                prev, g, None, 0.5, 3, 15, 3, 5, 1.2, 0)
            mag = np.hypot(flow[..., 0], flow[..., 1])
            div = np.gradient(flow[..., 0], axis=1) + np.gradient(flow[..., 1], axis=0)
            hist = cv2.calcHist([g], [0], None, [32], [0, 256])
            cv2.normalize(hist, hist)
            phist = cv2.calcHist([prev], [0], None, [32], [0, 256])
            cv2.normalize(phist, phist)
            rec.update(
                flow=float(mag.mean()) / ANALYSIS_W,          # fracción de ancho / frame
                flow_p95=float(np.percentile(mag, 95)) / ANALYSIS_W,
                div=float(div.mean()) / ANALYSIS_W,           # >0 = expansión (push-in)
                mad=float(np.mean(cv2.absdiff(g, prev))) / 255.0,
                hist=float(cv2.compareHist(phist, hist, cv2.HISTCMP_INTERSECT)),
            )
        rec["sharp"] = float(cv2.Laplacian(g, cv2.CV_32F).var())
        rows.append(rec)
        prev = g
    cap.release()

    f = np.array([r.get("flow", np.nan) for r in rows], dtype=float)
    d = np.array([r.get("div", np.nan) for r in rows], dtype=float)
    mad = np.array([r.get("mad", np.nan) for r in rows], dtype=float)
    hist = np.array([r.get("hist", np.nan) for r in rows], dtype=float)
    sharp = np.array([r["sharp"] for r in rows], dtype=float)
    fm, fs = _robust(f[~np.isnan(f)])
    mm, ms = _robust(mad[~np.isnan(mad)])
    sm = float(np.median(sharp))

    cuts, whips = [], []
    for i, r in enumerate(rows):
        if "flow" not in r:
            continue
        t = r["t"]
        if r["hist"] < 0.62 and r["mad"] > mm + 3.0 * ms:
            cuts.append(round(t, 3))
        elif r["flow"] > fm + 4.0 * fs and r["sharp"] < 0.78 * sm:
            whips.append(round(t, 3))

    def merge(ts: list[float], gap: float = 0.25) -> list[list[float]]:
        groups: list[list[float]] = []
        for t in ts:
            if groups and t - groups[-1][-1] <= gap:
                groups[-1].append(t)
            else:
                groups.append([t])
        return groups

    cut_g, whip_g = merge(cuts), merge(whips)
    div_ok = d[~np.isnan(d)]
    dur = n / fps
    curve = np.interp(np.linspace(0, 1, 128), np.linspace(0, 1, len(f)),
                      np.nan_to_num(f, nan=fm))
    return {
        "label": label, "file": str(path), "source_size": f"{w_src}x{h_src}",
        "aspect": round(w_src / h_src, 4), "frames_decoded": n, "fps": round(fps, 3),
        "duration": round(dur, 3),
        "flow_mean_norm": round(float(np.nanmean(f)), 5),
        "flow_peak_norm": round(float(np.nanmax(f)), 5),
        "flow_peak_t": round(float(np.nanargmax(f) + 1) / fps, 3),
        "cuts_raw": cuts, "cuts": [round(float(np.mean(g)), 3) for g in cut_g],
        "cut_groups": [[g[0], g[-1]] for g in cut_g],
        "whips_raw": whips, "whips": [round(float(np.mean(g)), 3) for g in whip_g],
        "whip_groups": [[g[0], g[-1]] for g in whip_g],
        "pushin_div_mean": round(float(np.mean(div_ok)), 6),
        "pushin_frames_positive_pct": round(float((div_ok > 0).mean() * 100), 1),
        "sharp_median": round(sm, 1),
        "curve_norm_time": [round(float(x), 6) for x in curve],
    }


def pearson(a: np.ndarray, b: np.ndarray) -> float:
    if a.std() < 1e-9 or b.std() < 1e-9:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


def main() -> None:
    res = {k: analyze(p, k) for k, p in PIECES.items() if p.exists()}
    ref = res.get("referencia_type_01")
    print("== AUDITORÍA DE MOVIMIENTO v2 (magnitudes normalizadas al ancho) ==")
    for k, r in res.items():
        print(f"\n{k}: {r['source_size']} (aspect {r['aspect']}) · {r['frames_decoded']}f "
              f"@{r['fps']}fps · {r['duration']}s")
        print(f"  flow_norm mean={r['flow_mean_norm']} peak={r['flow_peak_norm']} "
              f"@t={r['flow_peak_t']}s")
        print(f"  cortes={r['cuts']} (grupos {r['cut_groups']})")
        print(f"  whips/blurs={r['whips']} (grupos {r['whip_groups']})")
        print(f"  push-in: div_mean={r['pushin_div_mean']} frames_expansión="
              f"{r['pushin_frames_positive_pct']}%")

    if ref:
        rc = np.array(ref["curve_norm_time"])
        print("\n== COMPARACIÓN CON LA REFERENCIA (tiempo normalizado t/duración) ==")
        print(f"  eventos de la referencia en t/dur: "
              f"cortes={[round(c / ref['duration'], 3) for c in ref['cuts']]} "
              f"whips={[round(w / ref['duration'], 3) for w in ref['whips']]}")
        for k, r in res.items():
            if k == "referencia_type_01":
                continue
            c = np.array(r["curve_norm_time"])
            print(f"  {k:8} Pearson(curva flujo vs ref)={pearson(rc, c):+.3f} · "
                  f"cortes(t/dur)={[round(x / r['duration'], 3) for x in r['cuts']]} · "
                  f"whips(t/dur)={[round(x / r['duration'], 3) for x in r['whips']]} · "
                  f"flow_mean ratio vs ref={r['flow_mean_norm'] / ref['flow_mean_norm']:.2f}x")

    (ROOT / "research" / "audit_motion_v2_report.json").write_text(
        json.dumps(res, indent=2, ensure_ascii=False))
    print("\nreport:", ROOT / "research" / "audit_motion_v2_report.json")


if __name__ == "__main__":
    main()
