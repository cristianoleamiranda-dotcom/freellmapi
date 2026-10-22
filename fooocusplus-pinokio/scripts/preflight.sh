#!/usr/bin/env bash
# Preflight para instalar FooocusPlus con Pinokio (Linux / macOS).
# Uso: bash scripts/preflight.sh [--min-disk 50]
# Salida: informe legible + código 0 (listo o listo con avisos), 1 (bloqueante).

set -u

MIN_DISK_GB=50
while [ $# -gt 0 ]; do
  case "$1" in
    --min-disk) MIN_DISK_GB="${2:-50}"; shift 2 ;;
    -h|--help) sed -n '2,4p' "$0"; exit 0 ;;
    *) echo "Argumento no reconocido: $1"; exit 2 ;;
  esac
done

BLOCKERS=0
WARNINGS=0

c_red=$'\033[31m'; c_ylw=$'\033[33m'; c_grn=$'\033[32m'; c_dim=$'\033[2m'; c_off=$'\033[0m'
if [ ! -t 1 ]; then c_red=; c_ylw=; c_grn=; c_dim=; c_off=; fi

ok()   { printf "  %sOK%s    %s\n" "$c_grn" "$c_off" "$1"; }
warn() { printf "  %sWARN%s  %s\n" "$c_ylw" "$c_off" "$1"; WARNINGS=$((WARNINGS+1)); }
bad()  { printf "  %sFAIL%s  %s\n" "$c_red" "$c_off" "$1"; BLOCKERS=$((BLOCKERS+1)); }
info() { printf "  %s·%s     %s\n" "$c_dim" "$c_off" "$1"; }
head_() { printf "\n%s\n" "$1"; }

have() { command -v "$1" >/dev/null 2>&1; }

OS="$(uname -s)"; ARCH="$(uname -m)"
echo "FooocusPlus · preflight"
info "sistema: $OS $ARCH"

# ---------------------------------------------------------------- GPU
head_ "GPU"
GPU_KIND="none"
GPU_NAME=""
VRAM_MB=0

if have nvidia-smi && nvidia-smi >/dev/null 2>&1; then
  GPU_KIND="nvidia"
  GPU_NAME="$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -n1 | sed 's/[[:space:]]*$//')"
  VRAM_MB="$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -n1 | tr -dc '0-9')"
  DRIVER="$(nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null | head -n1)"
  ok "NVIDIA detectada: ${GPU_NAME:-desconocida} (${VRAM_MB:-?} MB VRAM, driver ${DRIVER:-?})"
elif have rocm-smi && rocm-smi >/dev/null 2>&1; then
  GPU_KIND="amd-linux"
  GPU_NAME="$(rocm-smi --showproductname 2>/dev/null | grep -i 'card series' | head -n1 | cut -d: -f2- | sed 's/^ *//')"
  warn "AMD/ROCm detectada (${GPU_NAME:-modelo desconocido}); soporte experimental en FooocusPlus"
elif [ "$OS" = "Darwin" ]; then
  GPU_KIND="apple"
  GPU_NAME="$(sysctl -n machdep.cpu.brand_string 2>/dev/null || echo Apple)"
  if [ "$ARCH" = "arm64" ]; then
    ok "Apple Silicon ($GPU_NAME): Pinokio arranca con --gpu-type none y usa Metal/MPS"
  else
    warn "macOS Intel: soporte limitado; espera lentitud notable"
  fi
elif have lspci; then
  GPU_NAME="$(lspci 2>/dev/null | grep -Ei 'vga|3d controller|display' | sed 's/.*: //' | paste -sd' | ' -)"
  if [ -n "$GPU_NAME" ]; then
    warn "GPU sin soporte acelerado detectado: $GPU_NAME"
    info "FooocusPlus arrancaría con --always-cpu (segundos/minutos por imagen)"
  else
    warn "No se detectó GPU dedicada; arrancaría con --always-cpu"
  fi
else
  warn "No se pudo detectar GPU; si no hay NVIDIA, arrancará con --always-cpu"
fi

if [ "$GPU_KIND" = "nvidia" ]; then
  if [ "${VRAM_MB:-0}" -ge 12000 ] 2>/dev/null; then
    ok "VRAM suficiente para Flux (12 GB recomendados)"
  elif [ "${VRAM_MB:-0}" -ge 8000 ] 2>/dev/null; then
    ok "VRAM suficiente para SDXL (8 GB recomendados); Flux irá justo"
  elif [ "${VRAM_MB:-0}" -ge 6000 ] 2>/dev/null; then
    warn "6–7 GB de VRAM: solo presets SDXL ligeros; Flux no es viable"
  else
    warn "Menos de 6 GB de VRAM: usa presets para VRAM baja o SD1.5"
  fi
fi

# ---------------------------------------------------------------- CPU / RAM
head_ "Memoria"
if [ "$OS" = "Darwin" ]; then
  RAM_GB=$(( $(sysctl -n hw.memsize 2>/dev/null || echo 0) / 1024 / 1024 / 1024 ))
