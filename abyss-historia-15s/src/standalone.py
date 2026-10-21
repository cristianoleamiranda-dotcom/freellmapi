#!/usr/bin/env python3
"""Genera un visor autónomo de un solo archivo HTML.

Embebe la previa de 3 MB en base64, así que el archivo se abre con doble clic,
funciona sin servidor y se puede enviar por correo o WhatsApp sin depender de
ningún hosting. Uso:

    python3 src/standalone.py
"""

from __future__ import annotations

import base64
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
VIDEO = OUT / "abyss_historia_15s_720x1280_preview.mp4"
POSTER = OUT / "cover_hook.jpg"
TARGET = OUT / "abyss_historia_15s_visor.html"

TAG = "abyss-historia-15s"
REPO = "cristianoleamiranda-dotcom/freellmapi"
RELEASE = f"https://github.com/{REPO}/releases/tag/{TAG}"

SCENES = [
    ("0.0", "1.8", "Hook · macro de aguja", "ESTO NO ES / UN TATUAJE"),
    ("1.8", "3.6", "La firma · lobo", "ES UNA FIRMA"),
    ("3.6", "5.4", "Pieza única · manga", "PIEZA ÚNICA"),
    ("5.4", "7.2", "Cabina · proceso real", "TRAZO A TRAZO"),
    ("7.2", "8.4", "Piercing · titanio", "TITANIO"),
    ("8.4", "9.6", "El lugar · fachada 528", "SAN BERNARDO"),
    ("9.6", "11.4", "Mosaico rítmico", "BLACK & GREY · ORIENTAL · FULL COLOR"),
    ("11.4", "15.0", "Cierre · emblema y CTA", "AGENDA TU HORA"),
]

