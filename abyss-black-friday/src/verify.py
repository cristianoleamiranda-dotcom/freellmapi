"""QC de entregables: ffprobe + integridad + hoja de contactos final."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
FF = str(ROOT / "bin" / "ffmpeg")

EXPECT = {
    "reel_black_friday_abyss_1080x1920_30fps.mp4": (18.0, True),
    "story_1_pre_black_friday_1080x1920_30fps.mp4": (6.0, False),
    "story_2_categorias_1080x1920_30fps.mp4": (6.0, False),
    "story_3_black_friday_cta_1080x1920_30fps.mp4": (6.0, False),
    "reel_black_friday_abyss_15s_1080x1920_30fps.mp4": (15.0, True),
}


def probe(path: Path) -> dict:
    cmd = [FF, "-hide_banner", "-i", str(path)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    info = r.stderr
    out = {"file": path.name, "size_mb": round(path.stat().st_size / 1e6, 2)}
    for line in info.splitlines():
        line = line.strip()
        if line.startswith("Duration"):
            out["duration"] = ":".join(line.split(",")[0].split(":")[1:])
        if "Video:" in line:
            out["video"] = line.split("Video:", 1)[1].strip()
        if "Audio:" in line:
            out["audio"] = line.split("Audio:", 1)[1].strip()
    return out


def main() -> int:
    ok = True
    rows = []
    for name, (dur, wants_audio) in EXPECT.items():
        p = OUT / name
        if not p.exists():
            print(f"FALTA {name}")
            ok = False
            continue
        info = probe(p)
        hh, mm, ss = info["duration"].split(":")
        d = float(hh) * 3600 + float(mm) * 60 + float(ss)
        good = abs(d - dur) < 0.12 and "1080x1920" in info["video"] and "30 fps" in info["video"]
        if wants_audio:
            good = good and "audio" in info
        ok = ok and good
        rows.append({**info, "expect_s": dur, "pass": good})
        print(f"{'OK ' if good else 'BAD'} {name}: {info['duration']} · {info['video']}"
              + (f" · {info.get('audio')}" if info.get("audio") else ""))
    (OUT / "qc.json").write_text(json.dumps(rows, indent=2))
    print("QC:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
