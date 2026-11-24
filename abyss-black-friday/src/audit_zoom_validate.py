"""Auditoría 1c: push-in verificado de forma determinista.

Medir zoom por flujo óptico sobre los frames entregados está contaminado por dos cosas:
las placas son VIDEO (el sujeto se mueve dentro del encuadre) y el frame lleva tipografía,
scrim, viñeta y grano estáticos que no hacen zoom. Por eso aquí se hace otra cosa:

  (1) se lee la curva de zoom REAL que aplica el renderer (sample_keys sobre las cam keys
      de cada capa photo de la escaleta entregada) → zoom inicial/final y %/s por escena;
  (2) se valida empíricamente la implementación con un experimento controlado: se renderiza
      una placa ESTÁTICA con las mismas cam keys y se mide el zoom por búsqueda de escala
      con matchTemplate (0.90x–1.35x, paso 0.25%). Si lo medido coincide con lo declarado,
      el push-in de las piezas entregadas es real (mismo código, mismas claves).

Uso: PYTHONPATH=src python3 src/audit_zoom_validate.py
"""
from __future__ import annotations
import sys
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import timeline as T
from kinetic import sample_keys, render_scene
import media as M

print("== (1) CURVA DE ZOOM APLICADA POR EL RENDERER (escaleta entregada) ==")
for label, fn, dur_override in (("reel18", T.reel_scenes, 18.0), ("story1", T.story1, 6.0),
                                ("story2", T.story2, 6.0), ("story3", T.story3, 6.0)):
    scenes, tr, dur = fn()
    for si, sc in enumerate(scenes):
        for ly in sc["layers"]:
            cam = ly.get("cam")
            if ly["kind"] != "photo" or not cam:
                continue
            t0 = max(sc["t0"], 0.0); t1 = min(sc["t1"], dur)
            zs = [sample_keys(cam, t)[0] for t in np.linspace(t0, t1 - 0.01, 12)]
            pct_s = (zs[-1] / zs[0] - 1) / max(t1 - t0 - 0.01, 0.1) * 100
            print(f"  {label} S{si+1} t=[{t0:5.2f},{t1:5.2f}] zoom {zs[0]:.3f}→{zs[-1]:.3f} "
                  f"= {pct_s:+.2f} %/s (total {(zs[-1]/zs[0]-1)*100:+.1f}%)")

print("\n== (2) VALIDACIÓN EMPÍRICA CON PLACA ESTÁTICA (matchTemplate multi-escala) ==")
plate = np.asarray(Image.open(ROOT / "material" / "brand" / "skull_mark_crema.png").convert("RGB"))
plate = cv2.resize(plate, (900, 1200))
layer = {"kind": "photo", "src": "test", "x": 540, "y": 960, "w": 700, "h": 900,
         "cam": [{"t": 0.0, "zoom": 1.05, "cx": 0.5, "cy": 0.5},
                 {"t": 3.0, "zoom": 1.20, "cx": 0.52, "cy": 0.52}],
         "keys": [{"t": 0.0, "s": 1.0, "a": 1.0}]}
scene = {"t0": 0.0, "t1": 3.0, "layers": [layer]}
plates = {"test": plate}


def frame_at(t):
    return np.asarray(render_scene(scene, t, plates, int(t * 30)).convert("RGB"))[:, :, ::-1]


def best_scale(a, b, lo=0.90, hi=1.40, step=0.0025, tpl=300, search=820):
    """Plantilla central de `a` (t0) buscada en `b` (t1) a varias escalas.

    La escala que maximiza TM_CCOEFF_NORMED es el zoom aplicado al contenido entre t0 y t1.
    """
    ha, wa = a.shape[:2]
    ga = cv2.cvtColor(a[ha//2 - tpl//2: ha//2 + tpl//2, wa//2 - tpl//2: wa//2 + tpl//2],
                      cv2.COLOR_BGR2GRAY)
    hb, wb = b.shape[:2]
    gb = cv2.cvtColor(b[hb//2 - search//2: hb//2 + search//2,
                        wb//2 - search//2: wb//2 + search//2], cv2.COLOR_BGR2GRAY)
    best = (None, -1.0)
    s = lo
    while s <= hi:
        nh, nw = max(8, int(ga.shape[0] * s)), max(8, int(ga.shape[1] * s))
        if nh >= gb.shape[0] or nw >= gb.shape[1]:
            s += step
            continue
        sc = cv2.resize(ga, (nw, nh), interpolation=cv2.INTER_AREA)
        r = cv2.matchTemplate(gb, sc, cv2.TM_CCOEFF_NORMED)
        v = float(r.max())
        if v > best[1]:
            best = (s, v)
        s += step
    return best


f0, f1 = frame_at(0.05), frame_at(2.95)
s_meas, score = best_scale(f0, f1)
declared = sample_keys(layer["cam"], 2.95)[0] / sample_keys(layer["cam"], 0.05)[0]
print(f"  zoom declarado por las cam keys: {declared:.4f}x ({(declared-1)*100:+.2f}%)")
print(f"  zoom medido en el frame renderizado: {s_meas:.4f}x ({(s_meas-1)*100:+.2f}%) · score={score:.3f}")
err = abs(s_meas - declared) / declared * 100
print(f"  error relativo: {err:.2f}%  → {'PASS (renderer aplica el push-in declarado)' if err < 6 else 'FAIL'}")
print(f"  equivalente en la pieza: {(declared**(1/2.9)-1)*100:+.2f} %/s sostenidos durante la escena")
