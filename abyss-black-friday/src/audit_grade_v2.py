"""Auditoría 2 (v2): NO TRANSABLE — material editado, teoría de color y grano.

Evidencia empírica sobre los frames ENTREGADOS (no sobre el código):
  · grano en CADA frame: σ del residuo de alta frecuencia por frame (min/media/max/CV).
  · edición vs material crudo: mismos medidores sobre las placas fuente sin procesar
    (material/film/*.mp4) y sobre los renders → delta de negros, saturación y contraste.
  · teoría de color: histograma de tonos de los píxeles saturados; % en tonos PROHIBIDOS
    por el manual de marca (amarillo/rojo retail, neón, magenta) y % en cobre/crema.
Salida: research/audit_grade_v2_report.json
"""
from __future__ import annotations
import json
from pathlib import Path
import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
MAT = ROOT / "material"
PIECES = ["reel_black_friday_abyss", "reel_black_friday_abyss_15s",
          "story_1_pre_black_friday", "story_2_categorias", "story_3_black_friday_cta"]
RAW = ["film/hero_film.mp4", "film/proceso_filmacion.mp4", "film/proceso_detalle.mp4",
       "film/proceso_pierna.mp4", "film/loop_film.mp4"]
STEP = 6  # muestreo: cada 6º frame


def metrics(frame_bgr) -> dict:
    g = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32)
    hp = g - cv2.GaussianBlur(g, (0, 0), 0.8)          # residuo alta frecuencia = grano
    hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
    h, s, v = hsv[..., 0].astype(np.float32), hsv[..., 1], hsv[..., 2]
    sat = s > 90
    sel = sat & (v > 40)
    hues = h[sel]
    def pct(a, b):
        if hues.size == 0:
            return 0.0
        if a <= b:
            m = (hues >= a) & (hues <= b)
        else:
            m = (hues >= a) | (hues <= b)
        return round(float(m.mean() * 100), 2)
    return {
        "grain_sigma": round(float(hp.std()), 3),
        "black_p1": round(float(np.percentile(g, 1)), 2),
        "white_p99": round(float(np.percentile(g, 99.9)), 2),
        "lum_mean": round(float(g.mean()), 2),
        "lum_std": round(float(g.std()), 2),
        "sat_mean": round(float(s.mean()), 2),
        "sat_pixels_pct": round(float(sel.mean() * 100), 2),
        "hue_copper_5_20": pct(5, 20),          # cobre/ámbar cálido (marca)
        "hue_cream_20_35": pct(20, 35),         # hueso/crema (marca)
        "hue_yellow_retail_25_40": pct(25, 40), # amarillo retail (PROHIBIDO)
        "hue_red_retail": pct(0, 4) + pct(170, 179),  # rojo retail saturado (PROHIBIDO)
        "hue_neon_green_cyan_40_100": pct(40, 100),   # neón/cyberpunk (PROHIBIDO)
        "hue_magenta_140_170": pct(140, 170),         # magenta/rosa (PROHIBIDO)
    }


def series(path: Path, step: int = STEP, cap_frames: int = 400) -> dict:
    cap = cv2.VideoCapture(str(path)); rows = []; i = 0
    while len(rows) < cap_frames:
        ok, fr = cap.read()
        if not ok:
            break
        if i % step == 0:
            rows.append(metrics(fr))
        i += 1
    cap.release()
    keys = rows[0].keys()
    agg = {k: {"min": round(float(min(r[k] for r in rows)), 3),
               "mean": round(float(np.mean([r[k] for r in rows])), 3),
               "max": round(float(max(r[k] for r in rows)), 3)} for k in keys}
    gs = np.array([r["grain_sigma"] for r in rows])
    agg["grain_cv"] = round(float(gs.std() / gs.mean()), 3)
    agg["frames_muestreados"] = len(rows)
    agg["frames_con_grano_pct"] = round(float((gs > 2.0).mean() * 100), 1)
    return agg


