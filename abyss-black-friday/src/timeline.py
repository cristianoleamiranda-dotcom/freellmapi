"""Escaletas: 1 reel (18 s) + 3 historias (6 s), 9:16 30 fps.

Estructura espejo de la referencia type_01 (póster cinético):
  plano A (retícula completa, push-in) → whip → plano B (tipografía gigante
  arriba/abajo, foto pequeña al centro) → barrido de glifos → plano C
  (categorías escalonadas) → whip → cierre (BLACK sólido / FRIDAY contorneado,
  firma −9°, CTA).
"""

from __future__ import annotations

import brand as B
from brand import W, H, COPY

ANTON = str(B.ANTON)
MON5 = str(B.MONTSERRAT_500)
MON6 = str(B.MONTSERRAT_600)
MON7 = str(B.MONTSERRAT_700)

CREAM, BONE, COPPER, CHROME, CHAMP = B.CREAM, B.BONE, B.COPPER, B.CHROME, B.CHAMPAGNE


def L(kind, z=0, **kw):
    d = {"kind": kind, "z": z}
    d.update(kw)
    return d


def K(t, **kw):
    d = {"t": t}
    d.update(kw)
    return d


# ---------------------------------------------------------------------------
# Bloques reutilizables
# ---------------------------------------------------------------------------
def micro_lines(x, y, lines, size=25, color=BONE, track=6, z=40, lead=10, align="l",
                in_=-9, out=99):
    anchor = {"l": "left", "c": "center", "r": "right"}[align]
    kw = {"in": in_, "out": out} if (in_ > -9 or out < 99) else {}
    return L("para", z=z, lines=tuple(lines), font=MON5, size=size, color=color,
             track=track, lead=lead, align=align, anchor=anchor, x=x, y=y, **kw)


def roundel(x, y, size, in_, out, keys=None, z=45):
    return L("roundel", z=z, src=str(B.MATERIAL / "brand" / "emblema_abyss_alpha.png"),
             x=x, y=y, **{"in": in_, "out": out},
             keys=keys or [K(in_, s=1.3, a=0.0), K(in_ + 0.5, s=1.0, a=1.0, ease="ob"),
                           K(out - 0.01, s=1.05, a=1.0)])


