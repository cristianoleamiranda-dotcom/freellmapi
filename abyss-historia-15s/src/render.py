#!/usr/bin/env python3
"""Render de la historia de 15 s de Abyss Tattoo Studio.

Uso:
    python3 src/audio.py          # genera render/soundtrack.wav
    python3 src/render.py         # renderiza máster, derivada y piezas

Salidas en out/:
    abyss_historia_15s_1080x1920_60fps.mp4   máster social
    abyss_historia_15s_1080x1920_30fps.mp4   derivada web
    cover_hook.jpg · poster_cta.jpg · storyboard.jpg · manifest.json
"""

from __future__ import annotations

import hashlib
import json
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
    MONTSERRAT_500,
    MONTSERRAT_600,
    MONTSERRAT_700,
    OBSIDIAN,
    REPO,
    SAGE,
    TEAL,
    W,
    clamp01,
    ease_out_cubic,
    hairline,
    paste_text,
    pill,
    radial_glow,
    rgba,
    shimmer,
)
from media import VideoReader, build_lut, camera_frame, finish, grade, load_plate, sample_keys
from timeline import (
    BELL,
    CLOSE_START,
    CLOSE_TEXTS,
    CTA_IN,
    CTA_OUT,
    CTA_TEXT,
    CTA_Y,
    MOSAIC,
    MOSAIC_START,
    SHOTS,
    TOTAL,
)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
WORK = ROOT / "render"
FF = imageio_ffmpeg.get_ffmpeg_exe()

WIDTH_IMAGE_PLATE = 1188
WIDTH_VIDEO_PLATE = 972

STORY_TIMES = [0.9, 2.7, 4.5, 6.3, 7.8, 9.0, 9.8, 10.3, 10.7, 11.1, 12.4, 13.4]
COVER_TIME = 1.30
POSTER_TIME = 13.6


def log(message: str) -> None:
    print(message, flush=True)


# ---------------------------------------------------------------------------
# Capa de texto
# ---------------------------------------------------------------------------

DECOR = {
    "P1 macro aguja": [(108, 470, 118, 0.55)],
    "P2 lobo": [(108, 1332, 96, 2.10)],
    "P3 manga": [(108, 410, 96, 3.92)],
    "P4 ink wipe": [(108, 1350, 96, 5.72)],
    "P5 helix": [(108, 414, 96, 7.50)],
    "P6 fachada": [(108, 1366, 96, 8.70)],
}


def draw_text(img: Image.Image, txt, t: float) -> None:
    if t < txt.t_in or t > txt.t_out:
        return
    p = ease_out_cubic((t - txt.t_in) / txt.enter)
    a_out = clamp01((txt.t_out - t) / txt.exit)
    alpha = p * a_out
    if alpha <= 0.004:
        return

    dy = 0.0
    scale = 1.0
    clip = None
    if txt.mode == "rise":
        dy = (1 - p) * 26
    elif txt.mode == "scale":
        scale = 0.945 + 0.055 * p
    elif txt.mode == "wipe":
        clip = p
    if txt.clip:
        clip = p

    paste_text(
        img,
        txt.value,
        txt.font,
        txt.size,
        txt.color,
        txt.x,
        int(round(txt.y + dy)),
        alpha=alpha,
        scale=scale,
        tracking=txt.tracking,
        clip=clip,
    )


def draw_center(img: Image.Image, txt, t: float) -> None:
    if t < txt.t_in or t > txt.t_out:
        return
    p = ease_out_cubic((t - txt.t_in) / txt.enter)
    alpha = p * clamp01((txt.t_out - t) / txt.exit)
    if alpha <= 0.004:
        return
    scale = 0.95 + 0.05 * p if txt.mode == "scale" else 1.0
    dy = (1 - p) * 22 if txt.mode == "rise" else 0.0
    paste_text(
        img, txt.value, txt.font, txt.size, txt.color,
        txt.x, int(round(txt.y + dy)),
        alpha=alpha, scale=scale, tracking=txt.tracking, anchor="center",
    )


def draw_decor(img: Image.Image, label: str, t: float, start: float) -> None:
    draw = ImageDraw.Draw(img, "RGBA")
    for x, y, length, at in DECOR.get(label, []):
        p = clamp01((t - at) / 0.5)
        if p <= 0:
            continue
        hairline(draw, x, y, int(length * ease_out_cubic(p)), TEAL, alpha=int(190 * p))


# ---------------------------------------------------------------------------
# Emblema y cierre
# ---------------------------------------------------------------------------

