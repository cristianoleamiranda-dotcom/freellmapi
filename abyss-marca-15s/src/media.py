"""Lectura de material, cámara virtual y etalonaje.

La cámara trabaja con una matriz afín sub-píxel: cada frame de salida se muestrea
del plate de origen con zoom, centro y rotación interpolados entre keyframes.
"""

from __future__ import annotations

import math
from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np

from brand import H, W, ease_in_out_cubic, ease_out_cubic, clamp01

TARGET = W / H


def cover_crop(img: np.ndarray, target: float = TARGET) -> np.ndarray:
    """Recorta al centro para llenar la relación 9:16 sin deformar."""
    h, w = img.shape[:2]
    if w / h > target:
        nw = int(round(h * target))
        x0 = (w - nw) // 2
        return img[:, x0:x0 + nw]
    nh = int(round(w / target))
    y0 = (h - nh) // 2
    return img[y0:y0 + nh, :]


def load_plate(path: str | Path, width: int = 1188) -> np.ndarray:
    """Imagen de origen como plate 9:16 con un 10 % de aire para el zoom."""
    img = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(path)
    plate = cover_crop(img)
    h, w = plate.shape[:2]
    scale = width / w
    if abs(scale - 1.0) > 0.01:
        plate = cv2.resize(plate, (int(round(w * scale)), int(round(h * scale))), interpolation=cv2.INTER_LANCZOS4)
    return plate


def load_plate_height(path: str | Path, height: int = 2112) -> np.ndarray:
    """Plate a altura fija: conserva todo el ancho del original.

    Sirve para material apaisado (fachada) donde el encuadre 9:16 no debe
    recortarse de golpe: la cámara panea dentro del plate completo.
    """
    img = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(path)
    h, w = img.shape[:2]
    scale = height / h
    if abs(scale - 1.0) > 0.01:
        img = cv2.resize(img, (int(round(w * scale)), height), interpolation=cv2.INTER_LANCZOS4)
    return img


class VideoReader:
    """Lee un video de forma secuencial y devuelve plates 9:16."""

    def __init__(self, path: str | Path, width: int = 972):
        self.path = str(path)
        self.cap = cv2.VideoCapture(self.path)
        if not self.cap.isOpened():
            raise FileNotFoundError(path)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30.0
        self.count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.width = width
        self._index = -1
        self._frame: np.ndarray | None = None

    def frame_at(self, seconds: float) -> np.ndarray:
        idx = int(round(seconds * self.fps))
        idx = max(0, min(idx, self.count - 1))
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
                raise RuntimeError(f"No se pudo leer {self.path} en {seconds:.2f}s")
            self._frame = self._prepare(frame)
            self._index = idx
        return self._frame

    def _prepare(self, frame: np.ndarray) -> np.ndarray:
        plate = cover_crop(frame)
        h, w = plate.shape[:2]
        if w < self.width:
            scale = self.width / w
            plate = cv2.resize(plate, (int(round(w * scale)), int(round(h * scale))), interpolation=cv2.INTER_LANCZOS4)
        return plate

    def close(self) -> None:
        self.cap.release()


def sample_keys(keys, t: float) -> tuple[float, float, float, float]:
    """Interpola zoom, centro y rotación entre keyframes con easing suave."""
    if t <= keys[0].t:
        k = keys[0]
        return k.zoom, k.cx, k.cy, k.rot
    if t >= keys[-1].t:
        k = keys[-1]
        return k.zoom, k.cx, k.cy, k.rot
    for a, b in zip(keys, keys[1:]):
        if a.t <= t <= b.t:
            u = clamp01((t - a.t) / max(1e-6, b.t - a.t))
            e = ease_in_out_cubic(u)
            return (
                a.zoom + (b.zoom - a.zoom) * e,
                a.cx + (b.cx - a.cx) * e,
                a.cy + (b.cy - a.cy) * e,
                a.rot + (b.rot - a.rot) * e,
            )
    k = keys[-1]
    return k.zoom, k.cx, k.cy, k.rot


