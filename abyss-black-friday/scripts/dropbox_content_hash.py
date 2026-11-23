#!/usr/bin/env python3
"""Calcula el content_hash estilo Dropbox de archivos locales para verificar integridad
local <-> Dropbox sin descargar. Receta validada contra el servidor (2026-11-23):
  content_hash = sha256( concat( sha256(bloque_i) ) ), bloques de 4 MiB.
Uso: python3 scripts/dropbox_content_hash.py ruta1 ruta2 ...
Compara el resultado con el campo content_hash de list_folder / get_file_metadata."""
import hashlib, pathlib, sys

BLOCK = 4 * 1024 * 1024

def content_hash(path):
    data = pathlib.Path(path).read_bytes()
    return hashlib.sha256(b"".join(
        hashlib.sha256(data[i:i + BLOCK]).digest() for i in range(0, len(data), BLOCK)
    )).hexdigest()

for arg in sys.argv[1:]:
    p = pathlib.Path(arg)
    print(f"{content_hash(p)}  {p.stat().st_size:>12,}  {p}")
