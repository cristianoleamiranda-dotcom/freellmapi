"""Identidad de marca, tipografía y curvas de animación — BLACK FRIDAY ABYSS.

Dirección de arte: campaña aprobada «A VISTA / BLACK · 02 CORTE»
(poster SPEC del repo abysstattoo) + gramática cinética de la referencia
`type_01_pindown.io_1795195281.mp4` (póster cinético: tipografía gigante
recortada, bloques fotográficos duotono, push-in continuo, cortes duros y
un barrido de glifos).

Sistema:
  · Fondo obsidiana (nunca blanco retail, nunca amarillo/rojo de oferta).
  · Tipografía display Anton (sólida y contorneada), etiquetas Montserrat.
  · Acentos metálicos cálidos: cobre/champán; cromo sólo como reflejo.
  · Grano de película, viñeta y gate weave en cada fotograma.
"""

from __future__ import annotations

import math
import os
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FPS = int(os.environ.get("ABYSS_FPS", "30"))

# Zona segura IG (UI superior/inferior reservada): todo texto esencial dentro.
SAFE_X0, SAFE_X1 = 72, 1008
SAFE_Y0, SAFE_Y1 = 250, 1670

ROOT = Path(__file__).resolve().parent.parent
MATERIAL = ROOT / "material"
DROPBOX = ROOT.parent / "dropbox"
FONTS = MATERIAL / "fonts"

ANTON = FONTS / "Anton-Regular.ttf"
MONTSERRAT_500 = FONTS / "montserrat-500.ttf"
MONTSERRAT_600 = FONTS / "montserrat-600.ttf"
MONTSERRAT_700 = FONTS / "montserrat-700.ttf"
CINZEL_700 = FONTS / "cinzel-700.ttf"

# Paleta aprobada (SPEC A VISTA / BLACK) + acentos metálicos de campaña
BLACK = "#080808"
OBSIDIAN = "#14100D"
GROUND = "#0B0908"
BONE = "#B5A295"
CREAM = "#EAE3DD"
COPPER = "#C98A5E"        # acento metálico cálido (reglas, fechas, rombos)
CHAMPAGNE = "#E7C9A4"     # brillo cálido de altas luces
CHROME = "#CFD6D8"        # reflejo especular frío, sólo barridos

RGB_GROUND = tuple(int(GROUND[i:i + 2], 16) for i in (1, 3, 5))
RGB_CREAM = tuple(int(CREAM[i:i + 2], 16) for i in (1, 3, 5))
RGB_BONE = tuple(int(BONE[i:i + 2], 16) for i in (1, 3, 5))
RGB_COPPER = tuple(int(COPPER[i:i + 2], 16) for i in (1, 3, 5))
RGB_CHAMPAGNE = tuple(int(CHAMPAGNE[i:i + 2], 16) for i in (1, 3, 5))
RGB_CHROME = tuple(int(CHROME[i:i + 2], 16) for i in (1, 3, 5))

COPY = {
    "studio": "BLACK FRIDAY ABYSS TATTOO STUDIO",
    "brand": "ABYSS TATTOO Y PIERCING ♦ San Bernardo",
    "pre": "PRE BLACK FRIDAY ABYSS: 26/11. INSCRIPCIÓN POR DM. ELIGE QUE PROMOCIÓN QUIERES.",
    "cats": ["TATUAJE", "JOYERÍA", "PERFORACIONES", "MÁQUINAS DE TATUAJE"],
    "close": "BLACK FRIDAY ABYSS: 27/11",
    "ig": "@abyss_tattoo_studio",
    "wa": "wa.me/56947786839",
}


# ---------------------------------------------------------------------------
# Easing
# ---------------------------------------------------------------------------
def clamp01(x: float) -> float:
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def ease_out_cubic(x: float) -> float:
    x = clamp01(x)
    return 1 - (1 - x) ** 3


def ease_in_cubic(x: float) -> float:
    x = clamp01(x)
    return x ** 3


def ease_in_out_cubic(x: float) -> float:
    x = clamp01(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def ease_out_expo(x: float) -> float:
    x = clamp01(x)
    return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)


def ease_out_back(x: float, s: float = 1.35) -> float:
    x = clamp01(x)
    c3 = s + 1
    return 1 + c3 * (x - 1) ** 3 + s * (x - 1) ** 2


def ease_in_out_quint(x: float) -> float:
    x = clamp01(x)
    return 16 * x ** 5 if x < 0.5 else 1 - (-2 * x + 2) ** 5 / 2


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


EASINGS = {
    "io": ease_in_out_cubic,
    "o": ease_out_cubic,
    "i": ease_in_cubic,
    "ox": ease_out_expo,
    "ob": ease_out_back,
    "q": ease_in_out_quint,
    "l": lambda x: clamp01(x),
}


# ---------------------------------------------------------------------------
# Tipografía
# ---------------------------------------------------------------------------
@lru_cache(maxsize=128)
def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), int(size))


def tracked_text(draw: ImageDraw.ImageDraw, xy, text, fnt, fill, tracking=0.0,
                 anchor="ls") -> tuple[int, int]:
    """Texto con tracking manual (PIL no trackea). Devuelve (w, h)."""
    x, y = xy
    widths = [draw.textlength(ch, font=fnt) for ch in text]
    total = sum(widths) + tracking * max(0, len(text) - 1)
    asc, desc = fnt.getmetrics()
    if anchor == "ls":
        pass
    elif anchor == "cs":
        x -= total / 2
    elif anchor == "rs":
        x -= total
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += w + tracking
    return int(total), asc + desc