def camera_frame(
    plate: np.ndarray,
    zoom: float,
    cx: float,
    cy: float,
    rot: float = 0.0,
    shake: float = 0.0,
    seed: int = 0,
) -> np.ndarray:
    """Muestrea el plate con una cámara virtual (zoom, paneo, rotación, vibración)."""
    ph, pw = plate.shape[:2]
    zoom = max(1.0, zoom)
    theta = math.radians(rot)
    cos, sin = math.cos(theta), math.sin(theta)

    sx, sy = (W / 2) / zoom, (H / 2) / zoom
    ex = abs(sx * cos) + abs(sy * sin)
    ey = abs(sx * sin) + abs(sy * cos)
    px = min(max(cx * pw, ex), pw - ex) if pw > 2 * ex else pw / 2
    py = min(max(cy * ph, ey), ph - ey) if ph > 2 * ey else ph / 2

    if shake:
        rng = np.random.default_rng(seed)
        jx = rng.normal(0, shake)
        jy = rng.normal(0, shake)
        jr = rng.normal(0, shake * 0.02)
        theta += math.radians(jr)
        cos, sin = math.cos(theta), math.sin(theta)
        px += jx
        py += jy

    m = np.array(
        [
            [cos / zoom, sin / zoom, px - (cos * W / 2 + sin * H / 2) / zoom],
            [-sin / zoom, cos / zoom, py - (-sin * W / 2 + cos * H / 2) / zoom],
        ],
        dtype=np.float32,
    )
    return cv2.warpAffine(
        plate,
        m,
        (W, H),
        flags=cv2.INTER_CUBIC | cv2.WARP_INVERSE_MAP,
        borderMode=cv2.BORDER_REFLECT,
    )


# ---------------------------------------------------------------------------
# Etalonaje
# ---------------------------------------------------------------------------

def build_lut(contrast: float = 1.03, teal_shadows: float = 0.040, warm_highs: float = 0.020, lift: float = 0.002) -> np.ndarray:
    x = np.arange(256, dtype=np.float32) / 255.0
    base = np.clip((x - 0.5) * contrast + 0.5 + lift, 0, 1)
    shadow = (1 - base) ** 2
    high = base ** 2
    r = np.clip(base + warm_highs * high - teal_shadows * 0.35 * shadow, 0, 1)
    g = np.clip(base + teal_shadows * 0.40 * shadow + warm_highs * 0.15 * high, 0, 1)
    b = np.clip(base + teal_shadows * shadow - warm_highs * 0.30 * high, 0, 1)
    lut = np.stack([b, g, r], axis=-1)  # BGR
    return (lut * 255).round().astype(np.uint8).reshape(256, 1, 3)


def highlight_shoulder(frame: np.ndarray, start: float = 0.80, strength: float = 0.75) -> np.ndarray:
    """Comprime sólo las altas luces. No sube nada: mata el clipping sin aplanar el tono medio.

    Para x > `start` la curva resta strength * (x-start)^2 / (1-start), de modo que
    x=start queda igual y x=1 acaba en 1 - strength*(1-start).
    """
    if strength <= 0:
        return frame
    x = frame.astype(np.float32) / 255.0
    over = np.clip(x - start, 0.0, None)
    y = x - strength * over * over / (1.0 - start)
    return np.clip(y * 255.0, 0, 255).astype(np.uint8)


def grade(frame: np.ndarray, lut: np.ndarray, saturation: float = 0.86) -> np.ndarray:
    out = cv2.LUT(frame, lut)
    if abs(saturation - 1.0) > 0.005:
        gray = cv2.cvtColor(out, cv2.COLOR_BGR2GRAY)
        gray3 = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        out = cv2.addWeighted(out, saturation, gray3, 1 - saturation, 0)
    return highlight_shoulder(out)


@lru_cache(maxsize=1)
def vignette_mask() -> np.ndarray:
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    cx, cy = W / 2, H * 0.48
    d = np.sqrt(((xx - cx) / (W * 0.62)) ** 2 + ((yy - cy) / (H * 0.68)) ** 2)
    mask = np.clip(1.02 - 0.30 * d ** 2.2, 0.55, 1.0)
    return mask.astype(np.float32)[..., None]


@lru_cache(maxsize=1)
def grain_bank(count: int = 10) -> tuple[np.ndarray, ...]:
    rng = np.random.default_rng(7)
    return tuple(rng.normal(0, 4.2, (H, W, 1)).astype(np.int16) for _ in range(count))


def finish(frame: np.ndarray, grain_index: int, grain: float = 1.0, sharpen: float = 0.0) -> np.ndarray:
    if sharpen:
        # Nitidez en Y solamente: aplicarla a los tres canales creaba halos de color
        # (bordes rojo/cian) sobre los blancos, que es justo donde se notaba el brillo.
        ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
        y, cr, cb = cv2.split(ycrcb)
        blur = cv2.GaussianBlur(y, (0, 0), 1.2)
        y = cv2.addWeighted(y, 1 + sharpen, blur, -sharpen, 0)
        frame = cv2.cvtColor(cv2.merge([y, cr, cb]), cv2.COLOR_YCrCb2BGR)
    f = frame.astype(np.float32) * vignette_mask()
    f += grain_bank()[grain_index % len(grain_bank())] * grain
    return np.clip(f, 0, 255).astype(np.uint8)
