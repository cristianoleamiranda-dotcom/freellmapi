"""Auditoría 4a: texto esencial dentro de la zona segura IG (72-1008 x 250-1670)."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import brand as B
import timeline as T
from kinetic import layer_state, visible, text_canvas, para_canvas, img_canvas, _rgba
from brand import SAFE_X0, SAFE_X1, SAFE_Y0, SAFE_Y1

ESSENTIAL = {"label", "para", "box"}   # micro-copy, copys y CTA: nunca pueden salir
DISPLAY_MIN = 200                      # type >= 200 px es display: puede desbordar (gramática)

def _ink(cv):
    """Recorta al bbox de tinta (alpha>8) para no medir el padding del canvas."""
    import numpy as np
    a = np.asarray(cv.getchannel("A") if cv.mode == "RGBA" else cv, dtype=np.uint8)
    ys, xs = np.where(a > 8)
    if len(xs) == 0:
        return cv, 0, 0
    x0, x1 = xs.min(), xs.max() + 1
    y0, y1 = ys.min(), ys.max() + 1
    return cv.crop((x0, y0, x1, y1)), x0, y0


def bbox(layer, t):
    st = layer_state(layer, t)
    kind = layer["kind"]
    if kind == "label":
        cv = text_canvas(layer["text"], str(layer["font"]), int(layer["size"]),
                         _rgba(layer.get("color", B.CREAM)), int(layer.get("track", 0)), 0)
    elif kind == "para":
        cv = para_canvas(tuple(layer["lines"]), str(layer["font"]), int(layer["size"]),
                         _rgba(layer.get("color", B.BONE)), int(layer.get("track", 0)),
                         int(layer.get("lead", 6)), layer.get("align", "l"))
    elif kind == "box":
        w, h = int(layer["w"]), int(layer["h"])
        return st["x"] - w * st["s"] / 2, st["y"] - h * st["s"] / 2, w * st["s"], h * st["s"]
    else:
        return None
    cv, ix, iy = _ink(cv)
    w, h = cv.width * st["s"], cv.height * st["s"]
    anchor = layer.get("anchor", "center")
    if anchor == "left":
        x0 = st["x"] + ix * st["s"]
    elif anchor == "right":
        x0 = st["x"] - w - ix * st["s"]
    else:
        x0 = st["x"] - w / 2
    y0 = st["y"] - h / 2
    return x0, y0, w, h

def audit_scenes(name, scenes, transitions, dur):
    viol = []
    for sc in scenes:
        for ly in sc["layers"]:
            if ly["kind"] not in ESSENTIAL:
                continue
            if ly["kind"] in ("label",) and int(ly.get("size", 0)) >= DISPLAY_MIN:
                continue
            t = ly.get("in", sc["t0"])
            t1 = min(ly.get("out", sc["t1"]), sc["t1"])
            n = 12
            for i in range(n + 1):
                tt = t + (t1 - t) * i / n
                if not visible(ly, tt):
                    continue
                st = layer_state(ly, tt)
                if st["a"] < 0.5:
                    continue
                bb = bbox(ly, tt)
                if bb is None:
                    continue
                x0, y0, w, h = bb
                x1, y1 = x0 + w, y0 + h
                if y0 < SAFE_Y0 - 1 or y1 > SAFE_Y1 + 1 or x0 < SAFE_X0 - 1 or x1 > SAFE_X1 + 1:
                    viol.append({"piece": name, "text": ly.get("text") or ly.get("lines"),
                                 "t": round(tt, 2),
                                 "bbox": [round(x0), round(y0), round(x1), round(y1)],
                                 "overflow": [round(max(0, SAFE_Y0 - y0)), round(max(0, y1 - SAFE_Y1)),
                                              round(max(0, SAFE_X0 - x0)), round(max(0, x1 - SAFE_X1))]})
    return viol

if __name__ == "__main__":
    allv = []
    sc, tr, dur = T.reel_scenes();  allv += audit_scenes("reel18", sc, tr, dur)
    sc, tr, dur = T.story1();       allv += audit_scenes("story1", sc, tr, dur)
    sc, tr, dur = T.story2();       allv += audit_scenes("story2", sc, tr, dur)
    sc, tr, dur = T.story3();       allv += audit_scenes("story3", sc, tr, dur)
    seen = set(); uniq = []
    for v in allv:
        k = (v["piece"], str(v["text"])[:40])
        if k not in seen:
            seen.add(k); uniq.append(v)
    for v in uniq:
        print(f"VIOLACIÓN {v['piece']} t={v['t']}s bbox={v['bbox']} overflow[top,bottom,left,right]={v['overflow']} :: {str(v['text'])[:60]}")
    if not uniq:
        print("SIN VIOLACIONES: todo texto esencial dentro de 72-1008 x 250-1670")
    import json
    (ROOT / "research" / "audit_safezones.json").write_text(json.dumps(uniq, indent=2, ensure_ascii=False))