# ---------------------------------------------------------------------------
# REEL 18 s
# ---------------------------------------------------------------------------
def reel_scenes():
    scenes = []

    # ---- S1 · INTRO 0.00–3.00 (retícula A: foto arriba-izq, type gigante) ----
    s1 = {"t0": -0.30, "t1": 3.00, "layers": [
        # bloque fotográfico: tatuador trabajando (máquina en mano)
        L("photo", z=10, src="artist", x=300, y=470, w=520, h=650,
          cam=[K(0.0, zoom=1.05, cx=0.5, cy=0.50), K(3.0, zoom=1.20, cx=0.52, cy=0.52)],
          keys=[K(0.0, s=0.94, a=0.0), K(0.45, s=1.0, a=1.0, ease="o"), K(3.0, s=1.06, a=1.0)]),
        # tipografía gigante recortada (bleed derecho)
        L("type", z=20, text="ABYSS", font=ANTON, size=470, color=CREAM,
          x=760, y=830, keys=[K(0.0, s=0.90, a=0.0), K(0.6, s=0.97, a=1.0, ease="o"),
                              K(3.0, s=1.10, a=1.0)]),
        L("type", z=21, text="STUDIO", font=ANTON, size=300, color=BONE,
          x=520, y=1230, keys=[K(0.15, s=0.92, a=0.0), K(0.8, s=0.98, a=1.0, ease="o"),
                                K(3.0, s=1.09, a=1.0)]),
        # etiqueta superior derecha (sistema SPATIAL de la referencia)
        L("label", z=30, text="BLACK FRIDAY", font=MON7, size=52, color=CREAM, track=2,
          anchor="left", x=560, y=296, keys=[K(0.3, a=0.0, y=284), K(0.85, a=1.0, y=296, ease="o"), K(3.0, a=1.0)]),
        micro_lines(562, 366, ["CAMPAÑA NOVIEMBRE 2026", "SAN BERNARDO · CHILE",
                              "INK. METAL. SKIN."], size=24, track=5, z=30),
        # rombo de marca + regla cobre
        L("rule", z=31, w=210, h=4, color=COPPER, anchor="left", x=562, y=492,
          keys=[K(0.5, s=0.0, a=0.0), K(1.1, s=1.0, a=1.0, ease="ox")]),
        # identificación de estudio, abajo-izquierda (zona segura)
        L("para", z=32, lines=("ABYSS TATTOO Y PIERCING", "♦ San Bernardo"), font=MON6,
          size=44, color=CREAM, track=3, lead=14, anchor="left", x=96, y=1480,
          keys=[K(0.6, a=0.0, y=1500), K(1.2, a=1.0, y=1480, ease="o"), K(3.0, a=1.0)]),
        micro_lines(96, 1620, ["PRE BLACK FRIDAY 26/11 · BLACK FRIDAY 27/11",
                               "INSCRIPCIÓN POR DM · ELIGE TU PROMOCIÓN"], size=26, track=4, z=32),
        roundel(930, 640, 150, 0.9, 3.0),
        # barrido especular cromo sobre el type gigante
        L("sweep", z=50, w=760, h=240, color=CHROME, x=-300, y=880,
          keys=[K(1.35, x=-320, a=0.0), K(1.75, x=760, a=0.38, ease="q"), K(2.15, x=1500, a=0.0)]),
    ]}
    scenes.append(s1)

    # ---- S2 · PRE BLACK FRIDAY 3.40–7.20 (retícula B) ----
    s2 = {"t0": 3.40, "t1": 7.20, "layers": [
        L("type", z=10, text="PRE BLACK", font=ANTON, size=430, color=CREAM,
          x=520, y=330, keys=[K(3.4, s=0.94, a=0.0), K(3.85, s=1.0, a=1.0, ease="o"),
                              K(7.2, s=1.13, a=1.0)]),
        L("type", z=10, text="FRIDAY", font=ANTON, size=430, color=BONE,
          x=470, y=1560, keys=[K(3.5, s=0.94, a=0.0), K(3.95, s=1.0, a=1.0, ease="o"),
                                K(7.2, s=1.13, a=1.0)]),
        # foto pequeña al centro (tatuaje real pierna) como en la referencia
        L("photo", z=20, src="leg", x=330, y=950, w=430, h=540,
          cam=[K(3.4, zoom=1.06, cx=0.5, cy=0.35), K(7.2, zoom=1.24, cx=0.5, cy=0.45)],
          keys=[K(3.55, s=0.9, a=0.0), K(4.05, s=1.0, a=1.0, ease="ob"), K(7.2, s=1.05, a=1.0)]),
        # copy esencial (zona segura central)
        L("para", z=40, lines=("PRE BLACK FRIDAY ABYSS:", "26/11."), font=ANTON, size=88,
          color=CREAM, track=2, lead=10, x=640, y=880,
          keys=[K(4.0, a=0.0, x=610), K(4.5, a=1.0, x=640, ease="o"), K(7.2, a=1.0)]),
        L("para", z=40, lines=("INSCRIPCIÓN POR DM.", "ELIGE QUE PROMOCIÓN", "QUIERES."),
          font=MON6, size=44, color=CHAMP, track=4, lead=14, x=640, y=1080,
          keys=[K(4.35, a=0.0, x=616), K(4.9, a=1.0, x=640, ease="o"), K(7.2, a=1.0)]),
        L("rule", z=41, w=150, h=4, color=COPPER, x=640, y=1010,
          keys=[K(4.2, s=0.0, a=0.0), K(4.7, s=1.0, a=1.0, ease="ox")]),
        micro_lines(640, 1330, ["ABYSS TATTOO Y PIERCING ♦ SAN BERNARDO"], size=26,
                    track=5, z=40, align="c"),
        # barrido de glifos: "26/11" gigante cruzando (como el sweep de la ref.)
        L("type", z=60, text="26/11", font=ANTON, size=560, color=COPPER,
          x=540, y=960, rot=-9,
          keys=[K(5.55, x=-620, a=0.0, blur=18, s=1.0), K(6.15, x=540, a=0.95, blur=6, ease="q"),
                K(6.75, x=1700, a=0.0, blur=20, s=1.06)]),
    ]}
    scenes.append(s2)

    # ---- S3 · CATEGORÍAS 7.20–13.20 (4 sub-beats escalonados) ----
    cats = [
        ("01", "TATUAJE", "forearm", 7.20, 8.70, dict(x=700, y=700), dict(x=430, y=1240)),
        ("02", "JOYERÍA", "ring_butterfly", 8.70, 10.20, dict(x=380, y=1230), dict(x=700, y=640)),
        ("03", "PERFORACIONES", "ear", 10.20, 11.70, dict(x=720, y=1260), dict(x=420, y=660)),
        ("04", "MÁQUINAS", "machine", 11.70, 13.20, dict(x=360, y=680), dict(x=660, y=1280), "DE TATUAJE"),
    ]
    layers = []
    for row in cats:
        num, word, src, t0, t1, tpos, ppos = row[:7]
        sub = row[7] if len(row) > 7 else None
        wsize = 250 if len(word) > 10 else 330
        layers += [
            L("photo", z=10, src=src, w=470, h=590,
              cam=[K(t0, zoom=1.0, cx=0.5, cy=0.28), K(t1, zoom=1.10, cx=0.52, cy=0.32)],
              keys=[K(t0, s=0.86, a=0.0, **ppos), K(t0 + 0.34, s=1.0, a=1.0, ease="ob", **ppos),
                    K(t1 - 0.12, s=1.04, a=1.0, **ppos), K(t1, s=1.06, a=0.0, **ppos)],
              **{"in": t0, "out": t1}),
            L("type", z=20, text=word, font=ANTON, size=wsize, color=CREAM,
              keys=[K(t0 + 0.06, s=1.22, a=0.0, **tpos), K(t0 + 0.42, s=1.0, a=1.0, ease="ob", **tpos),
                    K(t1 - 0.1, s=1.05, a=1.0, **tpos), K(t1, s=1.08, a=0.0, **tpos)],
              **{"in": t0, "out": t1}),
            L("label", z=30, text=num, font=MON7, size=54, color=COPPER, track=4,
              keys=[K(t0 + 0.18, a=0.0, x=tpos["x"], y=tpos["y"] - wsize * 0.72),
                    K(t0 + 0.5, a=1.0, x=tpos["x"], y=tpos["y"] - wsize * 0.72, ease="o"),
                    K(t1, a=0.0, x=tpos["x"], y=tpos["y"] - wsize * 0.72)],
              **{"in": t0, "out": t1}),
            L("rule", z=31, w=130, h=4, color=COPPER,
              keys=[K(t0 + 0.2, s=0.0, a=0.0, x=tpos["x"], y=tpos["y"] + wsize * 0.62),
                    K(t0 + 0.6, s=1.0, a=1.0, ease="ox", x=tpos["x"], y=tpos["y"] + wsize * 0.62),
                    K(t1, s=1.0, a=0.0, x=tpos["x"], y=tpos["y"] + wsize * 0.62)],
              **{"in": t0, "out": t1}),
        ] + ([L("label", z=22, text=sub, font=ANTON, size=120, color=BONE,
                keys=[K(t0 + 0.14, s=1.15, a=0.0, x=tpos["x"], y=tpos["y"] + wsize * 0.62 + 96),
                      K(t0 + 0.5, s=1.0, a=1.0, ease="ob", x=tpos["x"], y=tpos["y"] + wsize * 0.62 + 96),
                      K(t1 - 0.08, s=1.03, a=1.0, x=tpos["x"], y=tpos["y"] + wsize * 0.62 + 96),
                      K(t1, s=1.05, a=0.0, x=tpos["x"], y=tpos["y"] + wsize * 0.62 + 96)],
                **{"in": t0, "out": t1})] if sub else [])
    layers += [
        L("label", z=35, text="ELIGE QUE PROMOCIÓN QUIERES", font=MON6, size=34,
          color=CHAMP, track=6, x=540, y=1600,
          keys=[K(7.4, a=0.0), K(7.9, a=1.0, ease="o"), K(13.0, a=1.0), K(13.2, a=0.0)]),
        roundel(930, 330, 130, 7.4, 13.2),
    ]
    scenes.append({"t0": 7.20, "t1": 13.20, "layers": layers})

    # ---- S4 · CIERRE 13.60–18.00 ----
    s4 = {"t0": 13.60, "t1": 18.40, "layers": [
        # panel negro superior-izq (cuadro negro de la referencia)
        L("rule", z=5, w=430, h=430, color=B.BLACK, x=215, y=430,
          keys=[K(13.6, s=0.6, a=0.0), K(14.0, s=1.0, a=1.0, ease="o"), K(18.4, s=1.02, a=1.0)]),
        L("sweep", z=6, w=520, h=300, color=CHROME, x=215, y=430,
          keys=[K(14.3, x=-260, a=0.0), K(14.8, x=215, a=0.30, ease="q"), K(15.3, x=700, a=0.0)]),
        # BLACK sólido / FRIDAY contorneado (mecánica aprobada 02-CORTE)
        L("type", z=20, text="BLACK", font=ANTON, size=400, color=CREAM,
          x=640, y=820, keys=[K(13.6, s=0.9, a=0.0), K(14.05, s=1.0, a=1.0, ease="o"),
                              K(18.4, s=1.10, a=1.0)]),
        L("type", z=20, text="FRIDAY", font=ANTON, size=400, color=CREAM, outline=7,
          x=600, y=1180, keys=[K(13.75, s=0.9, a=0.0), K(14.2, s=1.0, a=1.0, ease="o"),
                                K(18.4, s=1.10, a=1.0)]),
        # firma de campaña −9°
        L("type", z=30, text="27/11", font=ANTON, size=200, color=COPPER, rot=-9,
          x=300, y=1318, keys=[K(14.1, s=1.3, a=0.0), K(14.6, s=1.0, a=1.0, ease="ob"),
                                K(18.4, s=1.03, a=1.0)]),
        L("para", z=40, lines=("BLACK FRIDAY ABYSS: 27/11",), font=MON7, size=52,
          color=CREAM, track=4, lead=0, x=540, y=1462, align="c",
          keys=[K(14.4, a=0.0, y=1486), K(14.9, a=1.0, y=1462, ease="o"), K(18.4, a=1.0)]),
        # CTA doble: DM + WhatsApp (caja fina, lenguaje del end-card de marca)
        L("box", z=41, w=760, h=100, color=BONE, stroke=3, x=540, y=1556,
          keys=[K(14.7, s=0.9, a=0.0), K(15.15, s=1.0, a=1.0, ease="ob"), K(18.4, s=1.0, a=1.0)]),
        L("label", z=42, text="DM  @abyss_tattoo_studio", font=MON6, size=40, color=CREAM,
          track=3, x=540, y=1530, keys=[K(14.85, a=0.0), K(15.25, a=1.0, ease="o"), K(18.4, a=1.0)]),
        L("label", z=42, text="WHATSAPP  wa.me/56947786839", font=MON6, size=36, color=CHAMP,
          track=3, x=540, y=1626, keys=[K(15.05, a=0.0), K(15.45, a=1.0, ease="o"), K(18.4, a=1.0)]),
        roundel(540, 430, 210, 14.2, 18.4),
        micro_lines(540, 1664, ["ABYSS TATTOO Y PIERCING ♦ SAN BERNARDO"], size=24,
                    track=6, z=40, align="c"),
    ]}
    scenes.append(s4)

    transitions = [
        {"at": 3.00, "kind": "whip", "dur": 0.40, "dir": 1},
        {"at": 7.20, "kind": "cut"},
        {"at": 13.20, "kind": "whip", "dur": 0.40, "dir": -1},
    ]
    return scenes, transitions, 18.0