def text_mask(text: str, path: Path, size: int, tracking: float = 0.0,
              stroke: int = 0) -> Image.Image:
    """Máscara L de un texto (para contorno/sweep/blur sin rasterizar 2 veces)."""
    fnt = font(str(path), size)
    pad = size // 2 + stroke * 2 + 8
    tmp = Image.new("L", (8, 8))
    d = ImageDraw.Draw(tmp)
    widths = [d.textlength(ch, font=fnt) for ch in text]
    w = int(sum(widths) + tracking * max(0, len(text) - 1)) + pad * 2
    asc, desc = fnt.getmetrics()
    h = asc + desc + pad * 2
    im = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(im)
    x = pad
    for ch, cw in zip(text, widths):
        if stroke:
            d.text((x, pad), ch, font=fnt, fill=255, stroke_width=stroke, stroke_fill=255)
        else:
            d.text((x, pad), ch, font=fnt, fill=255)
        x += cw + tracking
    return im


def outline_mask(mask: Image.Image, width: int) -> Image.Image:
    """Contorno puro de una máscara (anillo exterior) vía erosión numpy."""
    a = np.asarray(mask, dtype=np.uint8)
    k = width * 2 + 1
    pad = width
    p = np.pad(a, pad, mode="constant")
    er = p.copy()
    # erosión con kernel cuadrado (min shift en 4 direcciones aprox. suficiente)
    for dy in range(-width, width + 1):
        for dx in range(-width, width + 1):
            er = np.minimum(er, np.roll(np.roll(p, dy, 0), dx, 1))
    inner = er[pad:-pad, pad:-pad]
    return Image.fromarray(np.clip(a.astype(np.int16) - inner.astype(np.int16), 0, 255).astype(np.uint8))


# ---------------------------------------------------------------------------
# Acabado: grano, viñeta, halación, gate weave
# ---------------------------------------------------------------------------
@lru_cache(maxsize=1)
def vignette_mask() -> np.ndarray:
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    cx, cy = W / 2, H * 0.47
    d = np.sqrt(((xx - cx) / (W * 0.66)) ** 2 + ((yy - cy) / (H * 0.72)) ** 2)
    mask = np.clip(1.03 - 0.34 * d ** 2.1, 0.52, 1.0)
    return mask.astype(np.float32)[..., None]


@lru_cache(maxsize=1)
def grain_bank(count: int = 12) -> tuple[np.ndarray, ...]:
    """Grano fino tipo película: sigma moderado, correlación vertical leve."""
    rng = np.random.default_rng(20261127)
    bank = []
    for _ in range(count):
        g = rng.normal(0, 1.0, (H // 2, W // 2, 1))
        g = np.repeat(np.repeat(g, 2, 0), 2, 1)
        g = 0.72 * g + 0.28 * rng.normal(0, 1.0, (H, W, 1))
        bank.append((g * 3.6).astype(np.float32))
    return tuple(bank)


def halation(frame_f32: np.ndarray, strength: float = 0.10) -> np.ndarray:
    """Derrame cálido de altas luces (halo de emulsión)."""
    import cv2
    lum = frame_f32.mean(axis=2, keepdims=True) / 255.0
    hi = np.clip(lum - 0.72, 0, None) / 0.28
    blur = cv2.GaussianBlur(hi, (0, 0), 9.0)
    warm = np.stack([blur * 1.0, blur * 0.72, blur * 0.46], axis=-1)
    return frame_f32 + warm * strength * 255.0


def finish(frame: np.ndarray, grain_index: int, grain: float = 1.0,
           flicker: float = 0.006, weave: float = 0.8,
           hal: float = 0.10, seed: int = 0) -> np.ndarray:
    """Acabado final de fotograma: weave + flicker + halación + viñeta + grano."""
    rng = np.random.default_rng(seed * 7919 + grain_index)
    f = frame.astype(np.float32)
    if weave:
        jx = int(round(rng.normal(0, weave)))
        jy = int(round(rng.normal(0, weave)))
        f = np.roll(np.roll(f, jy, 0), jx, 1)
    if flicker:
        f *= 1.0 + rng.normal(0, flicker)
    if hal:
        f = halation(f, hal)
    f *= vignette_mask()
    f += grain_bank()[grain_index % len(grain_bank())] * grain
    return np.clip(f, 0, 255).astype(np.uint8)


def ground_layer(frame_index: int) -> np.ndarray:
    """Fondo obsidiana con respiración cálida sutil (no plano muerto)."""
    t = frame_index / max(FPS, 1)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    gx = W * (0.5 + 0.06 * math.sin(t * 0.35))
    gy = H * (0.36 + 0.03 * math.cos(t * 0.27))
    d = np.sqrt(((xx - gx) / (W * 1.05)) ** 2 + ((yy - gy) / (H * 0.85)) ** 2)
    glow = np.clip(1.0 - d, 0, 1) ** 2.2
    base = np.zeros((H, W, 3), np.float32)
    base[..., 0] = 11 + glow * 26      # R
    base[..., 1] = 9 + glow * 15       # G
    base[..., 2] = 8 + glow * 9        # B
    # textura de papel negro: ruido de baja frecuencia muy tenue
    return base
