"""Auditoría 3: copys, fechas, rubros y CTA exactos por pieza."""
from __future__ import annotations
import re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
src = (ROOT / "src" / "timeline.py").read_text()
brand = (ROOT / "src" / "brand.py").read_text()
blob = src + brand

REQUIRED = [
    "BLACK FRIDAY ABYSS TATTOO STUDIO",
    "ABYSS TATTOO Y PIERCING",
    "San Bernardo",
    "PRE BLACK FRIDAY ABYSS:",
    "26/11.",
    "INSCRIPCIÓN POR DM.",
    "ELIGE QUE PROMOCIÓN QUIERES.",
    "TATUAJE", "JOYERÍA", "PERFORACIONES", "MÁQUINAS", "DE TATUAJE",
    "BLACK FRIDAY ABYSS: 27/11",
    "@abyss_tattoo_studio",
    "wa.me/56947786839",
    "♦",
]
missing = [r for r in REQUIRED if r not in blob]
print("COPIAS EN TIMELINE/MARCA:")
for r in REQUIRED:
    print(f"  {'OK  ' if r in blob else 'FALTA'} {r!r}")
# presencia por pieza (escaleta)
import timeline as T
def texts(scenes):
    out = []
    for sc in scenes:
        for ly in sc["layers"]:
            if "text" in ly:
                out.append(ly["text"])
            if "lines" in ly:
                out += list(ly["lines"])
    return " | ".join(out)
pieces = {"reel18": T.reel_scenes()[0], "story1": T.story1()[0],
          "story2": T.story2()[0], "story3": T.story3()[0]}
CHECK = {
    "reel18": ["BLACK FRIDAY", "ABYSS TATTOO Y PIERCING", "San Bernardo", "PRE BLACK FRIDAY ABYSS:", "26/11.",
               "INSCRIPCIÓN POR DM.", "ELIGE QUE PROMOCIÓN", "TATUAJE", "JOYERÍA", "PERFORACIONES",
               "MÁQUINAS", "DE TATUAJE", "BLACK FRIDAY ABYSS: 27/11", "@abyss_tattoo_studio", "wa.me/56947786839"],
    "story1": ["PRE BLACK FRIDAY", "26/11.", "INSCRIPCIÓN POR DM.", "ELIGE QUE PROMOCIÓN QUIERES.", "ABYSS TATTOO Y PIERCING", "SAN BERNARDO"],
    "story2": ["TATUAJE", "JOYERÍA", "PERFORACIONES", "MÁQUINAS", "DE TATUAJE", "ELIGE QUE PROMOCIÓN QUIERES.", "BLACK FRIDAY ABYSS"],
    "story3": ["BLACK FRIDAY", "27/11", "@abyss_tattoo_studio", "wa.me/56947786839", "ABYSS TATTOO Y PIERCING", "SAN BERNARDO"],
}
ok_all = not missing
for name, sc in pieces.items():
    blobp = texts(sc)
    bad = [c for c in CHECK[name] if c not in blobp]
    ok_all = ok_all and not bad
    print(f"{name}: {'OK' if not bad else 'FALTA ' + str(bad)}")
# CTA canonical en docs
docs = (ROOT / "README.md").read_text() + (ROOT / "out" / "visor.html").read_text() + (ROOT / "out" / "manifest.json").read_text()
IG_FULL = "instagram.com/abyss_tattoo_studio"
print(f"URL IG completa en docs/visor/manifest: {'OK' if IG_FULL in docs else 'FALTA (solo handle)'}")
print("RESULT:", "PASS" if ok_all else "REVISAR")