# ---------------------------------------------------------------------------
# HISTORIAS 6 s
# ---------------------------------------------------------------------------
def story1():
    """Pre Black Friday · 26/11."""
    a = {"t0": -0.2, "t1": 3.00, "layers": [
        L("photo", z=10, src="leg", x=330, y=560, w=520, h=650,
          cam=[K(0.0, zoom=1.05, cx=0.5, cy=0.38), K(3.0, zoom=1.24, cx=0.5, cy=0.46)],
          keys=[K(0.0, s=0.92, a=0.0), K(0.4, s=1.0, a=1.0, ease="o"), K(3.0, s=1.06, a=1.0)]),
        L("type", z=20, text="PRE", font=ANTON, size=430, color=CREAM,
          x=640, y=1180, keys=[K(0.1, s=0.9, a=0.0), K(0.6, s=1.0, a=1.0, ease="o"),
                                K(3.0, s=1.12, a=1.0)]),
        L("type", z=30, text="26/11", font=ANTON, size=250, color=COPPER, rot=-9,
          x=620, y=1450, keys=[K(0.5, s=1.25, a=0.0), K(1.0, s=1.0, a=1.0, ease="ob"),
                                K(3.0, s=1.04, a=1.0)]),
        L("label", z=32, text="BLACK FRIDAY ABYSS", font=MON7, size=46, color=CREAM,
          track=4, x=540, y=300, keys=[K(0.4, a=0.0), K(0.9, a=1.0, ease="o"), K(3.0, a=1.0)]),
        roundel(900, 430, 130, 0.7, 3.0),
    ]}
    b = {"t0": 3.00, "t1": 6.30, "layers": [
        L("photo", z=10, src="artist", x=540, y=520, w=880, h=620,
          cam=[K(3.0, zoom=1.0, cx=0.5, cy=0.50), K(6.3, zoom=1.12, cx=0.5, cy=0.52)],
          keys=[K(3.0, s=0.94, a=0.0), K(3.35, s=1.0, a=1.0, ease="o"), K(6.3, s=1.05, a=1.0)]),
        L("para", z=40, lines=("PRE BLACK FRIDAY", "ABYSS: 26/11."), font=ANTON, size=104,
          color=CREAM, track=2, lead=8, x=540, y=1080, align="c",
          keys=[K(3.2, a=0.0, y=1110), K(3.65, a=1.0, y=1080, ease="o"), K(6.3, a=1.0)]),
        L("para", z=40, lines=("INSCRIPCIÓN POR DM.", "ELIGE QUE PROMOCIÓN QUIERES."),
          font=MON6, size=46, color=CHAMP, track=4, lead=16, x=540, y=1300, align="c",
          keys=[K(3.5, a=0.0), K(4.0, a=1.0, ease="o"), K(6.3, a=1.0)]),
        L("rule", z=41, w=170, h=4, color=COPPER, x=540, y=1210,
          keys=[K(3.4, s=0.0, a=0.0), K(3.9, s=1.0, a=1.0, ease="ox")]),
        L("label", z=42, text="ABYSS TATTOO Y PIERCING ♦ SAN BERNARDO", font=MON6, size=30,
          color=BONE, track=5, x=540, y=1596,
          keys=[K(3.8, a=0.0), K(4.3, a=1.0, ease="o"), K(6.3, a=1.0)]),
    ]}
    return [a, b], [{"at": 3.00, "kind": "cut"}], 6.0


