"""Motor cinético: capas, retícula de póster y transiciones de barrido.

Recrea la gramática de la referencia (póster cinético): tipografía display
gigante recortada en los bordes, bloques fotográficos duotono como
rectángulos duros, micro-etiquetas trackeadas, push-in continuo por capa
(parallax), cortes duros y whips con desenfoque direccional.
"""

from __future__ import annotations

import math
from functools import lru_cache

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import brand as B
from brand import W, H, clamp01, EASINGS
from media import camera_crop, motion_blur, sample_keys

CANVAS: dict[tuple, Image.Image] = {}


# ---------------------------------------------------------------------------
# Interpolación de claves de capa: x, y, s(cale), a(lpha), rot, blur
# ---------------------------------------------------------------------------
def layer_state(layer: dict, t: float):
    keys = layer.get("keys") or [{"t": 0.0}]
    st = {"x": layer.get("x", W / 2), "y": layer.get("y", H / 2), "s": 1.0,
          "a": 1.0, "rot": layer.get("rot", 0.0), "blur": 0.0}
    if t <= keys[0]["t"]:
        st.update({k: keys[0][k] for k in st if k in keys[0]})
        return st
    if t >= keys[-1]["t"]:
        st.update({k: keys[-1][k] for k in st if k in keys[-1]})
        return st
    for a, b in zip(keys, keys[1:]):
        if a["t"] <= t <= b["t"]:
            u = clamp01((t - a["t"]) / max(1e-6, b["t"] - a["t"]))
            e = EASINGS.get(b.get("ease", "io"), EASINGS["io"])(u)
            for k in st:
                if k in a or k in b:
                    va = a.get(k, st[k])
                    vb = b.get(k, va)
                    st[k] = va + (vb - va) * e
            return st
    st.update({k: keys[-1][k] for k in st if k in keys[-1]})
    return st


def visible(layer: dict, t: float) -> bool:
    return layer.get("in", -1e9) <= t < layer.get("out", 1e9)


# ---------------------------------------------------------------------------
# Rasterizado de capas estáticas (cache)
# ---------------------------------------------------------------------------
def _rgba(color) -> tuple:
    if isinstance(color, str):
        c = color.lstrip("#")
        return (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16))
    return tuple(color)[:3]


@lru_cache(maxsize=None)
def text_canvas(text: str, font_path: str, size: int, color: tuple, tracking: int,
                outline: int, pad: int = 0) -> Image.Image:
    fnt = B.font(font_path, size)
    pad = pad or size // 3 + outline * 2 + 12
    tmp = Image.new("L", (8, 8))
    d = ImageDraw.Draw(tmp)
    widths = [d.textlength(ch, font=fnt) for ch in text]
    tw = int(sum(widths) + tracking * max(0, len(text) - 1))
    asc, desc = fnt.getmetrics()
    im = Image.new("RGBA", (tw + pad * 2, asc + desc + pad * 2), (0, 0, 0, 0))
    if outline:
        solid = Image.new("L", im.size, 0)
        ds = ImageDraw.Draw(solid)
        x = pad
        for ch, cw in zip(text, widths):
            ds.text((x, pad), ch, font=fnt, fill=255, stroke_width=outline, stroke_fill=255)
            x += cw + tracking
        inner = Image.new("L", im.size, 0)
        di = ImageDraw.Draw(inner)
        x = pad
        for ch, cw in zip(text, widths):
            di.text((x, pad), ch, font=fnt, fill=255)
            x += cw + tracking
        a = np.clip(np.asarray(solid, np.int16) - np.asarray(inner, np.int16), 0, 255).astype(np.uint8)
        arr = np.zeros((*a.shape, 4), np.uint8)
        arr[..., 0], arr[..., 1], arr[..., 2] = color
        arr[..., 3] = a
        return Image.fromarray(arr, "RGBA")
    d = ImageDraw.Draw(im)
    x = pad
    for ch, cw in zip(text, widths):
        d.text((x, pad), ch, font=fnt, fill=color + (255,))
        x += cw + tracking
    return im


