"""Render offline: compone fotograma a fotograma y encodea con ffmpeg.

Salida: 1 reel 18 s + 3 historias 6 s, 1080×1920 30 fps, H.264 High,
grano de película, viñeta, halación y gate weave en cada fotograma.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

import brand as B
import timeline as T
from brand import W, H, FPS
from kinetic import render_scene, whip_mix
from media import VideoReader, duotone, grade, make_plate

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
DB = ROOT.parent / "dropbox"
M = ROOT / "material"

WARM_SHADOW = (12, 9, 8)
WARM_MID = (122, 74, 46)
WARM_HIGH = (233, 205, 168)


# ---------------------------------------------------------------------------
# Plates editados (NO TRANSABLE: todo material entra etalonado)
# ---------------------------------------------------------------------------
def _rgb(a: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(a, cv2.COLOR_BGR2RGB)


def _crop_frac(img: np.ndarray, x0, y0, x1, y1) -> np.ndarray:
    h, w = img.shape[:2]
    return img[int(y0 * h):int(y1 * h), int(x0 * w):int(x1 * w)]


def build_plates() -> dict:
    from media import cover_crop
    p = {}
    hero = VideoReader(M / "film" / "hero_film.mp4", width=1500, aspect=W / H)
    p["artist"] = _rgb(duotone(grade(hero.frame_at(0.70)), WARM_SHADOW, WARM_MID, WARM_HIGH, 0.55))
    p["session"] = _rgb(duotone(grade(_rgb2bgr(DB / "AV_SEL_28_0188.jpg")), WARM_SHADOW, WARM_MID, WARM_HIGH, 0.55))
    p["leg"] = _rgb(duotone(grade(_rgb2bgr(DB / "18.jpg")), WARM_SHADOW, WARM_MID, WARM_HIGH, 0.60))
    p["forearm"] = _rgb(duotone(grade(_rgb2bgr(DB / "AV_SEL_27_0180.jpg")), WARM_SHADOW, WARM_MID, WARM_HIGH, 0.60))
    ear = cover_crop(_rgb2bgr(DB / "1000025791.JPG (1).webp"), 0.85)
    p["ear"] = _rgb(duotone(grade(ear), WARM_SHADOW, WARM_MID, WARM_HIGH, 0.50))
    p["clown"] = _rgb(duotone(grade(_rgb2bgr(DB / "IMG-20260914-WA0018.jpg")), WARM_SHADOW, WARM_MID, WARM_HIGH, 0.55))
    p["facade"] = _rgb(grade(_rgb2bgr(DB / "IMG_3290_conv.jpg"), saturation=0.82, contrast=1.12))
    bf = _crop_frac(_rgb2bgr(DB / "Meta_AI_887990597_1133220852580442_6760098012968653658_n_20261102_170329.webp"),
                    0.10, 0.22, 0.90, 0.80)
    p["ring_butterfly"] = _rgb(duotone(grade(bf, saturation=0.55, contrast=1.14), WARM_SHADOW, (112, 102, 94), (238, 232, 226), 0.35))
    rd = _crop_frac(_rgb2bgr(DB / "Meta_AI_883649895_2013744662622229_7114893650517436722_n_20261102_170334.webp"),
                    0.10, 0.22, 0.90, 0.80)
    p["ring_double"] = _rgb(duotone(grade(rd, saturation=0.55, contrast=1.14), WARM_SHADOW, (112, 102, 94), (238, 232, 226), 0.35))
    for k in p:
        p[k] = _plate_width(p[k], 1500)
    # máquina: clip real de proceso (video)
    vr = VideoReader(M / "film" / "hero_film.mp4", width=1300, aspect=W / H)

    def machine(t: float, _vr=vr) -> np.ndarray:
        f = np.clip(_vr.frame_at(2.05 + (t % 6.0) * 0.30).astype(np.float32) * 1.5, 0, 255).astype(np.uint8)
        g = grade(f, contrast=1.02, warm=0.07, saturation=0.80)
        return _rgb(duotone(g, (14, 10, 8), (150, 95, 60), (238, 210, 175), 0.50))

    p["machine"] = machine
    return p


def _rgb2bgr(path) -> np.ndarray:
    img = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(path)
    return img


def _plate_width(img: np.ndarray, width: int) -> np.ndarray:
    h, w = img.shape[:2]
    s = width / w
    if abs(s - 1) > 0.01:
        img = cv2.resize(img, (int(round(w * s)), int(round(h * s))), interpolation=cv2.INTER_LANCZOS4)
    return img


# ---------------------------------------------------------------------------
# Ensamblaje
# ---------------------------------------------------------------------------
def boundaries(scenes, transitions, duration):
    b = [0.0] + [tr["at"] for tr in transitions] + [duration]
    return b


def frame_at(t: float, fi: int, scenes, transitions, bounds, plates) -> np.ndarray:
    # ¿dentro de una ventana de whip?
    for tr in transitions:
        if tr.get("kind") != "whip":
            continue
        d = tr["dur"]
        a = tr["at"]
        if a - d / 2 <= t < a + d / 2:
            k = bounds.index(a) - 1
            out = np.asarray(render_scene(scenes[k], t, plates, fi).convert("RGB"))
            inn = np.asarray(render_scene(scenes[k + 1], t, plates, fi).convert("RGB"))
            p = (t - (a - d / 2)) / d
            return whip_mix(out, inn, p, tr.get("dir", 1))
    k = 0
    for i in range(len(bounds) - 1):
        if bounds[i] <= t < bounds[i + 1]:
            k = i
            break
    else:
        k = len(scenes) - 1
    return np.asarray(render_scene(scenes[k], t, plates, fi).convert("RGB"))


def encode(frames_iter, total: int, path: Path, fps: int = FPS, label: str = "") -> float:
    cmd = [
        str(ROOT / "bin" / "ffmpeg"), "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
        "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
        "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.2",
        "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
        "-movflags", "+faststart", str(path),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    for i, fr in enumerate(frames_iter):
        proc.stdin.write(fr.tobytes())
        if i % 60 == 0:
            el = time.time() - t0
            print(f"  [{label}] {i:4d}/{total}  {el:5.1f}s  ({i / max(el, 1e-6):4.1f} fps)", flush=True)
    proc.stdin.close()
    proc.wait()
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg falló en {path}")
    return time.time() - t0


def render_piece(name: str, scenes, transitions, duration: float, plates: dict,
                 audio: dict | None = None) -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    total = int(round(duration * FPS))
    bounds = boundaries(scenes, transitions, duration)
    video = OUT / f"{name}_1080x1920_{FPS}fps.mp4"

    def gen():
        for i in range(total):
            t = i / FPS
            fr = frame_at(t, i, scenes, transitions, bounds, plates)
            yield B.finish(fr, i, grain=1.0, seed=hash(name) % 97)

    el = encode(gen(), total, video, label=name)

    sha = hashlib.sha256(video.read_bytes()).hexdigest()[:16]
    info = {"name": name, "file": video.name, "duration": duration, "fps": FPS,
            "frames": total, "size_mb": round(video.stat().st_size / 1e6, 2),
            "sha256_16": sha, "encode_s": round(el, 1)}

    if audio:
        import audio as A
        wav = OUT / f"{name}_bed.wav"
        A.write_wav(wav, A.build(duration, audio.get("beats", []), audio.get("whips", []), audio.get("bpm", 120)))
        muxed = OUT / f"{name}_1080x1920_{FPS}fps_audio.mp4"
        subprocess.run([str(ROOT / "bin" / "ffmpeg"), "-y", "-loglevel", "error",
                        "-i", str(video), "-i", str(wav), "-c:v", "copy", "-c:a", "aac",
                        "-b:a", "192k", "-shortest", str(muxed)], check=True)
        video.replace(video.with_suffix(".tmp.mp4"))
        muxed.replace(video)
        video.with_suffix(".tmp.mp4").unlink()
        info["audio"] = wav.name

    # posters + storyboard desde frames re-renderizados (acabado incluido)
    posters = {}
    for tag, pt in POSTERS.get(name, {}).items():
        fi = int(round(pt * FPS))
        fr = B.finish(frame_at(pt, fi, scenes, transitions, bounds, plates), fi, grain=1.0,
                      seed=hash(name) % 97)
        jp = OUT / f"{name}_{tag}.jpg"
        Image.fromarray(fr).save(jp, quality=92)
        posters[tag] = jp.name
    info["posters"] = posters

    # storyboard 3×3
    ts = [duration * k / 9 + 0.12 for k in range(9)]
    tiles = []
    for pt in ts:
        fi = int(round(pt * FPS))
        fr = frame_at(pt, fi, scenes, transitions, bounds, plates)
        tiles.append(Image.fromarray(fr).resize((270, 480)))
    sheet = Image.new("RGB", (270 * 3 + 16, 480 * 3 + 16), (10, 9, 8))
    for k, im in enumerate(tiles):
        sheet.paste(im, (4 + (k % 3) * (270 + 4), 4 + (k // 3) * (480 + 4)))
    sheet.save(OUT / f"{name}_storyboard.jpg", quality=88)
    info["storyboard"] = f"{name}_storyboard.jpg"
    return info


POSTERS = {
    "reel_black_friday_abyss": {"cover_hook": 1.7, "poster_cta": 16.4, "poster_pre": 5.0},
    "story_1_pre_black_friday": {"cover": 1.6, "poster_cta": 4.6},
    "story_2_categorias": {"cover": 0.9, "poster_cta": 5.2},
    "story_3_black_friday_cta": {"cover": 1.4, "poster_cta": 4.4},
}


def scale_piece(scenes, transitions, base_dur: float, new_dur: float):
    """Duración ajustable: re-escala proporcionalmente claves, cortes y whips.

    La escaleta es data-driven (claves en segundos absolutos), así que un factor
    f = nueva/base conserva ritmos, easings y rejilla de cortes. Permite cumplir
    «duración ajustable / podrás variar la cantidad de segundos» sin re-editar.
    """
    f = new_dur / base_dur

    def sk(keys):
        for k in keys or []:
            k["t"] = round(k["t"] * f, 4)

    for sc in scenes:
        sc["t0"] = round(sc["t0"] * f, 4)
        sc["t1"] = round(sc["t1"] * f, 4)
        for ly in sc["layers"]:
            for key in ("in", "out"):
                if key in ly:
                    ly[key] = round(ly[key] * f, 4)
            sk(ly.get("keys"))
            sk(ly.get("cam"))
    for tr in transitions:
        tr["at"] = round(tr["at"] * f, 4)
        if "dur" in tr:
            tr["dur"] = round(tr["dur"] * f, 4)
    return scenes, transitions, new_dur


def main(argv: list[str]) -> None:
    which = argv[0] if argv else "all"
    reel_dur = 18.0
    story_dur = 6.0
    if "--reel-dur" in argv:
        reel_dur = float(argv[argv.index("--reel-dur") + 1])
    if "--story-dur" in argv:
        story_dur = float(argv[argv.index("--story-dur") + 1])
    plates = build_plates()
    results = []
    pieces = []
    if which in ("all", "reel"):
        scenes, tr, dur = T.reel_scenes()
        base = dur
        scenes, tr, dur = scale_piece(scenes, tr, base, reel_dur)
        f = reel_dur / base
        POSTERS["reel_black_friday_abyss"] = {k: round(v * f, 3) for k, v in
                                              POSTERS["reel_black_friday_abyss"].items()}
        name = "reel_black_friday_abyss" if reel_dur == base else f"reel_black_friday_abyss_{reel_dur:g}s"
        if name != "reel_black_friday_abyss":
            POSTERS[name] = POSTERS["reel_black_friday_abyss"]
        pieces.append((name, scenes, tr, dur,
                       {"beats": [3.0 * f, 7.2 * f, 13.2 * f], "whips": [3.0 * f, 13.2 * f], "bpm": 120}))
    if which in ("all", "stories"):
        for nm, fn in (("story_1_pre_black_friday", T.story1),
                       ("story_2_categorias", T.story2),
                       ("story_3_black_friday_cta", T.story3)):
            scenes, tr, dur = fn()
            base = dur
            scenes, tr, dur = scale_piece(scenes, tr, base, story_dur)
            f = story_dur / base
            if f != 1.0:
                nm = f"{nm}_{story_dur:g}s"
            pieces.append((nm, scenes, tr, dur, None))
    for nm, scenes, tr, dur, au in pieces:
        print(f"== {nm} ({dur}s · {int(dur * FPS)} frames)")
        results.append(render_piece(nm, scenes, tr, dur, plates, au))
    write_manifest(results, merge=True)


def write_manifest(results: list[dict], merge: bool = True) -> dict:
    prev = {}
    if merge and (OUT / "manifest.json").exists():
        prev = {pc["name"]: pc for pc in json.loads((OUT / "manifest.json").read_text()).get("pieces", [])}
    for pc in results:
        prev[pc["name"]] = pc
    manifest = {
        "campaign": "BLACK FRIDAY ABYSS TATTOO STUDIO",
        "brand_line": "ABYSS TATTOO Y PIERCING ♦ San Bernardo",
        "format": f"{W}x{H} @ {FPS}fps · H.264 High 4.2 · BT.709",
        "reference": "dropbox/type_01_pindown.io_1795195281.mp4 (gramática replicada)",
        "grade": "hiperrealista + duotono metálico cálido + film grain + viñeta + halación",
        "duration_note": "duración ajustable: src/render.py reel --reel-dur S / stories --story-dur S",
        "cta": {
            "instagram": "https://www.instagram.com/abyss_tattoo_studio",
            "instagram_handle": "@abyss_tattoo_studio",
            "whatsapp": "https://wa.me/56947786839",
        },
        "pieces": list(prev.values()),
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    return manifest


def rebuild_manifest() -> None:
    """Reconstruye el manifest desde out/ (sin re-renderizar)."""
    import hashlib
    results = []
    for mp4 in sorted(OUT.glob("*_1080x1920_30fps.mp4")):
        name = mp4.name.replace("_1080x1920_30fps.mp4", "")
        posters = {}
        for tag in ("cover_hook", "poster_cta", "poster_pre", "cover"):
            jp = OUT / f"{name}_{tag}.jpg"
            if jp.exists():
                posters[tag] = jp.name
        sb = OUT / f"{name}_storyboard.jpg"
        results.append({
            "name": name, "file": mp4.name,
            "duration": round(int(round(_probe_dur(mp4) * FPS)) / FPS, 2),
            "fps": FPS, "frames": int(round(_probe_dur(mp4) * FPS)),
            "size_mb": round(mp4.stat().st_size / 1e6, 2),
            "sha256_16": hashlib.sha256(mp4.read_bytes()).hexdigest()[:16],
            "posters": posters,
            "storyboard": sb.name if sb.exists() else None,
        })
    m = write_manifest(results, merge=False)
    print(json.dumps(m, indent=2, ensure_ascii=False))


def _probe_dur(path: Path) -> float:
    r = subprocess.run([str(ROOT / "bin" / "ffmpeg"), "-hide_banner", "-i", str(path)],
                       capture_output=True, text=True)
    for line in r.stderr.splitlines():
        if line.strip().startswith("Duration"):
            hh, mm, ss = line.split(",")[0].split(":")[1:]
            return int(hh) * 3600 + int(mm) * 60 + float(ss)
    return 0.0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:]]
    if args and args[0] == "manifest":
        rebuild_manifest()
    else:
        main(args)