def story2():
    """Categorías de promoción."""
    layers = []
    cats = [
        ("01", "TATUAJE", "forearm", 0.00, 1.50, dict(x=660, y=760), dict(x=400, y=1300)),
        ("02", "JOYERÍA", "ring_butterfly", 1.50, 3.00, dict(x=400, y=1280), dict(x=680, y=700)),
        ("03", "PERFORACIONES", "ear", 3.00, 4.50, dict(x=680, y=1240), dict(x=400, y=680)),
        ("04", "MÁQUINAS", "machine", 4.50, 6.20, dict(x=400, y=700), dict(x=660, y=1240), "DE TATUAJE"),
    ]
    for row in cats:
        num, word, src, t0, t1, tpos, ppos = row[:7]
        sub = row[7] if len(row) > 7 else None
        wsize = 240 if len(word) > 10 else 320
        layers += [
            L("photo", z=10, src=src, w=520, h=650,
              cam=[K(t0, zoom=1.0, cx=0.5, cy=0.28), K(t1, zoom=1.10, cx=0.52, cy=0.32)],
              keys=[K(t0, s=0.86, a=0.0, **ppos), K(t0 + 0.3, s=1.0, a=1.0, ease="ob", **ppos),
                    K(t1 - 0.1, s=1.05, a=1.0, **ppos), K(t1, s=1.07, a=0.0, **ppos)],
              **{"in": t0, "out": t1}),
            L("type", z=20, text=word, font=ANTON, size=wsize, color=CREAM,
              keys=[K(t0 + 0.05, s=1.2, a=0.0, **tpos), K(t0 + 0.38, s=1.0, a=1.0, ease="ob", **tpos),
                    K(t1 - 0.08, s=1.05, a=1.0, **tpos), K(t1, s=1.08, a=0.0, **tpos)],
              **{"in": t0, "out": t1}),
            L("label", z=30, text=num, font=MON7, size=50, color=COPPER, track=4,
              keys=[K(t0 + 0.16, a=0.0, x=tpos["x"], y=tpos["y"] - wsize * 0.7),
                    K(t0 + 0.45, a=1.0, x=tpos["x"], y=tpos["y"] - wsize * 0.7, ease="o"),
                    K(t1, a=0.0, x=tpos["x"], y=tpos["y"] - wsize * 0.7)],
              **{"in": t0, "out": t1}),
        ] + ([L("label", z=22, text=sub, font=ANTON, size=112, color=BONE,
                keys=[K(t0 + 0.12, s=1.15, a=0.0, x=tpos["x"], y=tpos["y"] + wsize * 0.62 + 92),
                      K(t0 + 0.46, s=1.0, a=1.0, ease="ob", x=tpos["x"], y=tpos["y"] + wsize * 0.62 + 92),
                      K(t1 - 0.06, s=1.03, a=1.0, x=tpos["x"], y=tpos["y"] + wsize * 0.62 + 92),
                      K(t1, s=1.05, a=0.0, x=tpos["x"], y=tpos["y"] + wsize * 0.62 + 92)],
                **{"in": t0, "out": t1})] if sub else [])
    layers += [
        L("label", z=35, text="BLACK FRIDAY ABYSS · PROMOS", font=MON7, size=40,
          color=CREAM, track=5, x=540, y=300,
          keys=[K(0.2, a=0.0), K(0.7, a=1.0, ease="o"), K(6.0, a=1.0), K(6.2, a=0.0)]),
        L("label", z=35, text="ELIGE QUE PROMOCIÓN QUIERES", font=MON6, size=34,
          color=CHAMP, track=6, x=540, y=1648,
          keys=[K(0.4, a=0.0), K(0.9, a=1.0, ease="o"), K(6.0, a=1.0), K(6.2, a=0.0)]),
        roundel(950, 430, 104, 0.5, 6.2),
    ]
    return [{"t0": -0.2, "t1": 6.3, "layers": layers}], [], 6.0


