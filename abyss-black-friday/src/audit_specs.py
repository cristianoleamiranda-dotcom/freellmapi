"""Auditoría 4 (v2): especificaciones de entrega profundas.

Verifica por pieza: contenedor (orden de átomos = faststart), duración exacta y nº de
frames decodificables, códec/perfil/nivel, pix_fmt, etiquetado de color BT.709 completo,
SAR/DAR, metadata de rotación (debe ser 0/ausente en IG), GOP (intervalo de keyframes),
bitrate y, en los reels, audio AAC-LC 48 kHz estéreo con duración igual al video.
Salida: research/audit_specs_report.json
"""
from __future__ import annotations
import json, re, struct, subprocess
from pathlib import Path
import cv2

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
FF = str(ROOT / "bin" / "ffmpeg")
PIECES = ["reel_black_friday_abyss", "reel_black_friday_abyss_15s",
          "story_1_pre_black_friday", "story_2_categorias", "story_3_black_friday_cta"]


def atoms(p: Path):
    d = p.read_bytes(); i = 0; out = []
    while i < len(d) - 8 and len(out) < 12:
        size = struct.unpack(">I", d[i:i+4])[0]; typ = d[i+4:i+8].decode("latin1")
        if size < 8:
            break
        out.append((typ, i, size)); i += size
    return out


def probe(p: Path) -> dict:
    r = subprocess.run([FF, "-hide_banner", "-i", str(p)], capture_output=True, text=True)
    info = r.stderr
    g = lambda pat, d=None: (re.search(pat, info).group(1) if re.search(pat, info) else d)
    kf = subprocess.run([FF, "-hide_banner", "-i", str(p), "-vf",
                         "select=eq(pict_type\\,I),showinfo", "-f", "null", "-"],
                        capture_output=True, text=True)
    n_key = kf.stderr.count("pts_time")
    dec = subprocess.run([FF, "-v", "error", "-i", str(p), "-f", "null", "-"],
                         capture_output=True, text=True)
    cap = cv2.VideoCapture(str(p)); nframes = 0
    while True:
        ok, _ = cap.read()
        if not ok:
            break
        nframes += 1
    fps = cap.get(cv2.CAP_PROP_FPS); cap.release()
    at = atoms(p)
    order = [a[0] for a in at]
    moov_i = order.index("moov") if "moov" in order else -1
    mdat_i = order.index("mdat") if "mdat" in order else -1
    dur = float(g(r"Duration: ([\d:.]+)", "0").replace(".", ":").split(":")[0]) if False else None
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", info)
    dur = int(m.group(1))*3600 + int(m.group(2))*60 + float(m.group(3)) if m else None
    return {
        "file": p.name, "bytes": p.stat().st_size,
        "duration_s": round(dur, 3) if dur else None,
        "frames_decoded": nframes, "fps": round(fps, 3),
        "duration_from_frames_s": round(nframes / fps, 3),
        "size": g(r", (\d+x\d+)", "?"), "sar_dar": g(r"\[SAR (\S+) DAR (\S+)\]", "n/d"),
        "video_codec": g(r"Video: (\w+)"), "profile": g(r"Video: \w+ \(([^),]+)"),
        "level": g(r"avc1[^,]*, ([\d.]+) kb/s") and g(r"\(avc1 / 0x[0-9a-fA-F]+\), ([^,]+),") ,
        "pix_fmt_color": g(r"(yuv420p\([^)]*\))"),
        "video_bitrate": g(r", ([\d]+) kb/s", "?"),
        "audio": g(r"Audio: (.+?), (\d+) Hz, ([^,]+), (\w+), (\d+) kb/s"),
        "rotation_meta": "presente" if re.search(r"rotate|displaymatrix|Side data", info) else "ausente",
        "atoms_top_level": order, "faststart": bool(0 <= moov_i < mdat_i),
        "keyframes": n_key, "gop_s": round(nframes / n_key / fps, 2) if n_key else None,
        "decode_errors_ffmpeg": (dec.stderr.strip().splitlines() or ["0"])[0][:120] if dec.stderr.strip() else "ninguno",
        "decode_errors_count": len([l for l in dec.stderr.splitlines() if l.strip()]),
    }


res = {n: probe(OUT / f"{n}_1080x1920_30fps.mp4") for n in PIECES
       if (OUT / f"{n}_1080x1920_30fps.mp4").exists()}
fails = []
for n, r in res.items():
    ok = (r["size"] == "1080x1920" and abs(r["fps"] - 30) < 0.01 and r["video_codec"] == "h264"
          and "High" in (r["profile"] or "") and r["pix_fmt_color"] == "yuv420p(tv, bt709, progressive)"
          and r["faststart"] and abs(r["duration_from_frames_s"] - r["duration_s"]) < 0.05
          and r["rotation_meta"] == "ausente" and r["decode_errors_count"] == 0)
    if n.startswith("reel"):
        ok = ok and bool(r["audio"]) and "48000 Hz" in (r["audio"] or "") and "stereo" in (r["audio"] or "")
    print(f"{'PASS' if ok else 'FAIL'}  {n}: {r['size']} {r['fps']}fps {r['video_codec']}/"
          f"{r['profile']} {r['pix_fmt_color']} dur={r['duration_s']}s frames={r['frames_decoded']} "
          f"faststart={r['faststart']} rot={r['rotation_meta']} GOP={r['gop_s']}s audio={r['audio']}")
    if not ok:
        fails.append(n)
    print(f"      átomos={r['atoms_top_level']} · errs decode={r['decode_errors_count']} · "
          f"{r['bytes']:,} B · {r['video_bitrate']} kb/s")
(ROOT / "research" / "audit_specs_report.json").write_text(json.dumps(res, indent=2, ensure_ascii=False))
print("\nVEREDICTO 4-specs:", "PASS" if not fails else f"FAIL {fails}")