res = {}
print("== PLACAS FUENTE SIN EDITAR (material crudo) ==")
raw_all = []
for r in RAW:
    p = MAT / r
    if not p.exists():
        continue
    a = series(p, step=10, cap_frames=60); res[f"RAW {r}"] = a; raw_all.append(a)
    print(f"  {r:28} grainσ={a['grain_sigma']['mean']:>6} negros_p1={a['black_p1']['mean']:>6} "
          f"sat={a['sat_mean']['mean']:>6} lum_std={a['lum_std']['mean']:>6}")
print("\n== PIEZAS ENTREGADAS ==")
ren_all = []
for n in PIECES:
    p = OUT / f"{n}_1080x1920_30fps.mp4"
    if not p.exists():
        continue
    a = series(p); res[n] = a; ren_all.append(a)
    print(f"  {n:32} grainσ min/med/max={a['grain_sigma']['min']}/{a['grain_sigma']['mean']}/"
          f"{a['grain_sigma']['max']} CV={a['grain_cv']} frames_con_grano={a['frames_con_grano_pct']}%")
    print(f"      negros_p1={a['black_p1']['mean']} blancos_p99={a['white_p99']['mean']} "
          f"sat={a['sat_mean']['mean']} lum_std={a['lum_std']['mean']} · cobre={a['hue_copper_5_20']['mean']}% "
          f"crema={a['hue_cream_20_35']['mean']}% · PROHIBIDOS: amarillo={a['hue_yellow_retail_25_40']['mean']}% "
          f"rojo={a['hue_red_retail']['mean']}% neón={a['hue_neon_green_cyan_40_100']['mean']}% magenta={a['hue_magenta_140_170']['mean']}%")

if raw_all and ren_all:
    rb = float(np.mean([a["black_p1"]["mean"] for a in raw_all]))
    rn = float(np.mean([a["black_p1"]["mean"] for a in ren_all]))
    rs = float(np.mean([a["sat_mean"]["mean"] for a in raw_all]))
    ns = float(np.mean([a["sat_mean"]["mean"] for a in ren_all]))
    rc = float(np.mean([a["lum_std"]["mean"] for a in raw_all]))
    nc = float(np.mean([a["lum_std"]["mean"] for a in ren_all]))
    print(f"\nΔ crudo→entrega: negros p1 {rb:.1f}→{rn:.1f} ({rn-rb:+.1f}) · saturación {rs:.1f}→{ns:.1f} "
          f"({ns-rs:+.1f}) · contraste lum_std {rc:.1f}→{nc:.1f} ({nc-rc:+.1f})")
    grain_min = min(a["grain_sigma"]["min"] for a in ren_all)
    grain_cv = max(a["grain_cv"] for a in ren_all)
    proib = max(max(a["hue_yellow_retail_25_40"]["mean"], a["hue_red_retail"]["mean"],
                    a["hue_neon_green_cyan_40_100"]["mean"], a["hue_magenta_140_170"]["mean"])
                for a in ren_all)
    ver = ("PASS" if grain_min > 2.0 and grain_cv < 0.5 and proib < 12.0
           and abs(rn - rb) > 1.0 else "WARN")
    print(f"VEREDICTO 2: {ver} (grano_min_σ={grain_min}, CV_max={grain_cv}, "
          f"tono_prohibido_max={proib}%, edición_negros_Δ={rn-rb:+.1f})")
    res["_verdict"] = {"verdict": ver, "grain_min_sigma": grain_min, "grain_cv_max": grain_cv,
                       "prohibited_hue_max_pct": proib, "black_shift": round(rn - rb, 2),
                       "sat_shift": round(ns - rs, 2), "contrast_shift": round(nc - rc, 2)}
(ROOT / "research" / "audit_grade_v2_report.json").write_text(json.dumps(res, indent=2, ensure_ascii=False))
print("report:", ROOT / "research" / "audit_grade_v2_report.json")