def story3():
    """Black Friday 27/11 + CTA."""
    a = {"t0": -0.2, "t1": 2.80, "layers": [
        L("type", z=20, text="BLACK", font=ANTON, size=420, color=CREAM,
          x=620, y=760, keys=[K(0.0, s=0.9, a=0.0), K(0.45, s=1.0, a=1.0, ease="o"),
                               K(2.8, s=1.12, a=1.0)]),
        L("type", z=20, text="FRIDAY", font=ANTON, size=420, color=CREAM, outline=7,
          x=580, y=1120, keys=[K(0.15, s=0.9, a=0.0), K(0.6, s=1.0, a=1.0, ease="o"),
                                 K(2.8, s=1.12, a=1.0)]),
        L("type", z=30, text="27/11", font=ANTON, size=230, color=COPPER, rot=-9,
          x=330, y=1400, keys=[K(0.55, s=1.3, a=0.0), K(1.05, s=1.0, a=1.0, ease="ob"),
                                 K(2.8, s=1.04, a=1.0)]),
        L("label", z=32, text="ABYSS TATTOO Y PIERCING ♦ SAN BERNARDO", font=MON6, size=32,
          color=BONE, track=5, x=540, y=330,
          keys=[K(0.4, a=0.0), K(0.9, a=1.0, ease="o"), K(2.8, a=1.0)]),
        roundel(880, 480, 140, 0.6, 2.8),
    ]}
    b = {"t0": 2.80, "t1": 6.30, "layers": [
        L("photo", z=10, src="ring_double", x=540, y=560, w=760, h=760,
          cam=[K(2.8, zoom=1.05, cx=0.5, cy=0.5), K(6.3, zoom=1.18, cx=0.5, cy=0.5)],
          keys=[K(2.8, s=0.94, a=0.0), K(3.15, s=1.0, a=1.0, ease="o"), K(6.3, s=1.05, a=1.0)]),
        L("para", z=40, lines=("BLACK FRIDAY", "ABYSS: 27/11"), font=ANTON, size=100,
          color=CREAM, track=2, lead=8, x=540, y=1120, align="c",
          keys=[K(3.0, a=0.0, y=1150), K(3.45, a=1.0, y=1120, ease="o"), K(6.3, a=1.0)]),
        L("box", z=41, w=720, h=96, color=BONE, stroke=3, x=540, y=1330,
          keys=[K(3.4, s=0.9, a=0.0), K(3.8, s=1.0, a=1.0, ease="ob"), K(6.3, s=1.0, a=1.0)]),
        L("label", z=42, text="DM  @abyss_tattoo_studio", font=MON6, size=40, color=CREAM,
          track=3, x=540, y=1306, keys=[K(3.55, a=0.0), K(3.95, a=1.0, ease="o"), K(6.3, a=1.0)]),
        L("label", z=42, text="WHATSAPP  wa.me/56947786839", font=MON6, size=36, color=CHAMP,
          track=3, x=540, y=1408, keys=[K(3.75, a=0.0), K(4.15, a=1.0, ease="o"), K(6.3, a=1.0)]),
        L("label", z=43, text="ABYSS TATTOO Y PIERCING ♦ SAN BERNARDO", font=MON6, size=28,
          color=BONE, track=5, x=540, y=1596,
          keys=[K(4.0, a=0.0), K(4.5, a=1.0, ease="o"), K(6.3, a=1.0)]),
    ]}
    return [a, b], [{"at": 2.80, "kind": "cut"}], 6.0