@lru_cache(maxsize=None)
def para_canvas(lines: tuple, font_path: str, size: int, color: tuple,
                tracking: int, lead: int, align: str) -> Image.Image:
    fnt = B.font(font_path, size)
    tmp = Image.new("L", (8, 8))
    d = ImageDraw.Draw(tmp)
    ws = []
    for ln in lines:
        w = sum(d.textlength(ch, font=fnt) for ch in ln) + tracking * max(0, len(ln) - 1)
        ws.append(int(w))
    asc, desc = fnt.getmetrics()
    lh = asc + desc + lead
    tw = max(ws) if ws else 8
    im = Image.new("RGBA", (tw + 24, lh * len(lines) + 24), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, ln in enumerate(lines):
        if align == "l":
            x = 12
        elif align == "c":
            x = 12 + (tw - ws[i]) / 2
        else:
            x = 12 + tw - ws[i]
        xx = x
        for ch in ln:
            d.text((xx, 12 + i * lh), ch, font=fnt, fill=color + (255,))
            xx += d.textlength(ch, font=fnt) + tracking
    return im


@lru_cache(maxsize=None)
def img_canvas(path: str) -> Image.Image:
    im = Image.open(path).convert("RGBA")
    return im


@lru_cache(maxsize=None)
def rule_canvas(w: int, h: int, color: tuple) -> Image.Image:
    im = Image.new("RGBA", (max(2, w), max(1, h)), color + (255,))
    return im


@lru_cache(maxsize=None)
def box_canvas(w: int, h: int, color: tuple, stroke: int) -> Image.Image:
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([stroke / 2, stroke / 2, w - stroke / 2 - 1, h - stroke / 2 - 1],
                outline=color + (255,), width=stroke)
    return im


@lru_cache(maxsize=None)
def sweep_canvas(w: int, h: int, color: tuple) -> Image.Image:
    """Barra especular metálica: gradiente horizontal suave (cromo)."""
    x = np.linspace(-1, 1, w, dtype=np.float32)
    prof = np.clip(1 - np.abs(x), 0, 1) ** 2.2
    arr = np.zeros((h, w, 4), np.uint8)
    arr[..., 0] = color[0]
    arr[..., 1] = color[1]
    arr[..., 2] = color[2]
    arr[..., 3] = (prof * 255).astype(np.uint8)[None, :]
    return Image.fromarray(arr, "RGBA")


# ---------------------------------------------------------------------------
# Composición de una capa en el frame
# ---------------------------------------------------------------------------
def draw_layer(frame: Image.Image, layer: dict, t: float, plates: dict) -> None:
    st = layer_state(layer, t)
    a = clamp01(st["a"]) * clamp01(layer.get("alpha", 1.0))
    if a <= 0.004:
        return
    kind = layer["kind"]

    if kind == "photo":
        plate = plates[layer["src"]]
        if callable(plate):
            plate = plate(t)
        cam = sample_keys(layer.get("cam"), t)
        bw = int(round(layer["w"] * st["s"]))
        bh = int(round(layer["h"] * st["s"]))
        crop = camera_crop(plate, bw, bh, cam[0], cam[1], cam[2], cam[3])
        if st["blur"] > 0.5:
            crop = cv2.GaussianBlur(crop, (0, 0), st["blur"])
        im = Image.fromarray(crop).convert("RGBA")
        if st["rot"]:
            im = im.rotate(st["rot"], resample=Image.BICUBIC, expand=True)
        if a < 0.999:
            im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
        frame.alpha_composite(im, (int(st["x"] - im.width / 2), int(st["y"] - im.height / 2)))
        return

    if kind in ("type", "label"):
        col = _rgba(layer.get("color", B.CREAM))
        cv_ = text_canvas(layer["text"], str(layer["font"]), int(layer["size"]),
                          col, int(layer.get("track", 0)), int(layer.get("outline", 0)))
    elif kind == "para":
        col = _rgba(layer.get("color", B.BONE))
        cv_ = para_canvas(tuple(layer["lines"]), str(layer["font"]), int(layer["size"]),
                          col, int(layer.get("track", 0)), int(layer.get("lead", 6)),
                          layer.get("align", "l"))
    elif kind == "roundel":
        cv_ = img_canvas(str(layer["src"]))
        base = float(layer.get("size", 200)) / cv_.width
        st = dict(st); st["s"] = st["s"] * base
    elif kind == "rule":
        cv_ = rule_canvas(int(layer["w"]), int(layer["h"]), _rgba(layer.get("color", B.COPPER)))
    elif kind == "box":
        cv_ = box_canvas(int(layer["w"]), int(layer["h"]), _rgba(layer.get("color", B.BONE)),
                         int(layer.get("stroke", 3)))
    elif kind == "sweep":
        cv_ = sweep_canvas(int(layer["w"]), int(layer["h"]), _rgba(layer.get("color", B.CHROME)))
    else:
        return

    im = cv_
    if abs(st["s"] - 1.0) > 0.002:
        nw, nh = max(2, int(im.width * st["s"])), max(2, int(im.height * st["s"]))
        im = im.resize((nw, nh), Image.LANCZOS)
    if st["rot"]:
        im = im.rotate(st["rot"], resample=Image.BICUBIC, expand=True)
    if st["blur"] > 0.5:
        im = im.filter(ImageFilter.GaussianBlur(st["blur"]))
    if a < 0.999:
        im = im.copy()
        im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    anchor = layer.get("anchor", "center")
    if anchor == "left":
        px = int(st["x"])
    elif anchor == "right":
        px = int(st["x"] - im.width)
    else:
        px = int(st["x"] - im.width / 2)
    frame.alpha_composite(im, (px, int(st["y"] - im.height / 2)))


# ---------------------------------------------------------------------------
# Escena y transiciones
# ---------------------------------------------------------------------------
def render_scene(scene: dict, t: float, plates: dict, frame_index: int) -> Image.Image:
    bg = B.ground_layer(frame_index)
    img = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).convert("RGBA")
    for layer in sorted(scene["layers"], key=lambda l: l.get("z", 0)):
        if visible(layer, t):
            draw_layer(img, layer, t, plates)
    return img


