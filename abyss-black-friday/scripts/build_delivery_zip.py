#!/usr/bin/env python3
"""Construye el paquete ZIP de entrega final de la campana Black Friday ABYSS.

Reune en un unico archivo descargable (sin compresion, ``ZIP_STORED``, para que el
tamano publicado coincida byte a byte con el ``content_hash`` de Dropbox) todo lo
que el estudio necesita para publicar: los 5 videos finales, los 12 posters, los 5
storyboards y la documentacion (informes de auditoria, manifest, QC, visor, hashes
y enlaces de descarga).

El paquete es reproducible: ejecutar dos veces este script sobre el mismo ``out/``
genera el mismo arbol interno y los mismos ``LEEME.txt`` / ``SHA256SUMS.txt``.

Uso
---
    python3 scripts/build_delivery_zip.py            # out/ABYSS_..._<fecha>.zip
    python3 scripts/build_delivery_zip.py --check     # solo valida el ZIP existente

Tras generarlo, recalcula y publica los hashes:
    python3 scripts/dropbox_content_hash.py out/*.mp4 out/*.zip > out/INTEGRIDAD_hashes.txt
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import zipfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
RESEARCH = ROOT / "research"

# Nombre del paquete: la fecha es la de la entrega, no la de ejecucion, para que
# el archivo publicado y el que ya circula en Dropbox sigan siendo el mismo.
DELIVERY_DATE = "2026-11-23"
ZIP_NAME = f"ABYSS_BLACK_FRIDAY_ENTREGA_FINAL_{DELIVERY_DATE}.zip"

VIDEOS = [
    "reel_black_friday_abyss_1080x1920_30fps.mp4",
    "reel_black_friday_abyss_15s_1080x1920_30fps.mp4",
    "story_1_pre_black_friday_1080x1920_30fps.mp4",
    "story_2_categorias_1080x1920_30fps.mp4",
    "story_3_black_friday_cta_1080x1920_30fps.mp4",
]

# (archivo de origen, ruta dentro del ZIP)
DOCS = [
    (ROOT / "README.md", "docs/README.md"),
    (RESEARCH / "MOTION-TRANSFER.md", "docs/MOTION-TRANSFER.md"),
    (RESEARCH / "AUDITORIA_2026-11-23.md", "docs/AUDITORIA_2026-11-23.md"),
    (RESEARCH / "AUDITORIA_SENIOR_V2_2026-11-23.md", "docs/AUDITORIA_SENIOR_V2_2026-11-23.md"),
    (RESEARCH / "P1_legibilidad.patch", "docs/P1_legibilidad.patch"),
    (OUT / "manifest.json", "docs/manifest.json"),
    (OUT / "qc.json", "docs/qc.json"),
    (OUT / "visor.html", "docs/visor.html"),
    (OUT / "ENLACES_DESCARGA.md", "docs/ENLACES_DESCARGA.md"),
]

LEEME = """\
BLACK FRIDAY ABYSS TATTOO Y PIERCING - San Bernardo
Paquete de entrega final generado el {fecha}

CONTENIDO
  videos/       5 piezas finales 1080x1920 (9:16), 30 fps, H.264 High@4.2,
                yuv420p, BT.709, +faststart. Reels con audio AAC-LC 48 kHz stereo;
                historias sin pista de audio (decision de diseno).
                  reel_black_friday_abyss_1080x1920_30fps.mp4        18.00 s
                  reel_black_friday_abyss_15s_1080x1920_30fps.mp4    15.00 s (variante)
                  story_1_pre_black_friday_1080x1920_30fps.mp4        6.00 s
                  story_2_categorias_1080x1920_30fps.mp4              6.00 s
                  story_3_black_friday_cta_1080x1920_30fps.mp4        6.00 s
  posters/      12 imagenes: portada (cover_hook), poster PRE 26/11 y poster CTA.
  storyboards/  5 laminas de escaleta (secuencia de beats por pieza).
  docs/         Informes de auditoria (v1 y v2 senior), parche P1 de legibilidad,
                MOTION-TRANSFER.md (transferencia de movimiento desde la referencia),
                manifest.json (metadatos + CTAs), qc.json (control de calidad),
                visor.html (sala de revision offline) y ENLACES_DESCARGA.md.
  SHA256SUMS.txt  Hashes SHA-256 de todo el contenido del paquete.
  LEEME.txt       Este archivo.

