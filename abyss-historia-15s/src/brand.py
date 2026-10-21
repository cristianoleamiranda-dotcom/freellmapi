"""Identidad de marca, tipografía y curvas de animación.

Todos los valores salen de la skill `abyss-video-image-studio` y de los assets
del repo `cristianoleamiranda-dotcom/abysstattoo`.
"""

from __future__ import annotations

import math
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
FPS = 60
DURATION = 15.0
FRAMES = int(round(FPS * DURATION))

# Paleta oficial
OBSIDIAN = "#14100D"
PANEL = "#1A1512"
HUESO = "#B5A295"
CREAM = "#EAE3DD"
PAPER = "#F6F1ED"
SAGE = "#556C65"
TEAL = "#9EC4BA"

# Zonas seguras 9:16
SAFE_X0, SAFE_X1 = 84, 960
SAFE_Y0, SAFE_Y1 = 210, 1500
TEXT_X = 108
BOTTOM_X = 108

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT.parent / "skills-hub" / ".cache" / "repos" / "abysstattoo"
FONTS = REPO / "assets" / "fonts"

CINZEL_700 = FONTS / "cinzel-700.ttf"
CINZEL_800 = FONTS / "cinzel-800.ttf"
MONTSERRAT_500 = FONTS / "montserrat-500.ttf"
MONTSERRAT_600 = FONTS / "montserrat-600.ttf"
MONTSERRAT_700 = FONTS / "montserrat-700.ttf"


# --------------------------------------------------------------------------
# Easing
# --------------------------------------------------------------------------

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


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


# --------------------------------------------------------------------------
# Texto
# --------------------------------------------------------------------------

@lru_cache(maxsize=64)
def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def _copy_font(path: str, size: int):
    # lru_cache sobre FreeTypeFont es seguro para lectura concurrente.
    return font(str(path), size)


@lru_cache(maxsize=256)
def text_bitmap(
    text: str,
    font_path: str,
    size: int,
    color: str,
    tracking: float = 0.0,
    shadow: bool = True,
    pad: int = 28,
) -> Image.Image:
    """Renderiza texto con tracking manual y sombra suave, recortado con padding."""
    f = _copy_font(font_path, size)
    advances = [f.getlength(ch) for ch in text]
    width = int(math.ceil(sum(advances) + tracking * max(0, len(text) - 1)))
    ascent, descent = f.getmetrics()
    height = ascent + descent

    img = Image.new("RGBA", (width + pad * 2, height + pad * 2), (0, 0, 0, 0))
    if shadow:
        shadow_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
        sdraw = ImageDraw.Draw(shadow_img)
        sx = float(pad)
        for ch, adv in zip(text, advances):
            sdraw.text((sx + 2, pad + 3), ch, font=f, fill=(10, 8, 6, 150))
            sx += adv + tracking
        shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(7))
        img = Image.alpha_composite(img, shadow_img)

    # El texto va después de la sombra y sobre la capa ya compuesta.
    draw = ImageDraw.Draw(img)
    x = float(pad)
    for ch, adv in zip(text, advances):
        draw.text((x, pad), ch, font=f, fill=color)
        x += adv + tracking

    return img


def paste_text(
    frame: Image.Image,
    text: str,
    font_path: Path,
    size: int,
    color: str,
    x: int,
    y: int,
    *,
    alpha: float = 1.0,
    scale: float = 1.0,
    tracking: float = 0.0,
    shadow: bool = True,
    anchor: str = "left",
    clip: float | None = None,
) -> None:
    """Compone texto sobre un frame RGBA. `clip` recorta de izquierda a derecha (0..1)."""
    if alpha <= 0.002:
        return
    layer = text_bitmap(text, str(font_path), size, color, tracking, shadow)
    if clip is not None:
        c = clamp01(clip)
        if c <= 0.002:
            return
        cut = int(layer.width * c)
        layer = layer.crop((0, 0, cut, layer.height))
    if scale != 1.0:
        layer = layer.resize(
            (max(1, int(layer.width * scale)), max(1, int(layer.height * scale))),
            Image.LANCZOS,
        )
    if alpha < 0.999:
        a = layer.getchannel("A").point(lambda v: int(v * alpha))
        layer.putalpha(a)
    px = x - (layer.width // 2 if anchor == "center" else layer.width if anchor == "right" else 0)
    frame.alpha_composite(layer, (int(px), int(y - layer.height // 2 if anchor == "middle" else y)))


def hairline(draw: ImageDraw.ImageDraw, x0: int, y: int, length: int, color: str, alpha: int = 200, width: int = 2) -> None:
    r, g, b = ImageColor_get(color)
    draw.rectangle([x0, y, x0 + length, y + width - 1], fill=(r, g, b, alpha))


def ImageColor_get(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)


def rgba(color: str, alpha: int = 255) -> tuple[int, int, int, int]:
    r, g, b = ImageColor_get(color)
    return r, g, b, alpha


def pill(text: str, font_path: Path, size: int, fg: str, bg: str, tracking: float = 0.0, pad_x: int = 44, pad_y: int = 22) -> Image.Image:
    """Pastilla redondeada con texto centrado ópticamente."""
    label = text_bitmap(text, str(font_path), size, fg, tracking, shadow=False, pad=4)
    w = label.width + pad_x * 2
    h = label.height + pad_y * 2
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([0, 0, w - 1, h - 1], radius=h // 2, fill=rgba(bg))
    img.alpha_composite(label, (pad_x - 4, pad_y - 4))
    return img


def shimmer(layer: Image.Image, progress: float, width: int = 160) -> Image.Image:
    """Barrido especular recortado a la silueta de la capa."""
    x = int(-width + (layer.width + width * 2) * clamp01(progress))
    band = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(band)
    for i in range(width):
        a = int(70 * (1 - abs(i - width / 2) / (width / 2)))
        draw.line([(x + i, 0), (x + i, layer.height)], fill=(255, 250, 240, a))
    band = band.filter(ImageFilter.GaussianBlur(10))
    mask = layer.getchannel("A")
    band.putalpha(Image.composite(band.getchannel("A"), Image.new("L", layer.size, 0), mask))
    return Image.alpha_composite(layer, band)


def radial_glow(size: tuple[int, int], color: str, strength: float = 0.5) -> Image.Image:
    w, h = size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cx, cy = w / 2, h * 0.5
    d = np.sqrt(((xx - cx) / (w * 0.7)) ** 2 + ((yy - cy) / (h * 0.55)) ** 2)
    mask = np.clip(1 - d, 0, 1) ** 2 * strength
    r, g, b = ImageColor_get(color)
    arr = np.zeros((h, w, 4), dtype=np.uint8)
    arr[..., 0], arr[..., 1], arr[..., 2] = r, g, b
    arr[..., 3] = (mask * 255).astype(np.uint8)
    return Image.fromarray(arr, "RGBA")