TEMPLATE = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Abyss Tattoo Studio · historia 15 s</title>
<meta name="description" content="Historia vertical de 15 segundos para Abyss Tattoo Studio. Archivo autónomo: el video viaja dentro del HTML.">
<style>
  :root { --obsidian:#14100d; --line:#2c2521; --hueso:#b5a295; --cream:#eae3dd; --sage:#556c65; --teal:#9ec4ba; }
  * { box-sizing: border-box; }
  body {
    margin: 0; background: radial-gradient(1100px 700px at 80% -10%, #241d18 0%, transparent 60%), var(--obsidian);
    color: var(--cream); font-family: "Montserrat", system-ui, -apple-system, sans-serif; font-weight: 500;
  }
  .wrap { width: min(1240px, calc(100% - 44px)); margin-inline: auto; }
  header { border-bottom: 1px solid var(--line); padding: 16px 0; }
  .top { display: flex; justify-content: space-between; align-items: center; gap: 20px; flex-wrap: wrap; }
  .kicker { font-size: 11px; letter-spacing: .16em; text-transform: uppercase; color: var(--hueso); margin: 0 0 6px; }
  h1 { font-family: "Cinzel", Georgia, serif; font-weight: 800; font-size: clamp(26px, 3.6vw, 42px); margin: 0; letter-spacing: .02em; }
  h1 em { font-style: normal; color: var(--teal); }
  h2 { font-family: "Cinzel", Georgia, serif; font-size: clamp(19px, 2.2vw, 26px); margin: 0 0 8px; }
  .chips { display: flex; gap: 8px; flex-wrap: wrap; }
  .chip { border: 1px solid var(--line); border-radius: 999px; padding: 7px 13px; font-size: 11px; letter-spacing: .08em; text-transform: uppercase; color: var(--hueso); }
  .layout { display: grid; grid-template-columns: minmax(0, 440px) minmax(0, 1fr); gap: 52px; padding: 40px 0 8px; align-items: start; }
  .phone { background: linear-gradient(180deg, #1d1714, #120f0c); border: 1px solid var(--line); border-radius: 26px; padding: 13px; box-shadow: 0 40px 80px -40px #000; }
  video { width: 100%; aspect-ratio: 9/16; max-height: 70vh; border-radius: 16px; background: #000; display: block; }
  .bar { display: flex; justify-content: space-between; align-items: center; padding: 9px 3px 1px; font-size: 12px; color: var(--teal); font-variant-numeric: tabular-nums; }
  button { font: inherit; cursor: pointer; }
  .ghost { background: none; border: 1px solid var(--line); color: var(--hueso); border-radius: 999px; padding: 6px 12px; font-size: 11px; letter-spacing: .08em; text-transform: uppercase; }
  .controls { display: flex; gap: 12px; align-items: center; margin-top: 16px; flex-wrap: wrap; }
  .primary { background: var(--cream); color: #17120f; border: 0; border-radius: 999px; padding: 13px 20px; font-weight: 700; font-size: 14px; }
  .primary.is-playing { background: var(--teal); }
  .lede { color: var(--hueso); font-size: 14px; line-height: 1.65; margin: 0 0 16px; }
  .scenes { list-style: none; margin: 0; padding: 0; border-top: 1px solid var(--line); }
  .scenes li { border-bottom: 1px solid var(--line); }
  .scenes button { display: grid; grid-template-columns: 92px 1fr; grid-template-areas: "t n" "t x"; gap: 2px 16px; width: 100%; text-align: left; background: none; border: 0; border-left: 2px solid transparent; color: var(--cream); padding: 13px 12px 13px 14px; }
  .scenes button:hover { background: rgba(158,196,186,.05); }
  .scenes .t { grid-area: t; color: var(--teal); font-size: 12px; align-self: center; font-variant-numeric: tabular-nums; }
  .scenes .n { grid-area: n; font-weight: 600; font-size: 15px; }
  .scenes .x { grid-area: x; color: var(--hueso); font-size: 11px; letter-spacing: .1em; text-transform: uppercase; }
  .scenes li.is-active button { background: rgba(158,196,186,.08); border-left-color: var(--teal); }
  .section { padding: 44px 0 6px; }
  .files { list-style: none; padding: 0; margin: 16px 0 0; display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 12px; }
  .files a { display: block; border: 1px solid var(--line); border-radius: 14px; padding: 15px 17px; text-decoration: none; color: var(--cream); background: linear-gradient(180deg, rgba(26,21,18,.95), rgba(20,16,13,.95)); }
  .files a:hover { border-color: var(--sage); }
  .files strong { display: block; font-size: 14px; margin-bottom: 3px; }
  .files span { color: var(--hueso); font-size: 12px; }
  .board img { width: 100%; border: 1px solid var(--line); border-radius: 16px; display: block; }
  footer { border-top: 1px solid var(--line); margin-top: 46px; padding: 22px 0 42px; color: var(--hueso); font-size: 12px; line-height: 1.8; }
  footer strong { color: var(--cream); }
  code { color: var(--teal); }
  .note { border: 1px solid var(--sage); border-radius: 12px; padding: 12px 14px; color: var(--hueso); font-size: 12px; line-height: 1.6; margin-top: 14px; }
  @media (max-width: 900px) { .layout { grid-template-columns: 1fr; gap: 32px; } .phone { max-width: 400px; margin-inline: auto; } }
</style>
</head>
<body>
<header>
  <div class="wrap top">
    <div>
      <p class="kicker">Abyss Tattoo Studio · José Joaquín Pérez 528, San Bernardo</p>
      <h1>Historia de <em>15 segundos</em></h1>
    </div>
    <div class="chips">
      <span class="chip">1080 × 1920</span>
      <span class="chip">60 fps</span>
      <span class="chip">15.00 s</span>
      <span class="chip">100 BPM</span>
    </div>
  </div>
</header>

<main class="wrap layout">
  <section>
    <div class="phone">
      <video id="player" poster="__POSTER__" controls playsinline preload="auto" loop src="__VIDEO__"></video>
      <div class="bar"><span id="tc">00:00.00</span><button id="fs" class="ghost" type="button">Pantalla completa</button></div>
    </div>
    <div class="controls">
      <button id="play" class="primary" type="button">▶ Reproducir con sonido</button>
    </div>
    <div class="note">Este archivo es autónomo: el video (720×1280, 3 MB) viaja dentro del HTML.
      Ábrelo con doble clic, súbelo a Drive o mándalo por correo. No necesita internet.</div>
  </section>

  <section>
    <h2>Escaleta</h2>
    <p class="lede">Ocho bloques sobre rejilla de 0.6 s. Toca uno para saltar a ese punto.</p>
    <ol class="scenes" id="scenes">__SCENES__</ol>
  </section>
</main>

<section class="wrap section">
  <h2>Máster y piezas</h2>
  <p class="lede">Los archivos de máxima calidad están en el release del repositorio.</p>
  <ul class="files">
    <li><a href="https://github.com/__REPO__"><strong>Repositorio</strong><span>Los mp4 de máxima calidad, portadas y manifest están en <code>abyss-historia-15s/out/</code></span></a></li>
    <li><a href="https://github.com/__REPO__"><strong>Visor con servidor</strong><span>Versión completa: seek, calidad 30/60 fps y storyboard</span></a></li>
  </ul>
</section>

<footer class="wrap">
  <p>Dirección <strong>José Joaquín Pérez 528, San Bernardo</strong> · WhatsApp <strong>+56 9 4778 6839</strong> · <strong>@abyss_tattoo_studio</strong></p>
  <p>Material original del repositorio <code>abysstattoo</code>. Montaje, audio y tipografía generados para esta pieza.</p>
</footer>

<script>
  const player = document.getElementById('player');
  const tc = document.getElementById('tc');
  const playBtn = document.getElementById('play');
  const fsBtn = document.getElementById('fs');
  const scenes = [...document.querySelectorAll('#scenes button')];

  const fmt = (s) => {
    const m = Math.floor(s / 60).toString().padStart(2, '0');
    return m + ':' + (s % 60).toFixed(2).padStart(5, '0');
  };

  player.addEventListener('timeupdate', () => {
    tc.textContent = fmt(player.currentTime);
    let active = 0;
    scenes.forEach((btn, i) => { if (player.currentTime >= Number(btn.dataset.t)) active = i; });
    scenes.forEach((btn, i) => btn.parentElement.classList.toggle('is-active', i === active));
  });

  scenes.forEach((btn) => btn.addEventListener('click', () => {
    player.currentTime = Number(btn.dataset.t) + 0.01;
    player.play();
  }));

  const sync = () => {
    playBtn.textContent = player.paused ? '▶ Reproducir con sonido' : '❚❚ Pausa';
    playBtn.classList.toggle('is-playing', !player.paused);
  };
  playBtn.addEventListener('click', async () => {
    if (player.paused) { player.muted = false; try { await player.play(); } catch (e) { player.muted = true; await player.play(); } }
    else player.pause();
    sync();
  });
  player.addEventListener('play', sync);
  player.addEventListener('pause', sync);
  fsBtn.addEventListener('click', () => {
    if (player.requestFullscreen) player.requestFullscreen();
    else if (player.webkitEnterFullscreen) player.webkitEnterFullscreen();
  });
</script>
</body>
</html>
"""


def main() -> int:
    if not VIDEO.exists():
        raise SystemExit(f"Falta {VIDEO}. Renderiza primero con src/render.py")
    video_b64 = base64.b64encode(VIDEO.read_bytes()).decode("ascii")
    poster_b64 = base64.b64encode(POSTER.read_bytes()).decode("ascii") if POSTER.exists() else ""

    scenes_html = "\n".join(
        f'      <li><button data-t="{start}" type="button">'
        f'<span class="t">{start} – {end}</span><span class="n">{name}</span><span class="x">{copy}</span></button></li>'
        for start, end, name, copy in SCENES
    )

    html = (
        TEMPLATE.replace("__SCENES__", scenes_html)
        .replace("__REPO__", REPO)
        .replace("__RELEASE__", RELEASE)
        .replace("__POSTER__", f"data:image/jpeg;base64,{poster_b64}")
        .replace("__VIDEO__", f"data:video/mp4;base64,{video_b64}")
    )
    TARGET.write_text(html, encoding="utf-8")
    size_mb = TARGET.stat().st_size / (1024 * 1024)
    print(f"✓ {TARGET.name} · {size_mb:.2f} MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