else
  RAM_GB=$(awk '/MemTotal/ {printf "%d", $2/1024/1024}' /proc/meminfo 2>/dev/null || echo 0)
fi
CORES=$( (nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo "?") )

if [ "${RAM_GB:-0}" -ge 32 ]; then
  ok "RAM: ${RAM_GB} GB (recomendado ≥16, 32 para SDXL, 48 para Flux)"
elif [ "${RAM_GB:-0}" -ge 16 ]; then
  ok "RAM: ${RAM_GB} GB (suficiente para SDXL; Flux pedirá swap)"
else
  bad "RAM: ${RAM_GB} GB — por debajo del mínimo de 16 GB"
fi
info "núcleos de CPU: $CORES"

if [ "$OS" = "Linux" ]; then
  SWAP_GB=$(awk '/SwapTotal/ {printf "%.1f", $2/1024/1024}' /proc/meminfo 2>/dev/null || echo 0)
  if awk "BEGIN{exit !($SWAP_GB >= 20)}"; then
    ok "Swap: ${SWAP_GB} GB"
  else
    warn "Swap: ${SWAP_GB} GB — el troubleshoot oficial pide ~40 GB; sin swap aparecen Killed/OOM/segfault"
  fi
else
  info "swap: revisar memoria virtual del sistema (macOS la gestiona sola)"
fi

# ---------------------------------------------------------------- disco
head_ "Disco"
TARGET="${HOME:-/}"
FREE_GB=$(df -Pk "$TARGET" 2>/dev/null | awk 'NR==2 {printf "%d", $4/1024/1024}')
if [ "${FREE_GB:-0}" -ge "$MIN_DISK_GB" ]; then
  ok "Libre en $TARGET: ${FREE_GB} GB (mínimo pedido: ${MIN_DISK_GB} GB)"
elif [ "${FREE_GB:-0}" -ge 20 ]; then
  warn "Libre en $TARGET: ${FREE_GB} GB — alcanza para instalar, no para Flux + SDXL"
else
  bad "Libre en $TARGET: ${FREE_GB} GB — insuficiente (mínimo 50 GB)"
fi
info "desglose típico: entorno Python 10–15 GB + modelos 6–25 GB por familia"

# ---------------------------------------------------------------- herramientas
head_ "Herramientas"
for tool in git curl; do
  if have "$tool"; then ok "$tool: $(command -v "$tool")"; else bad "$tool no encontrado (lo necesita el launcher)"; fi
done
if have uv; then
  ok "uv: $(uv --version 2>/dev/null | head -n1)"
else
  info "uv ausente: Pinokio instala su bundle 'ai' y lo aporta"
fi
if have python3; then
  PYV="$(python3 -V 2>&1)"
  info "python3 del sistema: $PYV (FooocusPlus usa su propio venv; 3.10 es lo probado)"
fi

# ---------------------------------------------------------------- puerto
head_ "Puerto 7860"
if have ss && ss -ltn 2>/dev/null | awk '{print $4}' | grep -q ':7860$'; then
  warn "7860 ya está ocupado (¿ComfyUI/Forge abierto?). Ciérralo o cambia el puerto en start.js"
elif have lsof && lsof -nP -iTCP:7860 -sTCP:LISTEN >/dev/null 2>&1; then
  warn "7860 ya está ocupado; ciérralo antes de arrancar FooocusPlus"
else
  ok "7860 libre"
fi

# ---------------------------------------------------------------- red
head_ "Red"
check_url() {
  code=$(curl -sS -o /dev/null -m 10 -w '%{http_code}' "$1" 2>/dev/null)
  [ -z "$code" ] && code=000
  case "$code" in
    2*|3*|401|403) ok "$2 alcanzable (HTTP $code)" ;;
    *) bad "$2 NO alcanzable (HTTP $code) — la instalación o las descargas de modelos fallarán" ;;
  esac
}
check_url "https://github.com" "github.com (clone de la app y auto-update)"
check_url "https://huggingface.co" "huggingface.co (checkpoints, VAE, clip, prompt expansion)"

# ---------------------------------------------------------------- resumen
head_ "Resumen"
if [ "$BLOCKERS" -gt 0 ]; then
  printf "  %sBLOQUEANTE:%s %d fallo(s), %d aviso(s). Resuelve los FAIL antes de instalar.\n" "$c_red" "$c_off" "$BLOCKERS" "$WARNINGS"
  exit 1
elif [ "$WARNINGS" -gt 0 ]; then
  printf "  %sLISTO CON AVISOS:%s %d aviso(s). Puedes instalar; revisa swap/VRAM para no sufrir.\n" "$c_ylw" "$c_off" "$WARNINGS"
else
  printf "  %sLISTO:%s sin avisos. Instala desde Pinokio y arranca.\n" "$c_grn" "$c_off"
fi
exit 0
