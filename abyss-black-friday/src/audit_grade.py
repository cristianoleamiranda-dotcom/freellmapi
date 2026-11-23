"""Auditoría 2: edición NO TRANSABLE — etalonaje, teoría del color y grano."""
from __future__ import annotations
import sys
from pathlib import Path
import cv2, numpy as np
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import brand as B

FF = str(ROOT / "bin" / "ffmpeg")
OUT = ROOT / "out"

def frame(video, t):
    import subprocess
    p = ROOT / "research" / f"audit_grade_{Path(video).stem}_{t}.png"
    subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y", "-ss", str(t),
                    "-i", str(video), "-frames:v", "1", str(p)], check=True)
    return cv2.imread(str(p))

def stats(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    y = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
    hp = y - cv2.GaussianBlur(y, (0, 0), 2.0)
    dark = y < 40
    grain = float(hp[dark].std()) if dark.mean() > 0.05 else float(hp.std())
    return {"sat_mean": round(float(hsv[..., 1].mean()), 2),
            "lum_std": round(float(y.std()), 2),
            "lum_p99": round(float(np.percentile(y, 99)), 1),
            "grain_sigma_sombras": round(grain, 2)}

def clusters(img, k=6):
    z = img.reshape(-1, 3).astype(np.float32)
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 5)
    _, lab, cen = cv2.kmeans(z, k, None, crit, 3, cv2.KMEANS_PP_CENTERS)
    cnt = np.bincount(lab.ravel(), minlength=k)
    order = np.argsort(-cnt)
    return [(tuple(int(v) for v in cen[i][::-1]), round(float(cnt[i] / len(z)), 3)) for i in order]

TOKENS = {"obsidian": (20, 16, 13), "black": (8, 8, 8), "bone": (181, 162, 149),
          "cream": (234, 227, 221), "copper": (201, 138, 94), "champagne": (231, 201, 164),
          "chrome": (207, 214, 216)}

def nearest(rgb):
    best, bd = None, 1e9
    for name, tok in TOKENS.items():
        d = sum((a - b) ** 2 for a, b in zip(rgb, tok)) ** 0.5
        if d < bd:
            best, bd = name, d
    return best, round(bd, 1)

if __name__ == "__main__":
    src = cv2.imread(str(ROOT.parent / "dropbox" / "18.jpg"))
    ren = frame(OUT / "reel_black_friday_abyss_1080x1920_30fps.mp4", 5.0)
    s_src, s_ren = stats(src), stats(ren)
    print("FUENTE 18.jpg      :", s_src)
    print("RENDER reel t=5.0s :", s_ren)
    print(f"  → edición presente: sat {s_src['sat_mean']}→{s_ren['sat_mean']} · "
          f"grano σ={s_ren['grain_sigma_sombras']} (fuente sin grano: {s_src['grain_sigma_sombras']})")
    ok_grain = s_ren["grain_sigma_sombras"] >= 2.0
    ok_edit = abs(s_ren["sat_mean"] - s_src["sat_mean"]) > 5 or s_ren["lum_std"] != s_src["lum_std"]
    # paleta: clusters del cierre (debe dominar obsidiana + cream + bone + copper)
    cl = clusters(frame(OUT / "reel_black_friday_abyss_1080x1920_30fps.mp4", 16.6))
    print("CLUSTERS cierre 16.6s (RGB, peso):")
    matched = set()
    for rgb, w in cl:
        name, d = nearest(rgb)
        flag = "OK" if d <= 45 else "--"
        if d <= 45:
            matched.add(name)
        print(f"  {flag} {rgb} w={w:.3f} → {name} (Δ{d})")
    need = {"obsidian", "cream", "copper"} | {"bone", "black"}
    ok_palette = len(matched & {"obsidian", "black", "cream", "bone", "copper", "champagne"}) >= 4
    # grano en historias también
    for nm, t in (("story_1", 3.6), ("story_2", 2.1), ("story_3", 4.4)):
        base = {"story_1": "story_1_pre_black_friday", "story_2": "story_2_categorias",
                "story_3": "story_3_black_friday_cta"}[nm]
        st = stats(frame(OUT / f"{base}_1080x1920_30fps.mp4", t))
        print(f"grano {nm} t={t}s: σ={st['grain_sigma_sombras']} sat={st['sat_mean']}")
        ok_grain = ok_grain and st["grain_sigma_sombras"] >= 2.0
    print("VEREDICTO 2:", "PASS" if (ok_grain and ok_edit and ok_palette) else "REVISAR",
          f"(grano={ok_grain} edición={ok_edit} paleta={ok_palette} clusters_ok={sorted(matched)})")
