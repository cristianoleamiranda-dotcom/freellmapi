#!/usr/bin/env bash
# Despliega el visor de la historia de 15 s en Vercel como sitio estático.
#
# Requisitos:
#   - Vercel CLI (`npm install -g vercel@latest`)
#   - Un token con permiso sobre el equipo: https://vercel.com/account/tokens
#   - Salida de red a api.vercel.com (en el sandbox de Arena está bloqueada)
#
# Uso:
#   export VERCEL_TOKEN=...            # nunca lo escribas en el repo
#   scripts/deploy-vercel.sh
#
# Variables opcionales:
#   VERCEL_SCOPE   equipo por defecto (team_ddoZ4KbyQ3Q2C5HHqp0z6YaK)
#   PROD=0         despliegue de preview en lugar de producción

set -euo pipefail

cd "$(dirname "$0")/.."

SCOPE="${VERCEL_SCOPE:-team_ddoZ4KbyQ3Q2C5HHqp0z6YaK}"
PROD="${PROD:-1}"

if ! command -v vercel >/dev/null 2>&1; then
  echo "✗ falta el CLI. Instálalo con: npm install --global vercel@latest" >&2
  exit 1
fi

if [ -z "${VERCEL_TOKEN:-}" ]; then
  echo "✗ falta VERCEL_TOKEN. Créalo en https://vercel.com/account/tokens" >&2
  echo "  export VERCEL_TOKEN=...   # no lo guardes en el repositorio" >&2
  exit 1
fi

echo "· comprobando salida a api.vercel.com"
if ! curl -sS -o /dev/null -m 10 https://api.vercel.com; then
  echo "✗ api.vercel.com no responde desde este entorno." >&2
  echo "  El deploy se hace desde una máquina con salida a internet normal:" >&2
  echo "  git clone https://github.com/cristianoleamiranda-dotcom/freellmapi.git" >&2
  echo "  cd freellmapi && git checkout arena/a95742be-freellmapi" >&2
  echo "  VERCEL_TOKEN=... abyss-historia-15s/scripts/deploy-vercel.sh" >&2
  exit 2
fi

echo "· verificando token y equipo"
vercel whoami --token "$VERCEL_TOKEN" --scope "$SCOPE" >/dev/null

ARGS=(deploy --yes --token "$VERCEL_TOKEN" --scope "$SCOPE")
if [ "$PROD" = "1" ]; then
  ARGS+=(--prod)
fi

echo "· desplegando $PWD"
URL="$(vercel "${ARGS[@]}" 2>&1 | tee /dev/stderr | grep -oE 'https://[a-z0-9.-]+\.vercel\.app' | tail -1)"

echo
if [ -n "${URL:-}" ]; then
  echo "✓ listo: $URL"
  echo "  visor:  $URL/preview/"
  echo "  pieza:  $URL/out/abyss_historia_15s_720x1280_preview.mp4"
else
  echo "▲ el deploy terminó pero no se pudo leer la URL; revisa la salida de arriba."
fi
