#!/usr/bin/env python3
"""Render de la pieza de marca Abyss (15.00 s, 1080x1920, 60 fps).

Uso:
    python3 src/fetch_material.py     # material/ desde el repo abysstattoo
    python3 src/audio.py              # render/soundtrack.wav
    python3 src/render.py             # master + derivadas + piezas

Salidas en out/:
    abyss_marca_15s_1080x1920_60fps.mp4    máster social
    abyss_marca_15s_1080x1920_30fps.mp4    derivada web
    abyss_marca_15s_720x1280_preview.mp4   previa liviana
    cover_emblema.jpg · poster_cta.jpg · storyboard.jpg · manifest.json
"""

from __future__ import annotations

import math
import subprocess
import sys
import time
from pathlib import Path

import cv2
import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw

from audio import build as build_audio
from brand import (
    CREAM,
    FPS,
    FRAMES,
    H,
    HUESO,
    OBSIDIAN,
    SAGE,
    TEAL,
    W,
    clamp01,
    ease_in_out_cubic,
    ease_out_cubic,
    ease_out_expo,
    paste_text,
    radial_glow,
    rgba,
    shimmer,
)
from media import (
    VideoReader, build_lut, camera_frame, finish, grade, load_plate, load_plate_height, sample_keys,
)
import importlib
import os

# El montaje vive en un módulo de timeline. Por defecto el de 15 s; con
# ABYSS_TIMELINE=timeline_largo se renderiza la versión de 18 s.
TL = importlib.import_module(os.environ.get("ABYSS_TIMELINE", "timeline"))
RING_R = TL.RING_R
EMBLEM_CY = TL.EMBLEM_CY
EMBLEM_IN = TL.EMBLEM_IN
EMBLEM_SIZE = TL.EMBLEM_SIZE
SHIMMER_AT = TL.SHIMMER_AT
SHIMMER_DUR = TL.SHIMMER_DUR
SHOTS = TL.SHOTS
TEXTS = TL.TEXTS
TOTAL = TL.TOTAL
STORY_TIMES = TL.STORY_TIMES
COVER_TIME = TL.COVER_TIME
POSTER_TIME = TL.POSTER_TIME

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
WORK = ROOT / "work"
FF = imageio_ffmpeg.get_ffmpeg_exe()

# Nombres de archivo por versión: abyss_marca_15s_… / abyss_marca_18s_…
SLUG = os.environ.get("ABYSS_SLUG", f"abyss_marca_{int(round(TOTAL))}s")
DUR_TAG = f"{TOTAL:.2f}"
# Las piezas de 15 s conservan sus nombres; las demás llevan sufijo de versión.
SUFFIX = "" if int(round(TOTAL)) == 15 else f"_{int(round(TOTAL))}s"


def log(msg: str) -> None:
    print(msg, flush=True)


# ---------------------------------------------------------------------------
# Recursos
# ---------------------------------------------------------------------------

class Resources:
    def __init__(self) -> None:
        self.lut = build_lut()
        self.readers: dict[str, VideoReader] = {}
        self.plates: dict[str, np.ndarray] = {}
        self.emblem = self._load_emblem()
        self.glow = radial_glow((W, H), SAGE, 0.60)

    def _load_emblem(self) -> Image.Image:
        from brand import REPO
        img = Image.open(REPO / "assets" / "reel_plates" / "emblema_abyss_alpha.png").convert("RGBA")
        img = img.resize((EMBLEM_SIZE, EMBLEM_SIZE), Image.LANCZOS)
        return img

    def video(self, path: str) -> VideoReader:
        if path not in self.readers:
            self.readers[path] = VideoReader(path)
        return self.readers[path]

    def plate(self, path: str, wide: bool = False) -> np.ndarray:
        key = f"{'w' if wide else 'c'}:{path}"
        if key not in self.plates:
            self.plates[key] = load_plate_height(path) if wide else load_plate(path)
        return self.plates[key]

    def close(self) -> None:
        for r in self.readers.values():
            r.close()


# ---------------------------------------------------------------------------
# Capas
# ---------------------------------------------------------------------------

def band(img: Image.Image, y0: int, y1: int, strength: float = 0.62) -> None:
    """Degradado oscuro detrás de un bloque de texto para asegurar lectura."""
    if y1 <= y0:
        return
    h = y1 - y0
    yy = np.arange(h, dtype=np.float32) / max(1, h - 1)
    prof = np.clip(np.sin(yy * math.pi), 0, 1) ** 0.7 * strength
    prof = prof[:, None]
    arr = np.zeros((h, W, 4), dtype=np.uint8)
    arr[..., 0], arr[..., 1], arr[..., 2] = 20, 16, 13
    arr[..., 3] = (prof * 255).astype(np.uint8)
    img.alpha_composite(Image.fromarray(arr, "RGBA"), (0, y0))