class Emblem:
    def __init__(self) -> None:
        src = REPO / "assets/reel_plates/emblema_abyss_alpha.png"
        self.image = Image.open(src).convert("RGBA")
        self.bg = self._background()
        self.pill = pill(CTA_TEXT, MONTSERRAT_700, 40, OBSIDIAN, CREAM, tracking=1.0, pad_x=44, pad_y=22)

    def _background(self) -> Image.Image:
        base = Image.new("RGBA", (W, H), rgba(OBSIDIAN))
        panel = Image.new("RGBA", (W, H), rgba("#0F0C0A"))
        base = Image.alpha_composite(base, panel)
        glow = radial_glow((W, H), SAGE, strength=0.6)
        return Image.alpha_composite(base, glow)

    def frame(self, t: float, index: int) -> Image.Image:
        lt = t - CLOSE_START
        img = self.bg.copy()

        # Halos concéntricos que respiran detrás del emblema
        draw = ImageDraw.Draw(img, "RGBA")
        cx, cy = W // 2, 640
        for i, radius in enumerate((330, 404, 470)):
            r = radius * (1 + 0.012 * np.sin(lt * 1.4 + i))
            alpha = int((26 - i * 7) * clamp01(lt / 0.8))
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=rgba(SAGE, alpha), width=2)

        # Emblema con asentamiento (sin rebote: arquetipo Premium)
        p = ease_out_cubic(clamp01(lt / 0.95))
        scale = (1.07 - 0.07 * p) * (1 + 0.018 * clamp01(lt / 3.6))
        alpha = clamp01(lt / 0.55)
        size = int(560 * scale)
        emblem = self.image.resize((size, size), Image.LANCZOS)
        if alpha < 0.999:
            a = emblem.getchannel("A").point(lambda v: int(v * alpha))
            emblem.putalpha(a)
        img.alpha_composite(emblem, (cx - size // 2, cy - size // 2))

        # Título del cierre
        for txt in CLOSE_TEXTS[:1]:
            draw_center(img, txt, t)

        # Hairline bajo el título
        pl = clamp01((t - 11.95) / 0.5)
        if pl > 0:
            hairline(ImageDraw.Draw(img, "RGBA"), (W - 180) // 2, 1152, int(180 * ease_out_cubic(pl)), TEAL, alpha=int(200 * pl))

        # CTA: pastilla con barrido especular
        if CTA_IN <= t <= CTA_OUT:
            pin = ease_out_cubic((t - CTA_IN) / 0.42)
            aout = clamp01((CTA_OUT - t) / 0.2)
            a = pin * aout
            layer = self.pill
            sweep = clamp01((t - CTA_IN - 0.18) / 1.25)
            if 0 < sweep < 1:
                layer = shimmer(layer, sweep)
            if a < 0.999:
                layer = layer.copy()
                alpha_ch = layer.getchannel("A").point(lambda v: int(v * a))
                layer.putalpha(alpha_ch)
            img.alpha_composite(layer, ((W - layer.width) // 2, int(CTA_Y + (1 - pin) * 24)))

        for txt in CLOSE_TEXTS[1:]:
            draw_center(img, txt, t)

        return img


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------

class Renderer:
    def __init__(self) -> None:
        self.images: dict[str, np.ndarray] = {}
        self.readers: dict[str, VideoReader] = {}
        self.lut = build_lut()
        self.emblem = Emblem()
        self.saved: dict[str, Image.Image] = {}

    def plate_for(self, path: str) -> np.ndarray:
        plate = self.images.get(path)
        if plate is None:
            plate = load_plate(path, width=WIDTH_IMAGE_PLATE)
            self.images[path] = plate
        return plate

    def plate(self, shot) -> np.ndarray:
        if shot.kind == "video":
            reader = self.readers.get(shot.source)
            if reader is None:
                reader = VideoReader(shot.source, width=WIDTH_VIDEO_PLATE)
                self.readers[shot.source] = reader
            seconds = shot.src_start + (self.current_t - shot.start) * shot.src_speed
            return reader.frame_at(seconds)
        plate = self.images.get(shot.source)
        if plate is None:
            plate = load_plate(shot.source, width=WIDTH_IMAGE_PLATE)
            self.images[shot.source] = plate
        return plate

    def shot_for(self, t: float):
        if t < MOSAIC_START:
            for shot in SHOTS:
                if shot.start <= t < shot.end:
                    return shot, None
            return SHOTS[-1], None
        if t < CLOSE_START:
            for cell in MOSAIC:
                if cell.start <= t < cell.end:
                    return None, cell
            return None, MOSAIC[-1]
        return None, None

    def render_frame(self, t: float, index: int) -> Image.Image:
        self.current_t = t
        shot, cell = self.shot_for(t)

        if shot is None and cell is None:
            return self.emblem.frame(t, index)

        if cell is not None:
            plate = self.plate_for(cell.source)
            local = t - cell.start
            zoom, cx, cy, rot = sample_keys(cell.keys, local)
            frame = camera_frame(plate, zoom, cx, cy, rot, 0.0, index)
            frame = grade(frame, self.lut)
            frame = finish(frame, index, grain=1.0, sharpen=0.0)
            img = to_pil(frame)
            draw_text(img, cell.text, t)
            return finish_pil(img)

        plate = self.plate(shot)
        local = t - shot.start
        zoom, cx, cy, rot = sample_keys(shot.keys, local)
        frame = camera_frame(plate, zoom, cx, cy, rot, shot.shake, index)
        frame = grade(frame, self.lut)
        frame = finish(frame, index, grain=1.0, sharpen=0.22 if shot.kind == "video" else 0.0)

        img = to_pil(frame)
        for txt in shot.texts:
            draw_text(img, txt, t)
        draw_decor(img, shot.label, t, shot.start)
        return img

    def run(self) -> dict:
        OUT.mkdir(parents=True, exist_ok=True)
        WORK.mkdir(parents=True, exist_ok=True)
        audio = WORK / "soundtrack.wav"
        log("· sintetizando audio")
        build_audio(audio)

        master = OUT / "abyss_historia_15s_1080x1920_60fps.mp4"
        raw_cmd = [
            FF, "-y", "-hide_banner", "-loglevel", "error",
            "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
            "-i", str(audio),
            "-c:v", "libx264", "-preset", "slow", "-crf", "19",
            "-profile:v", "high", "-level", "4.2", "-pix_fmt", "yuv420p",
            "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-shortest", "-movflags", "+faststart", str(master),
        ]
        log("· renderizando 900 frames a 60 fps")
        proc = subprocess.Popen(raw_cmd, stdin=subprocess.PIPE)
        started = time.time()
        try:
            for index in range(FRAMES):
                t = index / FPS
                img = self.render_frame(t, index)
                frame = cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2BGR)
                proc.stdin.write(frame.tobytes())
                if index % 90 == 0:
                    log(f"  {index:4d}/{FRAMES}  {time.time() - started:5.1f}s")
                for moment, key in ((COVER_TIME, "cover"), (POSTER_TIME, "poster")):
                    if abs(t - moment) < 0.5 / FPS:
                        self.saved[key] = img.convert("RGB")
                for i, moment in enumerate(STORY_TIMES):
                    if abs(t - moment) < 0.5 / FPS:
                        thumb = img.convert("RGB").copy()
                        thumb.thumbnail((360, 640), Image.LANCZOS)
                        self.saved[f"story{i}"] = thumb
        finally:
            proc.stdin.close()
            code = proc.wait()
        if code != 0:
            raise RuntimeError(f"ffmpeg terminó con código {code}")

        log("· derivada 30 fps")
        web = OUT / "abyss_historia_15s_1080x1920_30fps.mp4"
        subprocess.run(
            [
                FF, "-y", "-hide_banner", "-loglevel", "error", "-i", str(master),
                "-vf", "fps=30,scale=1080:1920:flags=lanczos",
                "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-profile:v", "high",
                "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart",
                str(web),
            ],
            check=True,
        )

        log("· piezas: portada, póster, storyboard")
        cover = self.saved.get("cover")
        if cover is not None:
            cover.save(OUT / "cover_hook.jpg", quality=94, subsampling=1)
        poster = self.saved.get("poster")
        if poster is not None:
            poster.save(OUT / "poster_cta.jpg", quality=94, subsampling=1)
        self.write_storyboard()

        manifest = {
            "project": "Abyss Tattoo Studio · historia 15 s",
            "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "duration": TOTAL,
            "fps": FPS,
            "size": [W, H],
            "beat": 0.6,
            "files": {},
        }
        for path in sorted(OUT.glob("*")):
            if path.is_file() and path.suffix in {".mp4", ".jpg"}:
                manifest["files"][path.name] = {
                    "bytes": path.stat().st_size,
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                }
        (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
        for reader in self.readers.values():
            reader.close()
        log(f"✓ listo en {time.time() - started:.1f}s → {OUT}")
        return manifest

    def write_storyboard(self) -> None:
        thumbs = [self.saved.get(f"story{i}") for i in range(len(STORY_TIMES))]
        thumbs = [t for t in thumbs if t is not None]
        if not thumbs:
            return
        cols = 6
        tw, th = thumbs[0].size
        label_h = 54
        rows = (len(thumbs) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * tw, rows * (th + label_h)), (20, 16, 13))
        draw = ImageDraw.Draw(sheet)
        for i, thumb in enumerate(thumbs):
            x = (i % cols) * tw
            y = (i // cols) * (th + label_h)
            sheet.paste(thumb, (x, y))
            draw.text((x + 8, y + th + 8), f"{STORY_TIMES[i]:0.2f}s", fill=(158, 196, 186))
        sheet.save(OUT / "storyboard.jpg", quality=92)


def to_pil(frame: np.ndarray) -> Image.Image:
    return Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).convert("RGBA")


def finish_pil(img: Image.Image) -> Image.Image:
    return img.convert("RGB")


if __name__ == "__main__":
    Renderer().run()