VERIFICAR INTEGRIDAD
  shasum -a 256 -c SHA256SUMS.txt      # macOS / Linux
  sha256sum -c SHA256SUMS.txt          # Linux

PUBLICAR
  Reel: subir reel_black_friday_abyss_1080x1920_30fps.mp4 (o la variante de 15 s).
  Historias: story_1 -> story_2 -> story_3, en ese orden.
  CTAs literales: https://www.instagram.com/abyss_tattoo_studio?fqnt=MWZvZHQxdTV2MHVmbA==
                  https://wa.me/56947786839

AUDITORIA
  Veredicto vigente: APROBADO CON OBSERVACIONES
  Informe: docs/AUDITORIA_SENIOR_V2_2026-11-23.md (correcciones priorizadas P1-P6)
"""


def sha256_file(path: Path) -> str:
    """Devuelve el SHA-256 hexadecimal de un archivo, leyendolo por bloques."""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def collect() -> list[tuple[Path, str]]:
    """Lista (archivo_en_disco, ruta_en_zip) de todo el contenido del paquete."""
    entries: list[tuple[Path, str]] = []
    for name in VIDEOS:
        entries.append((OUT / name, f"videos/{name}"))
    for jpg in sorted(OUT.glob("*_storyboard.jpg")):
        entries.append((jpg, f"storyboards/{jpg.name}"))
    for jpg in sorted(OUT.glob("*.jpg")):
        if not jpg.name.endswith("_storyboard.jpg"):
            entries.append((jpg, f"posters/{jpg.name}"))
    entries.extend(DOCS)

    missing = [str(src) for src, _ in entries if not src.is_file()]
    if missing:
        raise SystemExit("Faltan archivos de la entrega:\n  " + "\n  ".join(missing))
    return entries


def build(zip_path: Path) -> None:
    """Genera el paquete ZIP (STORED) con LEEME.txt y SHA256SUMS.txt incluidos."""
    entries = collect()
    sums = [
        f"{sha256_file(src)}  {arc}"
        for src, arc in sorted(entries, key=lambda item: item[1])
    ]
    payload = "\n".join(sums) + "\n"
    leeme = LEEME.format(fecha=DELIVERY_DATE)

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_STORED, allowZip64=True) as zf:
        for src, arc in entries:
            zf.write(src, arc)
        zf.writestr("LEEME.txt", leeme)
        zf.writestr("SHA256SUMS.txt", payload)

    size = zip_path.stat().st_size
    with zipfile.ZipFile(zip_path) as zf:
        count = len(zf.namelist())
    print(f"OK  {zip_path}  {size:,} B  {count} archivos")
    print(f"    sha256(zip) = {sha256_file(zip_path)}")


def check(zip_path: Path) -> int:
    """Valida un paquete existente: integridad CRC y hashes internos."""
    if not zip_path.is_file():
        print(f"FAIL  no existe {zip_path}")
        return 1
    errors = 0
    with zipfile.ZipFile(zip_path) as zf:
        bad = zf.testzip()
        if bad is not None:
            print(f"FAIL  CRC corrupto en {bad}")
            return 1
        names = zf.namelist()
        sums = zf.read("SHA256SUMS.txt").decode("utf-8").splitlines()
        for line in sums:
            digest, _, arc = line.partition("  ")
            try:
                data = zf.read(arc)
            except KeyError:
                print(f"FAIL  falta en el ZIP: {arc}")
                errors += 1
                continue
            if hashlib.sha256(data).hexdigest() != digest:
                print(f"FAIL  {arc}")
                errors += 1
    listed = {line.partition("  ")[2] for line in sums}
    extra = [n for n in names if n not in listed and n not in {"LEEME.txt", "SHA256SUMS.txt"}]
    if extra:
        print(f"FAIL  archivos sin hash: {', '.join(extra)}")
        errors += len(extra)
    print(f"{'OK ' if not errors else 'FAIL'}  {zip_path.name}: {len(names)} archivos, "
          f"{len(sums)} hashes verificados, {errors} errores")
    return 1 if errors else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true",
                        help="valida el paquete existente en vez de regenerarlo")
    parser.add_argument("--out", type=Path, default=OUT / ZIP_NAME,
                        help=f"ruta del ZIP (default: out/{ZIP_NAME})")
    args = parser.parse_args(argv)

    if args.check:
        return check(args.out)
    build(args.out)
    return check(args.out)


if __name__ == "__main__":
    sys.exit(main())
