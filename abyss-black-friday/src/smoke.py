"""Render de prueba: fotogramas sueltos a JPG para revisión visual rápida."""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
import brand as B
import timeline as T
from render import build_plates, frame_at, boundaries, POSTERS

def sheet(name, scenes, tr, dur, plates, times, out):
    bounds = boundaries(scenes, tr, dur)
    tiles = []
    for t in times:
        fi = int(round(t * B.FPS))
        fr = B.finish(frame_at(t, fi, scenes, tr, bounds, plates), fi, grain=1.0, seed=7)
        tiles.append(Image.fromarray(fr).resize((360, 640)))
    cols = len(tiles)
    sh = Image.new("RGB", (cols * 360 + 8, 640 + 24), (10, 9, 8))
    from PIL import ImageDraw
    d = ImageDraw.Draw(sh)
    for k, im in enumerate(tiles):
        sh.paste(im, (4 + k * 360, 4))
        d.text((8 + k * 360, 646), f"{times[k]:.2f}s", fill=(235, 230, 225))
    sh.save(out, quality=90)
    print("saved", out)

if __name__ == "__main__":
    plates = build_plates()
    which = sys.argv[1] if len(sys.argv) > 1 else "reel"
    if which == "reel":
        sc, tr, dur = T.reel_scenes()
        sheet("reel", sc, tr, dur, plates, [0.8, 1.7, 2.9, 3.1, 4.6, 6.1, 7.8, 9.3, 10.9, 12.4, 13.1, 14.6, 16.4, 17.6], "research/smoke_reel.jpg")
    else:
        for nm, fn, ts in (("s1", T.story1, [0.8, 1.8, 3.6, 5.0]),
                           ("s2", T.story2, [0.6, 2.0, 3.5, 5.2]),
                           ("s3", T.story3, [0.8, 1.8, 3.4, 5.0])):
            sc, tr, dur = fn()
            sheet(nm, sc, tr, dur, plates, ts, f"research/smoke_{nm}.jpg")
