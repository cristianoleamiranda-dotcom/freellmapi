"""Línea de tiempo: planos, cámara, texto y audio.

Todo el montaje vive aquí. Cambiar el guion es cambiar estas estructuras.
Rejilla musical: 100 BPM -> 0.6 s por negra; 25 negras = 15.0 s.
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
    MONTSERRAT_700,
    REPO,
    TEAL,
)

BEAT = 0.6
TOTAL = 15.0


@dataclass
class Key:
    """Keyframe de cámara. t es relativo al plano."""
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
    mode: str = "rise"          # rise | scale | wipe | fade
    enter: float = 0.36
    exit: float = 0.20
    clip: bool = False


@dataclass
class Shot:
    kind: str                   # video | image | emblem
    source: str
    start: float
    end: float
    keys: list[Key]
    texts: list[Text] = field(default_factory=list)
    src_start: float = 0.0      # segundo dentro del video
    src_rate: float = 30.0
    src_speed: float = 1.0      # <1 = cámara lenta sobre el material
    shake: float = 0.0
    label: str = ""
    grade: dict = field(default_factory=dict)


@dataclass
class MosaicCell:
    source: str
    start: float
    end: float
    keys: list[Key]
    text: Text


def P(name: str) -> str:
    return str(REPO / name)


SHOTS: list[Shot] = [
    # P1 · hook. Macro de aguja: la cámara empuja mientras el titular entra.
    Shot(
        kind="video",
        source=P("film/hero_film.mp4"),
        start=0.0,
        end=1.8,
        src_start=3.20,          # macro de aguja
        src_rate=30.0,
        src_speed=0.55,          # 1.8 s de timeline consumen 0.99 s de macro real
        label="P1 macro aguja",
        shake=0.6,
        keys=[Key(0.0, 1.02, 0.52, 0.34), Key(1.8, 1.17, 0.50, 0.40)],
        texts=[
            Text("ESTO NO ES", CINZEL_700, 52, HUESO, 120, 286, 0.12, 1.62, tracking=3.0, mode="rise"),
            Text("UN TATUAJE", CINZEL_800, 104, CREAM, 120, 352, 0.34, 1.66, tracking=1.5, mode="scale"),
        ],
    ),
    # P2 · la firma. Lobo aullando, pull-back que revela la pieza completa.
    Shot(
        kind="image",
        source=P("assets/trabajos/trabajo_lobo_rugido.jpg"),
        start=1.8,
        end=3.6,
        label="P2 lobo",
        keys=[Key(0.0, 1.18, 0.48, 0.46), Key(1.8, 1.04, 0.50, 0.50)],
        texts=[
            Text("ES UNA FIRMA", CINZEL_800, 92, CREAM, 120, 1240, 1.84, 3.42, tracking=2.0, mode="rise", clip=True),
            Text("REALISMO BLACK & GREY", MONTSERRAT_500, 30, TEAL, 122, 1372, 2.02, 3.42, tracking=6.0, mode="fade"),
        ],
    ),
    # P3 · pieza única. Manga completa, paneo vertical lento.
    Shot(
        kind="image",
        source=P("assets/trabajos/trabajo_cristo_manga.jpg"),
        start=3.6,
        end=5.4,
        label="P3 manga",
        keys=[Key(0.0, 1.14, 0.50, 0.30), Key(1.8, 1.10, 0.50, 0.68)],
        texts=[
            Text("PIEZA ÚNICA", CINZEL_800, 88, CREAM, 120, 262, 3.66, 5.24, tracking=2.0, mode="scale"),
            Text("DISEÑO AUTORAL · SIN PLANTILLAS", MONTSERRAT_500, 28, TEAL, 122, 396, 3.86, 5.24, tracking=5.0, mode="fade"),
        ],
    ),
    # P4 · ink wipe. El gesto de limpiar la tinta es el momento más "oficio" del material.
    Shot(
        kind="video",
        source=P("film/proceso_filmacion.mp4"),
        start=5.4,
        end=7.2,
        src_start=1.60,
        src_rate=30.0,
        label="P4 en cabina",
        shake=0.4,
        grade={"brightness": 1.06},
        keys=[Key(0.0, 1.02, 0.46, 0.42, -0.6), Key(1.8, 1.13, 0.52, 0.46, -0.2)],
        texts=[
            Text("TRAZO A TRAZO", CINZEL_800, 88, CREAM, 120, 1150, 5.46, 7.02, tracking=2.0, mode="rise", clip=True),
            Text("SOMBRAS PROFUNDAS · CURADO PERFECTO", MONTSERRAT_500, 26, TEAL, 122, 1290, 5.66, 7.02, tracking=4.0, mode="fade"),
        ],
    ),
    # P5 · piercing. Crash zoom sobre el titanio.
    Shot(
        kind="image",
        source=P("assets/reel_plates/plate_p06_helix_titanio.jpg"),
        start=7.2,
        end=8.4,
        label="P5 helix",
        keys=[Key(0.0, 1.24, 0.52, 0.42), Key(1.2, 1.06, 0.50, 0.46)],
        texts=[
            Text("TITANIO", CINZEL_800, 104, CREAM, 120, 300, 7.26, 8.24, tracking=3.0, mode="scale"),
            Text("GRADO IMPLANTE · ASTM F136", MONTSERRAT_500, 28, TEAL, 122, 440, 7.44, 8.24, tracking=5.0, mode="fade"),
        ],
    ),
    # P6 · el lugar. Fachada real, dolly-in con tilt.
    Shot(
        kind="video",
        source=P("film/loop_film.mp4"),
        start=8.4,
        end=9.6,
        src_start=3.90,          # fachada
        src_rate=30.0,
        label="P6 fachada",
        grade={"brightness": 1.12, "saturation": 0.92},
        keys=[Key(0.0, 1.02, 0.50, 0.52), Key(1.2, 1.14, 0.50, 0.46)],
        texts=[
            Text("SAN BERNARDO", CINZEL_800, 76, CREAM, 120, 1152, 8.46, 9.44, tracking=2.0, mode="rise"),
            Text("JOSÉ JOAQUÍN PÉREZ 528", MONTSERRAT_600, 32, HUESO, 122, 1272, 8.64, 9.44, tracking=4.0, mode="fade"),
        ],
    ),
]

# P7 · mosaico rítmico: cuatro piezas, tres estilos, cortes al pulso.
MOSAIC_START = 9.6
MOSAIC: list[MosaicCell] = [
    MosaicCell(
        P("assets/trabajos/payaso.jpg"), 9.6, 10.05,
        [Key(0.0, 1.06, 0.50, 0.50), Key(0.45, 1.16, 0.50, 0.48)],
        Text("BLACK & GREY", CINZEL_700, 64, CREAM, 120, 300, 9.62, 10.02, tracking=3.0, mode="rise"),
    ),
    MosaicCell(
        P("assets/reel_plates/plate_p02_lobo_samurai.jpg"), 10.05, 10.5,
        [Key(0.0, 1.18, 0.48, 0.46), Key(0.45, 1.07, 0.52, 0.50)],
        Text("ORIENTAL", CINZEL_700, 64, CREAM, 120, 300, 10.07, 10.47, tracking=3.0, mode="rise"),
    ),
    MosaicCell(
        P("assets/reel_plates/plate_p05_color_anime.jpg"), 10.5, 10.95,
        [Key(0.0, 1.05, 0.50, 0.42), Key(0.45, 1.15, 0.50, 0.46)],
        Text("FULL COLOR", CINZEL_700, 64, CREAM, 120, 300, 10.52, 10.92, tracking=3.0, mode="rise"),
    ),
    MosaicCell(
        P("assets/trabajos/trabajo_hombro_real.jpg"), 10.95, 11.4,
        [Key(0.0, 1.16, 0.50, 0.50), Key(0.45, 1.04, 0.50, 0.46)],
        Text("REALISMO", CINZEL_700, 64, CREAM, 120, 300, 10.97, 11.37, tracking=3.0, mode="rise"),
    ),
]

# P8 · cierre. Emblema, CTA y dirección verificada.
CLOSE_START = 11.4
CLOSE_TEXTS = [
    Text("AGENDA TU HORA", CINZEL_800, 84, CREAM, 540, 1046, 11.58, 14.86, tracking=1.5, mode="scale"),
    Text("@abyss_tattoo_studio", MONTSERRAT_500, 34, HUESO, 540, 1392, 12.30, 14.86, tracking=4.0, mode="fade"),
    Text("J. J. PÉREZ 528 · SAN BERNARDO", MONTSERRAT_500, 28, HUESO, 540, 1444, 12.42, 14.86, tracking=3.0, mode="fade"),
]
CTA_TEXT = "WHATSAPP  +56 9 4778 6839"
CTA_Y = 1196
CTA_IN = 12.06
CTA_OUT = 14.86

# Eventos de audio (segundos absolutos)
CUTS = [1.8, 3.6, 5.4, 7.2, 8.4, 9.6, 10.05, 10.5, 10.95, 11.4]
KICKS = [round(i * BEAT, 3) for i in range(25)]
ACCENTS = [0.0, 1.8, 3.6, 5.4, 7.2, 9.6, 11.4]
RISER = (9.6, 11.4)
BELL = 12.0
