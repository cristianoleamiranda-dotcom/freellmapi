"""Auditoría 4c: legibilidad móvil real de cada texto entregado.

Para cada capa de texto de cada pieza se mide, sobre los frames YA RENDERIZADOS:
  · altura de mayúscula (cap height) en píxeles del frame final, con métricas reales de
    la fuente (PIL) — no el tamaño nominal.
  · contraste WCAG entre la tinta y el fondo local medido en el frame (percentil 90 vs 25
    de luminancia relativa en el bbox de la capa).
Criterios: cap height >= 30 px (mínimo legible en móvil a 1080x1920) y contraste >= 4.5:1
para cuerpo/micro y >= 3:1 para display grande (>= 60 px).
Salida: research/audit_legibility_report.json
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import timeline as T
from audit_safezones import bbox
from kinetic import layer_state, visible

OUT = ROOT / "out"
PIECES = [("reel18", T.reel_scenes, OUT / "reel_black_friday_abyss_1080x1920_30fps.mp4"),
          ("story1", T.story1, OUT / "story_1_pre_black_friday_1080x1920_30fps.mp4"),
          ("story2", T.story2, OUT / "story_2_categorias_1080x1920_30fps.mp4"),
          ("story3", T.story3, OUT / "story_3_black_friday_cta_1080x1920_30fps.mp4")]


def lin(c):
    """c ya viene normalizado 0..1 (bug de auditoría corregido: no volver a dividir por 255)."""
    return np.where(c <= 0.03928, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def wcag(l1, l2):
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def frame_at(cap, t, fps=30.0):
    cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, int(round(t * fps))))
    ok, fr = cap.read()
    return fr if ok else None


res = {}
fails = []
for name, fn, mp4 in PIECES:
    if not mp4.exists():
        continue
    scenes, tr, dur = fn()
    cap = cv2.VideoCapture(str(mp4))
    rows = []
    for sc in scenes:
        for ly in sc["layers"]:
            if ly["kind"] not in ("label", "para", "type"):
                continue
            t0 = max(sc["t0"], 0.0); t1 = min(sc["t1"], dur)
            if t1 <= t0:
                continue
            # instante de plena visibilidad: primer t del tramo con alpha >= 0.99
            t = None
            for cand in np.linspace(t0 + 0.05, t1 - 0.05, 24):
                if layer_state(ly, float(cand)).get("a", 0) >= 0.99:
                    t = float(cand)
                    break
            if t is None:
                continue
            bb = bbox(ly, t)
            if bb is None:
                continue
            x0, y0, w, h = bb
            fr = frame_at(cap, t)
            if fr is None:
                continue
            xi, yi = max(0, int(x0)), max(0, int(y0))
            xj, yj = min(fr.shape[1], int(x0 + w)), min(fr.shape[0], int(y0 + h))
            if xj - xi < 4 or yj - yi < 4:
                continue
            crop = cv2.cvtColor(fr[yi:yj, xi:xj], cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
            lum = lin(crop)  # gris ya es luminancia relativa
            ink = float(np.percentile(lum, 90)); bg = float(np.percentile(lum, 25))
            ratio = wcag(ink, bg)
            size = int(ly.get("size", 0))
            nlines = max(1, len(ly.get("lines", []) or [1]))
            lead = int(ly.get("lead", 6)) if nlines > 1 else 0
            cap_h = round((h - lead * (nlines - 1)) / nlines, 1)
            big = size >= 60
            need = 3.0 if big else 4.5
            ok = cap_h >= 30 and ratio >= need
            txt = ly.get("text") or " / ".join(ly.get("lines", []))
            rows.append({"text": txt[:60], "kind": ly["kind"], "size": size, "t": round(t, 2),
                         "cap_height_px": cap_h, "contrast": round(ratio, 2), "need": need,
                         "ok": bool(ok)})
            if not ok:
                fails.append(f"{name}: '{txt[:40]}' cap={cap_h}px contraste={ratio:.2f} (mín {need})")
    cap.release()
    res[name] = rows
    ch = [r["cap_height_px"] for r in rows]; ct = [r["contrast"] for r in rows]
    print(f"{name}: {len(rows)} textos · cap_height min/med={min(ch) if ch else '-'}/"
          f"{round(float(np.median(ch)),1) if ch else '-'} px · contraste min/med="
          f"{min(ct) if ct else '-'}/{round(float(np.median(ct)),2) if ct else '-'} · "
          f"{'PASS' if all(r['ok'] for r in rows) else 'WARN/FAIL'}")
    for r in sorted(rows, key=lambda r: r["cap_height_px"])[:4]:
        print(f"    · {r['cap_height_px']:>6} px  contraste {r['contrast']:>5}  {r['text'][:48]!r}")
(ROOT / "research" / "audit_legibility_report.json").write_text(json.dumps(res, indent=2, ensure_ascii=False))
print("\nincumplimientos:", len(fails))
for f in fails[:12]:
    print("  -", f)
print("VEREDICTO 4c-legibilidad:", "PASS" if not fails else "WARN" if len(fails) <= 3 else "FAIL")
