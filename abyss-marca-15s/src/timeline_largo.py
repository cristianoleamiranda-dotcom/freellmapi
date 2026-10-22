"""Línea de tiempo · versión larga de 18.00 s (9:16, 100 BPM).

Rejilla: 100 BPM -> 0.6 s por negra -> 30 negras = 18.0 s.

Diferencias con la versión de 15 s (src/timeline.py):
  · +1.8 s de proceso real (`film/proceso_pierna.mp4`, el tatuador trabajando),
    que es el material que sólo se veía de refilón en el corte corto;
  · +0.3 s al acto del lugar (la fachada tiene 1.2 s de paneo en vez de 0.9);
  · +1.2 s al cierre, para que el emblema respire y el CTA se lea dos veces.

Todo sigue cayendo en negras: 1.8 · 3.0 · 4.2 · 5.4 · 7.2 · 8.1 · 9.0 · 9.9
· 10.8 · 12.0 · 12.6 · 13.2.
"""

from __future__ import annotations

from timeline import (
    BEAT,
    CINZEL_700,
    CINZEL_800,
    CREAM,
    HUESO,
    MONTSERRAT_500,
    MONTSERRAT_600,
    P,
    TEAL,
    Key,
    Shot,
    Text,
)

TOTAL = 18.0

EMBLEM = "assets/reel_plates/emblema_abyss_alpha.png"
EMBLEM_CY = 720
EMBLEM_SIZE = 880
EMBLEM_VISIBLE_R = EMBLEM_SIZE * 0.4375
RING_R = int(EMBLEM_VISIBLE_R) + 18

# Momentos clave, compartidos con audio.py
EMBLEM_IN = 13.2
BELL = EMBLEM_IN + 0.35
RISER = (12.60, EMBLEM_IN)
CUTS = [1.8, 3.0, 4.2, 5.4, 7.2, 8.1, 9.0, 9.9, 10.8, 12.0, 12.6, EMBLEM_IN]
KICKS = [round(i * BEAT, 3) for i in range(30)]
ACCENTS = [1.8, 3.0, 4.2, 5.4, 10.8, EMBLEM_IN]

SHIMMER_AT = 14.45
SHIMMER_DUR = 0.85

SHOTS: list[Shot] = [
    # ---- ACTO 1 · gancho (0.0-3.0)
    Shot("video", P("film/hero_film.mp4"), 0.0, 1.8, src_start=0.12, src_speed=0.55,
         shake=0.4, label="S1 artista trabajando",
         keys=[Key(0.0, 1.06, 0.50, 0.42), Key(1.8, 1.19, 0.50, 0.40)]),
    Shot("video", P("film/hero_film.mp4"), 1.8, 3.0, src_start=2.45, src_speed=0.60,
         label="S2 macro aguja", exposure=1.22,
         keys=[Key(0.0, 1.16, 0.50, 0.44), Key(1.2, 1.03, 0.50, 0.46)]),

    # ---- ACTO 2 · proceso (3.0-7.2): el bloque que crece en la versión larga
    # proceso_detalle.mp4 viene quemado de cámara (36 % de píxeles saturados en la
    # fuente): se sustituye por el resultado sobre el brazo, que sí tiene rango.
    Shot("video", P("film/proceso_pierna.mp4"), 3.0, 4.2, src_start=4.20, src_speed=0.80,
         label="S3 sesion en curso",
         keys=[Key(0.0, 1.05, 0.50, 0.44), Key(1.2, 1.14, 0.52, 0.46)]),
    Shot("video", P("film/proceso_filmacion.mp4"), 4.2, 5.4, src_start=2.60, src_speed=0.80,
         label="S4 registro en estudio",
         keys=[Key(0.0, 1.04, 0.50, 0.46), Key(1.2, 1.15, 0.52, 0.48)]),
    Shot("video", P("film/proceso_pierna.mp4"), 5.4, 7.2, src_start=0.90, src_speed=0.78,
         label="S5 sesión en curso",
         keys=[Key(0.0, 1.05, 0.50, 0.44), Key(1.8, 1.16, 0.52, 0.46)]),

    # ---- ACTO 3 · obra (7.2-10.8)
    Shot("image", P("assets/trabajos/trabajo_hombro_real.jpg"), 7.2, 8.1,
         label="S6 hombro realismo",
         keys=[Key(0.0, 1.20, 0.50, 0.46), Key(0.9, 1.07, 0.50, 0.48)]),
    Shot("image", P("assets/trabajos/trabajo_cristo_manga.jpg"), 8.1, 9.0,
         label="S7 manga cristo",
         keys=[Key(0.0, 1.14, 0.50, 0.40), Key(0.9, 1.04, 0.50, 0.60)]),
    Shot("image", P("assets/trabajos/trabajo_lobo_rugido.jpg"), 9.0, 9.9,
         label="S8 lobo",
         keys=[Key(0.0, 1.26, 0.50, 0.46), Key(0.9, 1.08, 0.50, 0.50)]),
    Shot("image", P("assets/trabajos/septum.jpg"), 9.9, 10.8,
         label="S9 piercing",
         keys=[Key(0.0, 1.05, 0.50, 0.60), Key(0.9, 1.16, 0.52, 0.63)]),

    # ---- ACTO 4 · estudio (10.8-13.2)
    Shot("image", P("assets/estudio/fachada.jpg"), 10.8, 12.0, wide=True,
         label="S10 fachada",
         keys=[Key(0.0, 1.00, 0.20, 0.46), Key(1.2, 1.09, 0.50, 0.44)]),
    Shot("image", P("assets/estudio/vitrina.jpg"), 12.0, 12.6,
         label="S11 vitrina", exposure=0.98,
         keys=[Key(0.0, 1.02, 0.50, 0.52), Key(0.6, 1.10, 0.52, 0.50)]),
    Shot("video", P("film/loop_film.mp4"), 12.6, EMBLEM_IN, src_start=3.70, src_speed=1.0,
         label="S12 mural/fachada",
         keys=[Key(0.0, 1.12, 0.50, 0.50), Key(0.6, 1.22, 0.50, 0.50)]),

    # ---- ACTO 5 · marca (13.2-18.0)
    Shot("emblem", P(EMBLEM), EMBLEM_IN, TOTAL, keys=[], label="S13 emblema"),
]


