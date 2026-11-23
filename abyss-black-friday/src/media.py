"""Material, etalonaje hiperrealista y cámara virtual.

El material real de ABYSS se edita siempre (NO TRANSABLE): contraste,
hombro de altas luces, duotono cobre opcional y grano. Nada se usa crudo.
"""

from __future__ import annotations

import math
from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np

from brand import W, H, clamp01, ease_in_out_cubic


# ---------------------------------------------------------------------------
# Carga y recorte
# ---------------------------------------------------------------------------
def cover_crop(img: np.ndarray, target: float) -> np.ndarray:
    h, w = img.shape[:2]
    if w / h > target:
        nw = int(round(h * target))
        x0 = (w - nw) // 2
        return img[:, x0:x0 + nw]
    nh = int(round(w / target))
    y0 = (h - nh) // 2
    return img[y0:y0 + nh, :]


def load_image(path: str | Path) -> np.ndarray:
    p = str(path)
    img = cv2.imread(p, cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(p)
    return img


def make_plate(path: str | Path, width: int = 1400, aspect: float | None = None) -> np.ndarray:
    """Plate de trabajo: recorte cover a `aspect` (default 9:16) y ancho fijo."""
    img = load_image(path)
    if aspect:
        img = cover_crop(img, aspect)
    h, w = img.shape[:2]
    s = width / w
    if abs(s - 1.0) > 0.01:
        img = cv2.resize(img, (int(round(w * s)), int(round(h * s))), interpolation=cv2.INTER_LANCZOS4)
    return img


class VideoReader:
    """Lectura secuencial de clips reales (máquinas/proceso)."""

    def __init__(self, path: str | Path, width: int = 1200, aspect: float = W / H):
        self.cap = cv2.VideoCapture(str(path))
        if not self.cap.isOpened():
            raise FileNotFoundError(path)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30.0
        self.count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.width = width
        self.aspect = aspect
        self._index = -1
        self._frame = None

    def frame_at(self, seconds: float) -> np.ndarray:
        idx = max(0, min(int(round(seconds * self.fps)), self.count - 1))
        if idx != self._index:
            if idx < self._index or idx - self._index > 6:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            else:
                for _ in range(idx - self._index - 1):
                    self.cap.grab()
            ok, frame = self.cap.read()
            if not ok:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, idx - 1))
                ok, frame = self.cap.read()
            if not ok:
                raise RuntimeError(f"lectura fallida {seconds:.2f}s")
            plate = cover_crop(frame, self.aspect)
            h, w = plate.shape[:2]
            if w < self.width:
                s = self.width / w
                plate = cv2.resize(plate, (int(round(w * s)), int(round(h * s))), interpolation=cv2.INTER_LANCZOS4)
            self._frame = plate
            self._index = idx
        return self._frame

    def close(self):
        self.cap.release()


# ---------------------------------------------------------------------------
# Etalonaje hiperrealista
# ---------------------------------------------------------------------------
def build_lut(contrast: float = 1.10, warm_highs: float = 0.045,
              cool_shadows: float = 0.020, lift: float = -0.004) -> np.ndarray:
    x = np.arange(256, dtype=np.float32) / 255.0
    base = np.clip((x - 0.5) * contrast + 0.5 + lift, 0, 1)
    sh = (1 - base) ** 2
    hi = base ** 2
    r = np.clip(base + warm_highs * hi - cool_shadows * 0.5 * sh, 0, 1)
    g = np.clip(base + warm_highs * 0.35 * hi + cool_shadows * 0.10 * sh, 0, 1)
    b = np.clip(base - warm_highs * 0.35 * hi + cool_shadows * sh, 0, 1)
    return (np.stack([b, g, r], -1) * 255).round().astype(np.uint8).reshape(256, 1, 3)


@lru_cache(maxsize=8)
def lut(contrast: float = 1.10, warm: float = 0.045, cool: float = 0.020) -> np.ndarray:
    return build_lut(contrast, warm, cool)


def highlight_shoulder(frame: np.ndarray, start: float = 0.78, strength: float = 0.7) -> np.ndarray:
    x = frame.astype(np.float32) / 255.0
    over = np.clip(x - start, 0.0, None)
    y = x - strength * over * over / (1.0 - start)
    return np.clip(y * 255.0, 0, 255).astype(np.uint8)


def grade(frame: np.ndarray, saturation: float = 0.88, contrast: float = 1.10,
          warm: float = 0.045) -> np.ndarray:
    out = cv2.LUT(frame, lut(contrast, warm))
    if abs(saturation - 1.0) > 0.005:
        gray = cv2.cvtColor(out, cv2.COLOR_BGR2GRAY)
        out = cv2.addWeighted(out, saturation, cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR), 1 - saturation, 0)
    return highlight_shoulder(out)


