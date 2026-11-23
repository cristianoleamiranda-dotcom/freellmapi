"""Baja material binario desde repos públicos vía api.github.com (blobs raw)."""
from __future__ import annotations
import json, sys, urllib.request
from pathlib import Path

API = "https://api.github.com"

def tree(repo: str, ref: str = "main") -> dict:
    req = urllib.request.Request(f"{API}/repos/{repo}/git/trees/{ref}?recursive=1",
                                 headers={"Accept": "application/vnd.github+json", "User-Agent": "abyss-bf"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return {t["path"]: t for t in json.loads(r.read()).get("tree", []) if t["type"] == "blob"}

def blob(repo: str, sha: str, dst: Path) -> int:
    req = urllib.request.Request(f"{API}/repos/{repo}/git/blobs/{sha}",
                                 headers={"Accept": "application/vnd.github.raw", "User-Agent": "abyss-bf"})
    with urllib.request.urlopen(req, timeout=180) as r:
        data = r.read()
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(data)
    return len(data)

JOBS = [
    # (repo, ref, path_en_repo, destino_local)
    ("cristianoleamiranda-dotcom/abysstattoo", "main", "film/hero_film.mp4", "material/film/hero_film.mp4"),
    ("cristianoleamiranda-dotcom/abysstattoo", "main", "film/proceso_filmacion.mp4", "material/film/proceso_filmacion.mp4"),
    ("cristianoleamiranda-dotcom/abysstattoo", "main", "film/proceso_detalle.mp4", "material/film/proceso_detalle.mp4"),
    ("cristianoleamiranda-dotcom/abysstattoo", "main", "film/proceso_pierna.mp4", "material/film/proceso_pierna.mp4"),
    ("cristianoleamiranda-dotcom/abysstattoo", "main", "film/loop_film.mp4", "material/film/loop_film.mp4"),
    ("cristianoleamiranda-dotcom/abysstattoo", "main", "assets/reel_plates/emblema_abyss_alpha.png", "material/brand/emblema_abyss_alpha.png"),
    ("cristianoleamiranda-dotcom/abysstattoo", "main", "assets/skull_mark_crema.png", "material/brand/skull_mark_crema.png"),
    ("cristianoleamiranda-dotcom/abysstattoo", "main", "assets/logo_abyss_256.png", "material/brand/logo_abyss_256.png"),
    ("cristianoleamiranda-dotcom/abysstattoo", "main", "assets/fonts/montserrat-500.ttf", "material/fonts/montserrat-500.ttf"),
    ("cristianoleamiranda-dotcom/abysstattoo", "main", "assets/fonts/montserrat-600.ttf", "material/fonts/montserrat-600.ttf"),
    ("cristianoleamiranda-dotcom/abysstattoo", "main", "assets/fonts/montserrat-700.ttf", "material/fonts/montserrat-700.ttf"),
    ("cristianoleamiranda-dotcom/abysstattoo", "main", "assets/fonts/cinzel-700.ttf", "material/fonts/cinzel-700.ttf"),
    ("google/fonts", "main", "ofl/anton/Anton-Regular.ttf", "material/fonts/Anton-Regular.ttf"),
]

def main() -> int:
    cache: dict[str, dict] = {}
    for repo, ref, path, dst in JOBS:
        key = f"{repo}@{ref}"
        if key not in cache:
            cache[key] = tree(repo, ref)
        node = cache[key].get(path)
        if not node:
            print(f"  FALTA  {repo}:{path}")
            continue
        d = Path(dst)
        if d.exists() and d.stat().st_size == node.get("size"):
            print(f"  ok     {dst} (cache)")
            continue
        n = blob(repo, node["sha"], d)
        print(f"  {n/1e6:6.2f} MB  {dst}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
