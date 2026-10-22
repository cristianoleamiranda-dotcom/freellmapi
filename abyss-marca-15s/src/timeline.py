"""Línea de tiempo · pieza de marca Abyss (15.00 s, 9:16, 100 BPM).

Todo el montaje vive aquí: si hay que cambiar el guion, se cambian estas
estructuras y `render.py` no se toca.

Rejilla: 100 BPM -> 0.6 s por negra -> 25 negras = 15.0 s.
Material: repo `cristianoleamiranda-dotcom/abysstattoo` (ver src/fetch_material.py).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from brand import (
    CINZEL_700,
    CINZEL_800,
    CREAM,
    HUESO,
    MONTSERRAT_500,
    MONTSERRAT_600,
    REPO,
    TEAL,
)

BEAT = 0.6
TOTAL = 15.0

# Momentos clave, compartidos con audio.py
EMBLEM_IN = 11.4          # el logo entra en la negra 19
BELL = EMBLEM_IN + 0.35
RISER = (10.80, EMBLEM_IN)
CUTS = [1.8, 3.0, 4.2, 5.4, 6.3, 7.2, 8.1, 9.0, 9.9, 10.8, EMBLEM_IN]
KICKS = [round(i * BEAT, 3) for i in range(25)]
ACCENTS = [1.8, 3.0, 4.2, 9.0, EMBLEM_IN]

EMBLEM = "assets/reel_plates/emblema_abyss_alpha.png"
EMBLEM_CY = 720
EMBLEM_SIZE = 880
# el arte visible ocupa el 87.5 % del lienzo del PNG (bbox medido sobre el alfa)
EMBLEM_VISIBLE_R = EMBLEM_SIZE * 0.4375
RING_R = int(EMBLEM_VISIBLE_R) + 18


@dataclass
class Key:
    t: float
    zoom: float
    cx: float = 0.5
    cy: float = 0.5
    rot: float = 0.0


@dataclass
class Text:
    value: str
    font: Path
    size: int
    color: str
    x: int
    y: int
    t_in: float
    t_out: float
    tracking: float = 0.0
    mode: str = "rise"        # rise | scale | wipe | fade
    enter: float = 0.36
    exit: float = 0.22
    clip: bool = False
    anchor: str = "left"      # left | center


@dataclass
class Shot:
    kind: str                 # video | image | emblem
    source: str
    start: float
    end: float
    keys: list[Key]
    src_start: float = 0.0
    src_speed: float = 1.0
    shake: float = 0.0
    wide: bool = False        # plate a altura fija: permite panear en apaisado
    exposure: float = 1.0
    label: str = ""
    grade: dict = field(default_factory=dict)


def P(name: str) -> str:
    return str(REPO / name)


SHOTS: list[Shot] = [
    # ---- ACTO 1 · gancho (0.0-3.0): manos trabajando y macro de aguja
    Shot("video", P("film/hero_film.mp4"), 0.0, 1.8, src_start=0.12, src_speed=0.55,
         shake=0.4, label="S1 artista trabajando",
         keys=[Key(0.0, 1.06, 0.50, 0.42), Key(1.8, 1.19, 0.50, 0.40)]),
    Shot("video", P("film/hero_film.mp4"), 1.8, 3.0, src_start=2.45, src_speed=0.60,
         label="S2 macro aguja", exposure=1.22,
         keys=[Key(0.0, 1.16, 0.50, 0.44), Key(1.2, 1.03, 0.50, 0.46)]),

    # ---- ACTO 2 · proceso (3.0-5.4): guantes, tinta, filmación
    Shot("video", P("film/proceso_detalle.mp4"), 3.0, 4.2, src_start=1.20, src_speed=0.85,
         label="S3 detalle guantes", exposure=0.94,
         keys=[Key(0.0, 1.10, 0.50, 0.54), Key(1.2, 1.02, 0.50, 0.52)]),
    Shot("video", P("film/proceso_filmacion.mp4"), 4.2, 5.4, src_start=2.60, src_speed=0.80,
         label="S4 registro en estudio",
         keys=[Key(0.0, 1.04, 0.50, 0.46), Key(1.2, 1.15, 0.52, 0.48)]),

    # ---- ACTO 3 · obra (5.4-9.0): cuatro cortes rápidos
    Shot("image", P("assets/trabajos/trabajo_hombro_real.jpg"), 5.4, 6.3,
         label="S5 hombro realismo",
         keys=[Key(0.0, 1.20, 0.50, 0.46), Key(0.9, 1.07, 0.50, 0.48)]),
    Shot("image", P("assets/trabajos/trabajo_cristo_manga.jpg"), 6.3, 7.2,
         label="S6 manga cristo",
         keys=[Key(0.0, 1.14, 0.50, 0.40), Key(0.9, 1.04, 0.50, 0.60)]),
    Shot("image", P("assets/trabajos/trabajo_lobo_rugido.jpg"), 7.2, 8.1,
         label="S7 lobo",
         keys=[Key(0.0, 1.26, 0.50, 0.46), Key(0.9, 1.08, 0.50, 0.50)]),
    Shot("image", P("assets/trabajos/septum.jpg"), 8.1, 9.0,
         label="S8 piercing",
         keys=[Key(0.0, 1.05, 0.50, 0.60), Key(0.9, 1.16, 0.52, 0.63)]),

    # ---- ACTO 4 · estudio (9.0-11.4): lugar, vitrina, fachada
    Shot("image", P("assets/estudio/fachada.jpg"), 9.0, 9.9, wide=True,
         label="S9 fachada",
         keys=[Key(0.0, 1.00, 0.22, 0.46), Key(0.9, 1.08, 0.46, 0.44)]),
    Shot("image", P("assets/estudio/vitrina.jpg"), 9.9, 10.8,
         label="S10 vitrina", exposure=0.98,
         keys=[Key(0.0, 1.02, 0.50, 0.52), Key(0.9, 1.14, 0.52, 0.50)]),
    Shot("video", P("film/loop_film.mp4"), 10.8, EMBLEM_IN, src_start=3.70, src_speed=1.0,
         label="S11 mural/fachada",
         keys=[Key(0.0, 1.12, 0.50, 0.50), Key(0.6, 1.22, 0.50, 0.50)]),

    # ---- ACTO 5 · marca (11.4-15.0): el emblema sobre obsidiana
    Shot("emblem", P(EMBLEM), EMBLEM_IN, TOTAL, keys=[], label="S12 emblema"),
]


TEXTS: list[Text] = [
    # Acto 1
    Text("HECHO", CINZEL_700, 54, HUESO, 112, 246, 0.10, 1.66, tracking=3.4, mode="rise"),
    Text("A MANO", CINZEL_800, 112, CREAM, 108, 314, 0.32, 1.70, tracking=1.5, mode="scale"),
    Text("PUNTO POR PUNTO", MONTSERRAT_500, 30, TEAL, 114, 1428, 2.02, 2.96, tracking=6.0, mode="fade"),
    # Acto 3
    Text("REALISMO", CINZEL_800, 96, CREAM, 108, 1408, 5.52, 7.08, tracking=2.0, mode="rise", clip=True),
    Text("BLACK & GREY", MONTSERRAT_500, 30, TEAL, 112, 1544, 5.74, 7.08, tracking=6.4, mode="fade"),
    # Acto 4
    Text("SAN BERNARDO", CINZEL_700, 64, CREAM, 108, 1288, 9.06, 11.16, tracking=3.0, mode="rise"),
    Text("JOSÉ JOAQUÍN PÉREZ 528", MONTSERRAT_500, 28, TEAL, 112, 1382, 9.28, 11.16, tracking=4.2, mode="fade"),
    # Acto 5 · cierre (bajo el emblema)
    Text("AGENDA TU HORA", CINZEL_700, 62, CREAM, 540, 1330, 12.40, 15.05, tracking=3.0, mode="scale", anchor="center", exit=0.14),
    Text("+56 9 4778 6839", MONTSERRAT_600, 34, TEAL, 540, 1436, 12.62, 15.05, tracking=2.2, mode="rise", anchor="center", exit=0.14),
    Text("@abyss_tattoo_studio", MONTSERRAT_500, 28, HUESO, 540, 1498, 12.80, 15.05, tracking=2.6, mode="fade", anchor="center", exit=0.14),
]

# Barrido especular sobre el emblema
SHIMMER_AT = 12.55
SHIMMER_DUR = 0.85

# Piezas fijas que se extraen del render
STORY_TIMES = [0.9, 2.4, 3.6, 4.8, 5.8, 6.7, 7.6, 8.5, 9.4, 10.3, 11.1, 12.1, 13.0, 14.2]
COVER_TIME = 1.25
POSTER_TIME = 13.90

# Escaleta para el visor autónomo: (inicio, fin, nombre, texto)
SCENES = [
    ("0.0", "1.8", "Manos · el artista trabajando", "HECHO A MANO"),
    ("1.8", "3.0", "Macro de aguja", "PUNTO POR PUNTO"),
    ("3.0", "4.2", "Detalle · guantes y tinta", ""),
    ("4.2", "5.4", "Registro en el estudio", ""),
    ("5.4", "6.3", "Realismo · hombro", "REALISMO / BLACK & GREY"),
    ("6.3", "7.2", "Manga · cristo", ""),
    ("7.2", "8.1", "Lobo", ""),
    ("8.1", "9.0", "Piercing · septum", ""),
    ("9.0", "9.9", "El lugar · fachada 528", "SAN BERNARDO"),
    ("9.9", "10.8", "Vitrina", ""),
    ("10.8", "11.4", "Mural", ""),
    ("11.4", "15.0", "Cierre · emblema y CTA", "AGENDA TU HORA"),
]
