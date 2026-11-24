"""Auditoría v2 — verificaciones finas que los auditores anteriores medían mal.

(a) SPECS reales del bitstream H.264 con trace_headers: profile_idc, level_idc,
    chroma_format_idc, bit_depth, aspect_ratio_idc + línea de audio completa.
(b) GRANO en zona de tonos medios: la sigma de alta frecuencia de todo el frame se
    desploma en negros planos (el encoder suaviza el ruido ahí), así que se mide sólo
    sobre píxeles 40<=lum<=210. Criterio: sigma >= 2.0 en el 100% de los frames.
(c) PUSH-IN dentro de la placa: el ajuste afín sobre el frame completo mezcla la placa
    que hace zoom con tipografía/viñeta/scrim estáticos y subestima el zoom ~5x. Aquí se
    mide dentro del bbox de la capa 'photo' con cam keys y se compara con lo que la
    escaleta declara. En la referencia se usan sólo ventanas libres de cortes.

Uso: PYTHONPATH=src python3 src/audit_final_checks.py
"""
from __future__ import annotations
import json, re, subprocess, sys
from pathlib import Path
import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
OUT = ROOT / "out"
FF = str(ROOT / "bin" / "ffmpeg")
PIECES = ["reel_black_friday_abyss", "reel_black_friday_abyss_15s",
          "story_1_pre_black_friday", "story_2_categorias", "story_3_black_friday_cta"]
REF = ROOT.parent / "dropbox" / "type_01_pindown.io_1795195281.mp4"


def bitstream(p: Path) -> dict:
    r = subprocess.run([FF, "-hide_banner", "-i", str(p), "-c", "copy", "-bsf:v",
                        "trace_headers", "-f", "null", "-"], capture_output=True, text=True)
    err = r.stderr
    def first(name):
        # trace_headers imprime "BINARIO = DECIMAL"; nos interesa el decimal
        m = re.search(rf"{name}\s+\S+\s*=\s*(\d+)", err)
        return m.group(1) if m else None
    info = subprocess.run([FF, "-hide_banner", "-i", str(p)], capture_output=True, text=True).stderr
    audio = re.search(r"Audio: (.+)", info)
    return {
        "profile_idc": first("profile_idc"),
        "level_idc": first("level_idc"),
        "chroma_format_idc": first("chroma_format_idc"),
        "bit_depth_luma": first("bit_depth_luma_minus8"),
        "aspect_ratio_idc": first("aspect_ratio_idc"),
        "audio_line": audio.group(1).strip() if audio else None,
        "sar_dar": (re.search(r"\[(SAR [^\]]+)\]", info).group(1)
                    if re.search(r"\[(SAR [^\]]+)\]", info) else "cuadrada implícita (SAR 1:1)"),
    }


print("== (a) BITSTREAM H.264 + AUDIO ==")
bs = {}
for n in PIECES:
    p = OUT / f"{n}_1080x1920_30fps.mp4"
    if not p.exists():
        continue
    b = bitstream(p); bs[n] = b
    level = f"{int(b['level_idc'])/10:.1f}" if b["level_idc"] else "?"
    profile = {"100": "High", "77": "Main", "66": "Baseline"}.get(b["profile_idc"], b["profile_idc"])
    chroma = {"1": "4:2:0"}.get(b["chroma_format_idc"], b["chroma_format_idc"])
    depth = f"{8 + int(b['bit_depth_luma'] or 0)} bits"
    sar = {"1": "1:1 (cuadrada)"}.get(b["aspect_ratio_idc"], b["aspect_ratio_idc"])
    ok = (profile == "High" and level == "4.2" and chroma == "4:2:0" and depth == "8 bits")
    if n.startswith("reel"):
        ok = ok and bool(b["audio_line"]) and "48000 Hz" in b["audio_line"] and "stereo" in b["audio_line"]
    print(f"  {'PASS' if ok else 'FAIL'} {n:32} {profile}@{level} {chroma} {depth} SAR={sar} "
          f"· audio={b['audio_line'] or '—'}")

print("\n== (b) GRANO EN TONOS MEDIOS (40<=lum<=210) ==")
grain = {}
for n in PIECES:
    p = OUT / f"{n}_1080x1920_30fps.mp4"
    if not p.exists():
        continue
    cap = cv2.VideoCapture(str(p)); sig = []; i = 0
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        if i % 5 == 0:
            g = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY).astype(np.float32)
            hp = g - cv2.GaussianBlur(g, (0, 0), 0.8)
            m = (g >= 40) & (g <= 210)
            if m.sum() > 4000:
                sig.append(float(hp[m].std()))
        i += 1
    cap.release()
    s = np.array(sig)
    grain[n] = {"frames": len(s), "min": round(float(s.min()), 3), "mean": round(float(s.mean()), 3),
                "max": round(float(s.max()), 3), "cv": round(float(s.std() / s.mean()), 3),
                "pct_ge_2": round(float((s >= 2.0).mean() * 100), 1)}
    print(f"  {n:32} frames_medidos={len(s):3d} σ min/med/max={s.min():.2f}/{s.mean():.2f}/{s.max():.2f} "
          f"CV={s.std()/s.mean():.2f} · σ>=2.0 en {grain[n]['pct_ge_2']}% de frames")


