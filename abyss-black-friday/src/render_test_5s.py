"""Render de prueba ABYSS/Pindown: 5 s, 9:16, 1080x1920, 30 fps.

Usa el pipeline offline existente (Pillow/OpenCV/FFmpeg); no genera ni altera
los originales. Requiere los plates locales que usa src/render.py.
"""
from __future__ import annotations

import render as R
import timeline as T
import brand as B

L, K = T.L, T.K
ANTON = str(B.ANTON)
MON6, MON7 = str(B.MONTSERRAT_600), str(B.MONTSERRAT_700)
CREAM, BONE, COPPER = B.CREAM, B.BONE, B.COPPER

NAME = "abyss_pindown_test_5s"


def scenes_5s():
    # 0.00–2.00 · hook tipográfico, escala agresiva y bleed editorial.
    intro = {"t0": -0.15, "t1": 2.00, "layers": [
        L("type", z=20, text="BLACK", font=ANTON, size=470, color=CREAM,
          x=545, y=710, rot=-4,
          keys=[K(0.00, s=1.28, a=0.0, x=690), K(0.28, s=1.0, a=1.0, x=545, ease="ob"),
                K(1.98, s=1.12, a=1.0, x=510)]),
        L("type", z=21, text="FRIDAY", font=ANTON, size=420, color=BONE, outline=7,
          x=520, y=1110, rot=-4,
          keys=[K(0.18, s=1.24, a=0.0, x=390), K(0.48, s=1.0, a=1.0, x=520, ease="ob"),
                K(1.98, s=1.10, a=1.0, x=560)]),
        L("label", z=30, text="ABYSS TATTOO STUDIO", font=MON7, size=36,
          color=CREAM, track=5, x=540, y=310,
          keys=[K(0.35, a=0.0, y=340), K(0.72, a=1.0, y=310, ease="o"), K(1.98, a=1.0)]),
        L("rule", z=31, w=250, h=4, color=COPPER, x=540, y=1325,
          keys=[K(0.55, s=0.0, a=0.0), K(0.95, s=1.0, a=1.0, ease="ox")]),
        L("label", z=32, text="TATTOO · PIERCING · ART", font=MON6, size=28,
          color=BONE, track=6, x=540, y=1390,
          keys=[K(0.68, a=0.0), K(1.02, a=1.0, ease="o"), K(1.98, a=1.0)]),
    ]}

    # 2.00–4.00 · collage de fotografía real, paneles y desplazamiento.
    photos = {"t0": 2.00, "t1": 4.00, "layers": [
        L("box", z=1, w=1080, h=1920, color=B.OBSIDIAN, x=540, y=960,
          keys=[K(2.0, a=1.0)]),
        L("photo", z=10, src="leg", x=210, y=890, w=330, h=780,
          cam=[K(2.0, zoom=1.04, cx=0.50, cy=0.42), K(4.0, zoom=1.20, cx=0.52, cy=0.48)],
          keys=[K(2.0, s=0.82, a=0.0, x=170), K(2.26, s=1.0, a=1.0, x=210, ease="ob"),
                K(4.0, s=1.08, a=1.0, x=235)]),
        L("photo", z=11, src="forearm", x=550, y=890, w=330, h=780,
          cam=[K(2.0, zoom=1.02, cx=0.50, cy=0.40), K(4.0, zoom=1.18, cx=0.48, cy=0.46)],
          keys=[K(2.12, s=0.84, a=0.0, y=980), K(2.40, s=1.0, a=1.0, y=890, ease="ob"),
                K(4.0, s=1.07, a=1.0, y=870)]),
        L("photo", z=12, src="ear", x=890, y=890, w=330, h=780,
          cam=[K(2.0, zoom=1.02, cx=0.50, cy=0.40), K(4.0, zoom=1.19, cx=0.50, cy=0.48)],
          keys=[K(2.24, s=0.82, a=0.0, x=950), K(2.52, s=1.0, a=1.0, x=890, ease="ob"),
                K(4.0, s=1.08, a=1.0, x=870)]),
        L("box", z=20, w=1080, h=250, color=B.BLACK, x=540, y=330,
          keys=[K(2.0, a=0.0), K(2.28, a=0.82, ease="o")]),
        L("label", z=30, text="REAL WORK. REAL SKIN.", font=MON7, size=34,
          color=CREAM, track=5, x=540, y=330,
          keys=[K(2.24, a=0.0), K(2.58, a=1.0, ease="o"), K(4.0, a=1.0)]),
        L("label", z=31, text="TATUAJE  /  PIERCING  /  JOYERÍA", font=MON6, size=24,
          color=BONE, track=3, x=540, y=1640,
          keys=[K(2.55, a=0.0), K(2.88, a=1.0, ease="o"), K(4.0, a=1.0)]),
    ]}

    # 4.00–5.00 · end card limpio, copy literal.
    end = {"t0": 4.00, "t1": 5.00, "layers": [
        L("type", z=20, text="BLACK FRIDAY", font=ANTON, size=220, color=CREAM,
          x=540, y=790, keys=[K(4.0, s=1.22, a=0.0), K(4.22, s=1.0, a=1.0, ease="ob"),
                               K(5.0, s=1.04, a=1.0)]),
        L("rule", z=30, w=330, h=4, color=COPPER, x=540, y=990,
          keys=[K(4.18, s=0.0, a=0.0), K(4.48, s=1.0, a=1.0, ease="ox")]),
        L("label", z=31, text="ABYSS TATTOO STUDIO", font=MON7, size=38,
          color=BONE, track=5, x=540, y=1080,
          keys=[K(4.30, a=0.0, y=1110), K(4.56, a=1.0, y=1080, ease="o"), K(5.0, a=1.0)]),
    ]}
    return [intro, photos, end], [
        {"at": 2.00, "kind": "cut"},
        {"at": 4.00, "kind": "cut"},
    ], 5.0


def main():
    plates = R.build_plates()
    scenes, transitions, duration = scenes_5s()
    R.POSTERS[NAME] = {"cover_hook": 0.8, "poster_cta": 4.7}
    info = R.render_piece(NAME, scenes, transitions, duration, plates, audio=None)
    R.write_manifest([info], merge=True)
    print(f"\nOK: {R.OUT / info['file']}")
    print(f"Frames: {info['frames']} | Duración: {info['duration']} s | SHA256: {info['sha256_16']}")


if __name__ == "__main__":
    main()