TEXTS: list[Text] = [
    # Acto 1
    Text("HECHO", CINZEL_700, 54, HUESO, 112, 246, 0.10, 1.66, tracking=3.4, mode="rise"),
    Text("A MANO", CINZEL_800, 112, CREAM, 108, 314, 0.32, 1.70, tracking=1.5, mode="scale"),
    Text("PUNTO POR PUNTO", MONTSERRAT_500, 30, TEAL, 114, 1428, 2.02, 2.96, tracking=6.0, mode="fade"),
    # Acto 2 · sólo en la versión larga
    Text("TRAZO A TRAZO", CINZEL_800, 84, CREAM, 108, 1396, 5.58, 7.06, tracking=2.2, mode="rise", clip=True),
    Text("SESIÓN EN CURSO", MONTSERRAT_500, 28, TEAL, 112, 1516, 5.80, 7.06, tracking=5.6, mode="fade"),
    # Acto 3
    Text("REALISMO", CINZEL_800, 96, CREAM, 108, 1408, 7.32, 9.52, tracking=2.0, mode="rise", clip=True),
    Text("BLACK & GREY", MONTSERRAT_500, 30, TEAL, 112, 1544, 7.54, 9.52, tracking=6.4, mode="fade"),
    # Acto 4
    Text("SAN BERNARDO", CINZEL_700, 64, CREAM, 108, 1288, 10.86, 12.92, tracking=3.0, mode="rise"),
    Text("JOSÉ JOAQUÍN PÉREZ 528", MONTSERRAT_500, 28, TEAL, 112, 1382, 11.08, 12.92, tracking=4.2, mode="fade"),
    # Acto 5 · cierre
    Text("AGENDA TU HORA", CINZEL_700, 62, CREAM, 540, 1330, 14.20, 18.05, tracking=3.0,
         mode="scale", anchor="center", exit=0.14),
    Text("+56 9 4778 6839", MONTSERRAT_600, 34, TEAL, 540, 1436, 14.42, 18.05, tracking=2.2,
         mode="rise", anchor="center", exit=0.14),
    Text("@abyss_tattoo_studio", MONTSERRAT_500, 28, HUESO, 540, 1498, 14.60, 18.05, tracking=2.6,
         mode="fade", anchor="center", exit=0.14),
]

STORY_TIMES = [0.9, 2.4, 3.6, 4.8, 6.2, 7.7, 8.6, 9.5, 10.4, 11.5, 12.3, 13.7, 15.4, 17.4]
COVER_TIME = 1.25
POSTER_TIME = 16.60

SCENES = [
    ("0.0", "1.8", "Manos · el artista trabajando", "HECHO A MANO"),
    ("1.8", "3.0", "Macro de aguja", "PUNTO POR PUNTO"),
    ("3.0", "4.2", "Detalle · guantes y tinta", ""),
    ("4.2", "5.4", "Registro en el estudio", ""),
    ("5.4", "7.2", "Sesión en curso · la pierna", "TRAZO A TRAZO"),
    ("7.2", "8.1", "Realismo · hombro", "REALISMO / BLACK & GREY"),
    ("8.1", "9.0", "Manga · cristo", ""),
    ("9.0", "9.9", "Lobo", ""),
    ("9.9", "10.8", "Piercing · septum", ""),
    ("10.8", "12.0", "El lugar · fachada 528", "SAN BERNARDO"),
    ("12.0", "12.6", "Vitrina", ""),
    ("12.6", "13.2", "Mural", ""),
    ("13.2", "18.0", "Cierre · emblema y CTA", "AGENDA TU HORA"),
]