def text_bands(img: Image.Image, t: float) -> None:
    """Oscurece sólo la franja que ocupan los textos visibles."""
    for txt in TEXTS:
        if txt.t_in - 0.05 <= t <= txt.t_out:
            band(img, txt.y - 54, txt.y + txt.size + 46, 0.5)


def draw_texts(img: Image.Image, t: float) -> None:
    for txt in TEXTS:
        if t < txt.t_in or t > txt.t_out:
            continue
        p = ease_out_cubic((t - txt.t_in) / txt.enter)
        alpha = p * clamp01((txt.t_out - t) / txt.exit)
        if alpha <= 0.004:
            continue
        dy = 0.0
        scale = 1.0
        clip = None
        if txt.mode == "rise":
            dy = (1 - p) * 26
        elif txt.mode == "scale":
            scale = 0.945 + 0.055 * p
        if txt.clip:
            clip = p
        paste_text(
            img, txt.value, txt.font, txt.size, txt.color, txt.x,
            int(round(txt.y + dy)), alpha=alpha, scale=scale,
            tracking=txt.tracking, clip=clip, anchor=txt.anchor,
        )


def emblem_layer(res: Resources, local: float) -> tuple[Image.Image, float]:
    """Devuelve el emblema transformado y su opacidad global para un tiempo local."""
    if local < 0:
        return res.emblem, 0.0
    appear = ease_out_cubic(local / 0.28)
    settle = ease_out_expo(local / 1.10)
    scale = 0.86 + 0.14 * settle
    angle = -7.0 * (1.0 - settle)
    sweep = clamp01((local - 0.06) / 0.72)

    layer = res.emblem
    if abs(angle) > 0.05:
        layer = layer.rotate(angle, resample=Image.BICUBIC, expand=False)
    if abs(scale - 1.0) > 0.002:
        size = max(1, int(layer.width * scale))
        layer = layer.resize((size, size), Image.LANCZOS)

    # barrido angular: el emblema se dibuja desde las 12 en sentido horario
    if sweep < 0.999:
        mask = Image.new("L", layer.size, 0)
        d = ImageDraw.Draw(mask)
        r = layer.width
        d.pieslice((-r, -r, 2 * r, 2 * r), start=-90, end=-90 + 360 * sweep, fill=255)
        a = layer.getchannel("A").point(lambda v: v)
        layer = layer.copy()
        layer.putalpha(Image.composite(a, Image.new("L", layer.size, 0), mask))

    if appear < 0.999:
        layer = layer.copy()
        layer.putalpha(layer.getchannel("A").point(lambda v: int(v * appear)))
    return layer, appear


def draw_ring(img: Image.Image, local: float) -> None:
    """Anillo fino que se traza alrededor del emblema entre 11.9 y 12.6 s."""
    p = clamp01((local - 0.35) / 0.9)
    if p <= 0 or p >= 1.0:
        return
    cx, cy = W // 2, EMBLEM_CY
    r = RING_R
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    a = int(190 * min(1.0, p * 3))
    d.arc([cx - r, cy - r, cx + r, cy + r], start=-90, end=-90 + 360 * ease_in_out_cubic(p),
          fill=rgba(HUESO, a), width=2)
    img.alpha_composite(layer)


def compose(t: float, res: Resources) -> tuple[Image.Image, str]:
    shot = next(s for s in SHOTS if s.start <= t < s.end or (s is SHOTS[-1] and t >= s.end))
    local = t - shot.start
    label = shot.label

    if shot.kind == "emblem":
        base = Image.new("RGBA", (W, H), rgba(OBSIDIAN))
        glow_a = 0.55 + 0.45 * clamp01(local / 0.8)
        g = res.glow.copy()
        g.putalpha(g.getchannel("A").point(lambda v: int(v * glow_a)))
        base.alpha_composite(g)
        band(base, 1180, 1620, 0.45)
        return base, label

    zoom, cx, cy, rot = sample_keys(shot.keys, local)
    if shot.kind == "video":
        plate = res.video(shot.source).frame_at(shot.src_start + local * shot.src_speed)
    else:
        plate = res.plate(shot.source, wide=shot.wide)

    frame = camera_frame(plate, zoom, cx, cy, rot, shot.shake, seed=int(t * FPS))
    if shot.exposure != 1.0:
        frame = np.clip(frame.astype(np.float32) * shot.exposure, 0, 255).astype(np.uint8)
    frame = grade(frame, res.lut, saturation=0.86)
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).convert("RGBA")
    return img, label


