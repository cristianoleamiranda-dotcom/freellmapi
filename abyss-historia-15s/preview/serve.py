#!/usr/bin/env python3
"""Servidor mínimo para revisar la historia en el navegador.

Añade lo que `python3 -m http.server` no trae y el video necesita:
peticiones Range (para poder mover la barra de progreso), MIME correcto y
redirección de la raíz al visor.

Uso:
    python3 preview/serve.py --port 8000
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import socket
import sys
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent

MIME = {
    ".mp4": "video/mp4",
    ".webm": "video/webm",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".html": "text/html; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".ttf": "font/ttf",
    ".woff2": "font/woff2",
    ".md": "text/markdown; charset=utf-8",
}

RANGE_RE = re.compile(r"bytes=(\d*)-(\d*)")


class Handler(SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def __init__(self, *args, directory: str | None = None, **kwargs):
        super().__init__(*args, directory=directory or str(PROJECT), **kwargs)

    # -- rutas ---------------------------------------------------------------
    def do_GET(self):  # noqa: N802
        if self.path == "/health":
            body = b'{"ok":true}'
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path in ("/", "/index.html"):
            self.send_response(HTTPStatus.FOUND)
            self.send_header("Location", "/preview/")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        if self.path.startswith("/preview") and not self.path.startswith("/preview/"):
            self.send_response(HTTPStatus.FOUND)
            self.send_header("Location", "/preview/")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        super().do_GET()

    def do_HEAD(self):  # noqa: N802
        super().do_HEAD()

    # -- tipos y cabeceras ---------------------------------------------------
    def guess_type(self, path):
        suffix = Path(path).suffix.lower()
        return MIME.get(suffix) or super().guess_type(path)

    def end_headers(self):
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    # -- transferencia robusta ------------------------------------------------
    def copyfile(self, source, outputfile):
        """Copia con bloques pequeños y tolera que el cliente corte la conexión.

        El proxy de preview corta la conexión a mitad de un mp4 grande; sin este
        manejo, el servidor imprime un traceback por cada corte.
        """
        try:
            shutil.copyfileobj(source, outputfile, length=64 * 1024)
        except (BrokenPipeError, ConnectionResetError, socket.timeout):
            self.close_connection = True

    def handle_one_request(self):
        try:
            super().handle_one_request()
        except (BrokenPipeError, ConnectionResetError, socket.timeout):
            self.close_connection = True

    # -- Range ---------------------------------------------------------------
    def send_head(self):
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            return super().send_head()
        if not os.path.exists(path):
            return super().send_head()

        header = self.headers.get("Range")
        if not header:
            return super().send_head()

        match = RANGE_RE.fullmatch(header.strip())
        if not match:
            return super().send_head()

        size = os.path.getsize(path)
        start_raw, end_raw = match.groups()
        if start_raw == "" and end_raw == "":
            return super().send_head()

        if start_raw == "":
            # Sufijo: bytes=-N
            length = min(int(end_raw), size)
            start = size - length
            end = size - 1
        else:
            start = int(start_raw)
            end = int(end_raw) if end_raw else size - 1
            end = min(end, size - 1)

        if start >= size or end < start:
            self.send_response(HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE)
            self.send_header("Content-Range", f"bytes */{size}")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return None

        length = end - start + 1
        fh = open(path, "rb")
        fh.seek(start)
        self.send_response(HTTPStatus.PARTIAL_CONTENT)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(length))
        self.send_header("Last-Modified", self.date_time_string(os.path.getmtime(path)))
        self.end_headers()
        return _LimitedReader(fh, length)

    def log_message(self, fmt, *args):  # silencio salvo errores
        if args and str(args[1]).startswith(("4", "5")):
            sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


class _LimitedReader:
    """Envuelve el archivo para que copyfile no se pase del tramo pedido."""

    def __init__(self, fh, remaining: int):
        self.fh = fh
        self.remaining = remaining

    def read(self, amount: int = 64 * 1024) -> bytes:
        if self.remaining <= 0:
            return b""
        chunk = self.fh.read(min(amount, self.remaining))
        self.remaining -= len(chunk)
        return chunk

    def close(self) -> None:
        self.fh.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Visor local de la historia de 15 s")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 8000)))
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--root", default=str(PROJECT))
    args = parser.parse_args()

    handler = lambda *a, **kw: Handler(*a, directory=args.root, **kw)  # noqa: E731
    server = ThreadingHTTPServer((args.host, args.port), handler)
    print(f"Visor en http://{args.host}:{args.port}/preview/  (raíz: {args.root})", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