def whip_mix(out_img: np.ndarray, in_img: np.ndarray, p: float, direction: int = 1) -> np.ndarray:
    """Barrido tipo flujo óptico: salida acelera hacia un lado con blur
    direccional creciente, entrada frena desde el otro lado."""
    e_out = p * p
    e_in = (1 - p) * (1 - p)
    blur_out = 2 + int(46 * p)
    blur_in = 2 + int(46 * (1 - p))
    a = motion_blur(out_img, blur_out, 0)
    b = motion_blur(in_img, blur_in, 0)
    off_out = int(direction * e_out * W * 0.9)
    off_in = int(-direction * e_in * W * 0.9)
    ca = np.roll(a, off_out, axis=1)
    cb = np.roll(b, off_in, axis=1)
    w = (0.5 - 0.5 * math.cos(math.pi * clamp01(p)))  # smoothstep
    mix = ca.astype(np.float32) * (1 - w) + cb.astype(np.float32) * w
    # streak cobre en el punto medio del barrido
    streak = math.sin(math.pi * clamp01(p)) ** 1.6
    if streak > 0.02:
        x = np.linspace(0, 1, W, np.float32)[None, :, None]
        pos = 0.5 + direction * (0.5 - p) * 0.8
        g = np.exp(-((x - pos) ** 2) / (2 * 0.05 ** 2))[..., 0][..., None] if False else np.exp(-((x - pos) ** 2) / (2 * 0.05 ** 2))
        col = np.array(B.RGB_COPPER, np.float32)[None, None, :]
        mix = mix + g * col * (streak * 0.55)
    return np.clip(mix, 0, 255).astype(np.uint8)