def render_frame(t: float, res: Resources, grain_index: int) -> np.ndarray:
    img, _ = compose(t, res)
    shot = next(s for s in SHOTS if s.start <= t < s.end or (s is SHOTS[-1] and t >= s.end))

    if shot.kind == "emblem":
        local = t - EMBLEM_IN
        draw_ring(img, local)
        layer, _ = emblem_layer(res, local)
        x = (W - layer.width) // 2
        y = EMBLEM_CY - layer.height // 2
        img.alpha_composite(layer, (x, y))
        if SHIMMER_AT <= t <= SHIMMER_AT + SHIMMER_DUR:
            p = (t - SHIMMER_AT) / SHIMMER_DUR
            img = Image.alpha_composite(img, Image.new("RGBA", (W, H), (0, 0, 0, 0)))
            swept = shimmer(layer, p, width=240)
            clear = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            clear.paste(swept, (x, y), swept)
            img = Image.alpha_composite(img, clear)
        draw_texts(img, t)
    else:
        text_bands(img, t)
        draw_texts(img, t)

    # impacto en los cortes: un frame de luz muy contenido
    for cut in [s.start for s in SHOTS]:
        if 0.0 < t - cut < 1.0 / FPS:
            img = Image.alpha_composite(img, Image.new("RGBA", (W, H), (246, 241, 237, 16)))
            break

    rgb = np.array(img.convert("RGB"))
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    return finish(bgr, grain_index, grain=1.0, sharpen=0.18)


# ---------------------------------------------------------------------------
# Codificación y piezas
# ---------------------------------------------------------------------------

def encode(frames_iter, out_path: Path, wav: Path | None, crf: int = 20, preset: str = "medium") -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        FF, "-y", "-hide_banner", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
    ]
    if wav is not None and wav.exists():
        cmd += ["-i", str(wav), "-c:a", "aac", "-b:a", "192k", "-ar", "48000"]
    cmd += [
        "-c:v", "libx264", "-preset", preset, "-crf", str(crf), "-pix_fmt", "yuv420p",
        "-profile:v", "high", "-level", "4.2", "-tune", "film",
        "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
        "-movflags", "+faststart", "-shortest", str(out_path),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    assert proc.stdin is not None
    for frame in frames_iter:
        # OJO: las capas se componen en BGR (OpenCV); el pipe va en RGB.
        # Sin esta conversión el mp4 sale con rojo y azul intercambiados.
        proc.stdin.write(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError(f"ffmpeg falló con {out_path}")


def frame_at(t: float, res: Resources) -> np.ndarray:
    return render_frame(t, res, grain_index=int(round(t * FPS)))


def derive(master: Path, wav: Path) -> None:
    d30 = OUT / f"{SLUG}_1080x1920_30fps.mp4"
    prev = OUT / f"{SLUG}_720x1280_preview.mp4"
    subprocess.run([FF, "-y", "-hide_banner", "-loglevel", "error", "-i", str(master),
                    "-t", DUR_TAG, "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "21",
                    "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", str(d30)], check=True)
    subprocess.run([FF, "-y", "-hide_banner", "-loglevel", "error", "-i", str(master),
                    "-t", DUR_TAG, "-vf", "scale=720:1280:flags=lanczos", "-c:v", "libx264", "-preset", "medium",
                    "-crf", "27", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k",
                    "-movflags", "+faststart", str(prev)], check=True)


def pieces(res: Resources) -> None:
    cover = Image.fromarray(cv2.cvtColor(frame_at(COVER_TIME, res), cv2.COLOR_BGR2RGB))
    cover.save(OUT / f"cover_emblema{SUFFIX}.jpg", quality=92)
    poster = Image.fromarray(cv2.cvtColor(frame_at(POSTER_TIME, res), cv2.COLOR_BGR2RGB))
    poster.save(OUT / f"poster_cta{SUFFIX}.jpg", quality=92)

    tw, th = 216, 384
    cols = 7
    rows = max(2, math.ceil(len(STORY_TIMES) / cols))
    sheet = Image.new("RGB", (cols * (tw + 10) + 10, rows * (th + 34) + 10), (20, 18, 16))
    d = ImageDraw.Draw(sheet)
    for i, t in enumerate(STORY_TIMES):
        img = Image.fromarray(cv2.cvtColor(frame_at(t, res), cv2.COLOR_BGR2RGB)).resize((tw, th), Image.LANCZOS)
        x = 10 + (i % cols) * (tw + 10)
        y = 10 + (i // cols) * (th + 34)
        sheet.paste(img, (x, y))
        d.text((x + 2, y + th + 8), f"{t:.1f}s", fill=(190, 185, 175))
    sheet.save(OUT / f"storyboard{SUFFIX}.jpg", quality=90)


def main() -> int:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    res = Resources()
    wav = ROOT / "render" / "soundtrack.wav"
    if not wav.exists():
        log("audio · sintetizando banda sonora")
        build_audio(wav)

    log(f"render · {FRAMES} frames a {FPS} fps")
    master = OUT / f"{SLUG}_1080x1920_60fps.mp4"

    def frames():
        for i in range(FRAMES):
            t = i / FPS
            yield render_frame(t, res, grain_index=i)
            if i % 60 == 0:
                log(f"  frame {i:4d}/{FRAMES}  {time.time() - t0:6.1f}s")

    encode(frames(), master, wav)
    log(f"máster listo en {time.time() - t0:.1f}s")
    derive(master, wav)
    log("derivadas listas")
    pieces(res)
    res.close()
    log("piezas listas")
    log(f"total {time.time() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