def duotone(frame: np.ndarray, shadow=(10, 8, 7), mid=(60, 96, 138), high=(210, 231, 231),
            mix: float = 0.85) -> np.ndarray:
    """Duotono metálico cálido: sombras obsidiana → medios cobre → altos champán.

    (tuplas en RGB; se convierten a BGR al componer)
    """
    g = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
    g = np.clip((g - 0.5) * 1.12 + 0.5, 0, 1)
    sh = np.array(shadow, np.float32)[::-1]      # -> BGR
    md = np.array(mid, np.float32)[::-1]
    hi = np.array(high, np.float32)[::-1]
    lo = np.clip(g * 2, 0, 1)[..., None]
    up = np.clip(g * 2 - 1, 0, 1)[..., None]
    ramp = sh * (1 - lo) + md * lo
    ramp = ramp * (1 - up) + hi * up
    if mix >= 0.999:
        return ramp.astype(np.uint8)
    return np.clip(frame.astype(np.float32) * (1 - mix) + ramp * mix, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------------------
# Cámara virtual (afín sub-píxel) sobre un plate
# ---------------------------------------------------------------------------
def sample_keys(keys, t: float):
    if not keys:
        return 1.0, 0.5, 0.5, 0.0
    if t <= keys[0]["t"]:
        k = keys[0]
        return k.get("zoom", 1.0), k.get("cx", 0.5), k.get("cy", 0.5), k.get("rot", 0.0)
    if t >= keys[-1]["t"]:
        k = keys[-1]
        return k.get("zoom", 1.0), k.get("cx", 0.5), k.get("cy", 0.5), k.get("rot", 0.0)
    for a, b in zip(keys, keys[1:]):
        if a["t"] <= t <= b["t"]:
            u = clamp01((t - a["t"]) / max(1e-6, b["t"] - a["t"]))
            e = EASE = ease_in_out_cubic(u)
            return (
                a.get("zoom", 1.0) + (b.get("zoom", 1.0) - a.get("zoom", 1.0)) * e,
                a.get("cx", 0.5) + (b.get("cx", 0.5) - a.get("cx", 0.5)) * e,
                a.get("cy", 0.5) + (b.get("cy", 0.5) - a.get("cy", 0.5)) * e,
                a.get("rot", 0.0) + (b.get("rot", 0.0) - a.get("rot", 0.0)) * e,
            )
    k = keys[-1]
    return k.get("zoom", 1.0), k.get("cx", 0.5), k.get("cy", 0.5), k.get("rot", 0.0)


def camera_crop(plate: np.ndarray, out_w: int, out_h: int, zoom: float,
                cx: float = 0.5, cy: float = 0.5, rot: float = 0.0) -> np.ndarray:
    """Muestrea `plate` con zoom/centro/rotación hacia un bloque out_w×out_h."""
    ph, pw = plate.shape[:2]
    zoom = max(1.0, zoom)
    theta = math.radians(rot)
    cos, sin = math.cos(theta), math.sin(theta)
    sx, sy = (out_w / 2) / zoom, (out_h / 2) / zoom
    ex = abs(sx * cos) + abs(sy * sin)
    ey = abs(sx * sin) + abs(sy * cos)
    px = min(max(cx * pw, ex), pw - ex) if pw > 2 * ex else pw / 2
    py = min(max(cy * ph, ey), ph - ey) if ph > 2 * ey else ph / 2
    m = np.array([
        [cos / zoom, sin / zoom, px - (cos * out_w / 2 + sin * out_h / 2) / zoom],
        [-sin / zoom, cos / zoom, py - (-sin * out_w / 2 + cos * out_h / 2) / zoom],
    ], np.float32)
    return cv2.warpAffine(plate, m, (out_w, out_h),
                          flags=cv2.INTER_CUBIC | cv2.WARP_INVERSE_MAP,
                          borderMode=cv2.BORDER_REFLECT)


def motion_blur(img: np.ndarray, length: int, angle: float = 0.0) -> np.ndarray:
    if length <= 1:
        return img
    k = np.zeros((length, length), np.float32)
    a = math.radians(angle)
    cx = cy = (length - 1) / 2
    for i in range(length):
        x = int(round(cx + (i - cy) * math.cos(a)))
        y = int(round(cy + (i - cy) * math.sin(a)))
        if 0 <= x < length and 0 <= y < length:
            k[y, x] = 1
    if k.sum() == 0:
        k[cy, :] = 1
    k /= k.sum()
    return cv2.filter2D(img, -1, k)