def affine_zoom(a, b, W=540):
    h = int(round(W * a.shape[0] / a.shape[1]))
    ga = cv2.cvtColor(cv2.resize(a, (W, h), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY)
    gb = cv2.cvtColor(cv2.resize(b, (W, h), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY)
    f = cv2.calcOpticalFlowFarneback(ga, gb, None, 0.5, 3, 21, 3, 7, 1.5, 0)
    ys, xs = np.mgrid[0:h:3, 0:W:3]
    px = (xs - W / 2).astype(np.float32).ravel(); py = (ys - h / 2).astype(np.float32).ravel()
    M = np.stack([px, py, np.ones(px.size)], axis=1)
    cx, *_ = np.linalg.lstsq(M, f[ys, xs, 0].ravel(), rcond=None)
    cy, *_ = np.linalg.lstsq(M, f[ys, xs, 1].ravel(), rcond=None)
    resid = float(np.sqrt(np.mean((M @ cx - f[ys, xs, 0].ravel())**2 + (M @ cy - f[ys, xs, 1].ravel())**2)))
    return (cx[0] + cy[1]) / 2.0, resid


print("\n== (c1) PUSH-IN DE LA REFERENCIA (ventanas libres de cortes) ==")
cap = cv2.VideoCapture(str(REF)); frs = []
while True:
    ok, fr = cap.read()
    if not ok:
        break
    frs.append(fr)
cap.release()
CUTS_REF = [2.733]
ref_rows = []
for i in range(0, len(frs) - 30, 30):
    t0, t1 = i / 30.0, (i + 30) / 30.0
    if any(abs(c - t0) < 1.0 or abs(c - t1) < 1.0 or (t0 < c < t1) for c in CUTS_REF):
        continue
    z, resid = affine_zoom(frs[i], frs[i + 30])
    ref_rows.append({"t0": round(t0, 2), "zoom_pct_s": round(z / 30 * 30 * 100, 3), "resid_px": round(resid, 2)})
for r in ref_rows:
    print(f"  t0={r['t0']:>5}s  zoom={r['zoom_pct_s']:+.3f} %/s  residuo={r['resid_px']} px")
if ref_rows:
    zr = np.array([r["zoom_pct_s"] for r in ref_rows])
    print(f"  → referencia sin cortes: zoom medio {zr.mean():+.3f} %/s · expansivas "
          f"{(zr>0).mean()*100:.0f}% · residuo medio {np.mean([r['resid_px'] for r in ref_rows]):.2f} px")

print("\n== (c2) PUSH-IN DENTRO DE LA PLACA (medido vs declarado en la escaleta) ==")
import timeline as T
plate_rows = []
for label, fn, fname in (("reel18", T.reel_scenes, "reel_black_friday_abyss"),
                         ("story1", T.story1, "story_1_pre_black_friday"),
                         ("story2", T.story2, "story_2_categorias"),
                         ("story3", T.story3, "story_3_black_friday_cta")):
    p = OUT / f"{fname}_1080x1920_30fps.mp4"
    if not p.exists():
        continue
    scenes, tr, dur = fn()
    cap = cv2.VideoCapture(str(p))
    for si, sc in enumerate(scenes):
        for ly in sc["layers"]:
            cam = ly.get("cam")
            if ly["kind"] != "photo" or not cam or len(cam) < 2:
                continue
            t0 = max(sc["t0"] + 0.15, 0.0); t1 = min(sc["t1"], dur) - 0.15
            if t1 - t0 < 0.6:
                continue
            if "x" not in ly or "y" not in ly:
                continue
            w, h = int(ly["w"] * 1.0), int(ly["h"] * 1.0)
            x0 = max(0, int(ly["x"] - w / 2)); y0 = max(0, int(ly["y"] - h / 2))
            x1 = min(1080, x0 + w); y1 = min(1920, y0 + h)
            if x1 - x0 < 120 or y1 - y0 < 120:
                continue
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(t0 * 30)); ok1, fa = cap.read()
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(t1 * 30)); ok2, fb = cap.read()
            if not (ok1 and ok2):
                continue
            dt = int(t1 * 30) - int(t0 * 30)
            z, resid = affine_zoom(fa[y0:y1, x0:x1], fb[y0:y1, x0:x1], W=420)
            measured = z / dt * 30 * 100
            declared = (cam[-1]["zoom"] / cam[0]["zoom"] - 1) / (t1 - t0) * 100
            plate_rows.append({"pieza": label, "escena": si + 1, "t": [round(t0, 2), round(t1, 2)],
                               "zoom_medido_pct_s": round(measured, 3),
                               "zoom_declarado_pct_s": round(declared, 3),
                               "ratio": round(measured / declared, 2) if declared else None,
                               "residuo_px": round(resid, 2)})
            print(f"  {label} S{si+1} t=[{t0:.2f},{t1:.2f}] placa {w}x{h} → zoom medido {measured:+.3f} %/s "
                  f"vs declarado {declared:+.3f} %/s (ratio {plate_rows[-1]['ratio']}) residuo {resid:.2f}px")
    cap.release()

(ROOT / "research" / "audit_final_checks_report.json").write_text(json.dumps(
    {"bitstream": bs, "grano_tonos_medios": grain, "pushin_referencia": ref_rows,
     "pushin_placas": plate_rows}, indent=2, ensure_ascii=False))
print("\nreport:", ROOT / "research" / "audit_final_checks_report.json")
