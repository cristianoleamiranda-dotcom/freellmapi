# DESCARGA DEL MATERIAL FINAL — BLACK FRIDAY ABYSS TATTOO STUDIO
Actualizado 2026-11-23 · **Veredicto vigente: APROBADO CON OBSERVACIONES**
Informe que rige: `research/AUDITORIA_SENIOR_V2_2026-11-23.md` (correcciones priorizadas P1–P6) ·
Auditoría anterior (superada en los puntos 1 y 4c): `research/AUDITORIA_2026-11-23.md`

## 1) Paquete completo (recomendado)
ZIP de 33 archivos — `videos/` 5 piezas · `posters/` 12 · `storyboards/` 5 · `docs/` 9 + `LEEME.txt` + `SHA256SUMS.txt`

- **Carpeta de la entrega en Dropbox** (todo: videos sueltos, ZIP, posters, storyboards, docs):
  https://www.dropbox.com/scl/fo/0crptvwdfh2nyvga0stzg/ALpOzAsAdB1My1DH7QH0Kjw?rlkey=28bxlxuab57zr8bhx1tphtchy&dl=0
- **ZIP — descarga directa** (cambia `dl=0` por `dl=1` para bajarlo sin abrir Dropbox):
  https://www.dropbox.com/scl/fi/73bf5vdr5hld81uibcjdm/ABYSS_BLACK_FRIDAY_ENTREGA_FINAL_2026-11-23.zip?rlkey=jmseeyqr07rpuq5hwcslqe306&dl=1
- **Informe de auditoría senior v2** (PDF/MD legible en el navegador):
  https://www.dropbox.com/scl/fi/6hr570djrrxclrrqplrvv/AUDITORIA_SENIOR_V2_2026-11-23.md?rlkey=4k7x4fkyih8zfsbgj47w5l137&dl=0
- **Parche P1 (legibilidad, validado y sin aplicar)**:
  https://www.dropbox.com/scl/fi/jsjj7n9xht61xlg8n99ru/P1_legibilidad.patch?rlkey=b5blwmtqa8a3p3i15bizvwznm&dl=0
- Carpeta raíz de activos de la campaña (incluye `/material` original, 18 archivos intactos):
  https://www.dropbox.com/scl/fo/4go1i024c3iekp0mlb8t0/ALHRa8awLgImlMWL94F8zog?rlkey=lsycopu8vqxgclnb8ac1zo6i7&dl=0
- Sala de revisión local (visor con descarga del ZIP): `out/visor.html` — se sirve con
  `PYTHONPATH=src python3 src/serve_preview.py` (soporta Range/206).

## 2) Piezas individuales (descarga directa: cambia `dl=0` por `dl=1`)
| Pieza | Duración | Tamaño | Enlace |
|---|---|---|---|
| Reel principal (audio AAC) | 18.00 s | 31,590,916 B | https://www.dropbox.com/scl/fi/1nv4yle0iyund49j2ilyg/reel_black_friday_abyss_1080x1920_30fps.mp4?rlkey=q1dbo6tf60ef5gnus7h1w9u08&dl=1 |
| Reel variante 15 s (audio AAC) | 15.00 s | 26,416,942 B | https://www.dropbox.com/scl/fi/9zaawq4njtzk299r6wl1d/reel_black_friday_abyss_15s_1080x1920_30fps.mp4?rlkey=vt9dk5adkmjvovs5pv9acmmjb&dl=1 |
| Historia 1 — PRE 26/11 | 6.00 s | 10,441,172 B | https://www.dropbox.com/scl/fi/cwbimce9w75fheorof27c/story_1_pre_black_friday_1080x1920_30fps.mp4?rlkey=6oi0awf2wkk89lxsxisnsrhsc&dl=1 |
| Historia 2 — rubros | 6.00 s | 10,007,543 B | https://www.dropbox.com/scl/fi/owq26uvb08nzo7fb4f0u5/story_2_categorias_1080x1920_30fps.mp4?rlkey=d9o36he5e2rawovfqd2bnyskq&dl=1 |
| Historia 3 — 27/11 + CTAs | 6.00 s | 9,747,782 B | https://www.dropbox.com/scl/fi/mqjwvanh8vbnyrkdzy6iw/story_3_black_friday_cta_1080x1920_30fps.mp4?rlkey=ackyh4jxls6eybw6alnguy6c9&dl=1 |

Duración variable sin re-editar: `PYTHONPATH=src python3 src/render.py reel --reel-dur 15`
(historias: `stories --story-dur 8`). Cortes verificados de 10 a 30 s.

## 3) Verificación de integridad tras descargar
```bash
unzip ABYSS_BLACK_FRIDAY_ENTREGA_FINAL_2026-11-23.zip -d entrega
cd entrega && shasum -a 256 -c SHA256SUMS.txt      # macOS / Linux
             # o: sha256sum -c SHA256SUMS.txt
```
Especificaciones: 1080×1920 (9:16, píxel cuadrado) · 30 fps · H.264 **High@4.2** · yuv420p 8-bit ·
**BT.709** (tv/progressive) · `+faststart` · reels con AAC-LC 48 kHz estéreo 189 kb/s ·
historias sin pista de audio (decisión de diseño, obs. O4).
Zonas seguras Instagram: 0 violaciones (margen 72–1008 × 250–1670).
CTAs literales: `https://www.instagram.com/abyss_tattoo_studio?fqnt=MWZvZHQxdTV2MHVmbA==` ·
`https://wa.me/56947786839`

## 4) Integridad local ↔ Dropbox (content_hash estilo Dropbox, validado contra el servidor)
`sha256(concat(sha256(bloques de 4 MiB)))` — recalcula en cualquier momento:
```bash
python3 scripts/dropbox_content_hash.py out/*.mp4 out/*.zip   # -> out/INTEGRIDAD_hashes.txt
python3 scripts/build_delivery_zip.py --check                 # valida el ZIP sin regenerarlo
```
Los 6 valores de `out/INTEGRIDAD_hashes.txt` coinciden byte a byte con los que reporta Dropbox.
Videos (inmutables): reel18 `59b06a98…` · reel15 `b1b59b19…` · story1 `a6a8aff7…` ·
story2 `9cc3f343…` · story3 `cc0b2627…`.
