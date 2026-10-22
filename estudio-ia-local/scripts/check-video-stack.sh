#!/usr/bin/env bash
# ¿Cuál de las cinco herramientas de vídeo-IA local es viable en ESTA máquina?
# Uso: bash scripts/check-video-stack.sh [--min-disk 150]
# Umbrales tomados de los README/instaladores de cada app (ver ../README.md §1).
# Salida: informe + veredicto por app. Código 0 si al menos una es viable, 1 si ninguna.

set -u

MIN_DISK_GB=150
while [ $# -gt 0 ]; do
  case "$1" in
    --min-disk) MIN_DISK_GB="${2:-150}"; shift 2 ;;
    -h|--help) sed -n '2,3p' "$0"; exit 0 ;;
    *) echo "Argumento no reconocido: $1"; exit 2 ;;
  esac
done

c_red=$'\033[31m'; c_ylw=$'\033[33m'; c_grn=$'\033[32m'; c_dim=$'\033[2m'; c_off=$'\033[0m'
if [ ! -t 1 ]; then c_red=; c_ylw=; c_grn=; c_dim=; c_off=; fi

ok()   { printf "  %sOK%s    %s\n"   "$c_grn" "$c_off" "$1"; }
warn() { printf "  %sWARN%s  %s\n"   "$c_ylw" "$c_off" "$1"; }
bad()  { printf "  %sFAIL%s  %s\n"   "$c_red" "$c_off" "$1"; }
info() { printf "  %s·%s     %s\n"   "$c_dim" "$c_off" "$1"; }
h()    { printf "\n%s\n" "$1"; }
have() { command -v "$1" >/dev/null 2>&1; }

OS="$(uname -s)"; ARCH="$(uname -m)"
echo "Vídeo-IA local · chequeo de hardware"
info "sistema: $OS $ARCH"

# ------------------------------------------------------------ GPU
h "GPU"
GPU_KIND=none; GPU_NAME=""; VRAM_MB=0; DRIVER=""

if have nvidia-smi && nvidia-smi >/dev/null 2>&1; then
  GPU_KIND=nvidia
  GPU_NAME="$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -n1 | sed 's/[[:space:]]*$//')"
  VRAM_MB="$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -n1 | tr -dc '0-9')"
  DRIVER="$(nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null | head -n1)"
  ok "NVIDIA: ${GPU_NAME:-?} · ${VRAM_MB:-?} MB VRAM · driver ${DRIVER:-?}"
  DRV_MAJOR="${DRIVER%%.*}"
  if [ "${DRV_MAJOR:-0}" -ge 580 ] 2>/dev/null; then
    ok "Driver ≥580: compatible con el runtime CUDA 13 por defecto de Maestro"
  else
    warn "Driver <580: Maestro bloquea la instalación si detecta que necesita CUDA 13 (pide actualizar a 580+)"
  fi
elif have rocm-smi && rocm-smi >/dev/null 2>&1; then
  GPU_KIND=amd
  GPU_NAME="$(rocm-smi --showproductname 2>/dev/null | head -n1)"
  warn "AMD/ROCm detectada: Maestro, H3 y FramePack NO soportan AMD (solo NVIDIA)"
elif [ "$OS" = "Darwin" ]; then
  GPU_KIND=apple
  GPU_NAME="$(sysctl -n machdep.cpu.brand_string 2>/dev/null)"
  if [ "$ARCH" = arm64 ]; then
    warn "Apple Silicon ($GPU_NAME): Maestro no soporta macOS; H3/FramePack son NVIDIA-only"
  else
    warn "macOS Intel: sin soporte para el stack de vídeo"
  fi
else
  if have lspci; then GPU_NAME="$(lspci 2>/dev/null | grep -Ei 'vga|3d controller' | sed 's/.*: //' | paste -sd' | ' -)"; fi
  warn "Sin NVIDIA utilizable${GPU_NAME:+ ($GPU_NAME)}: las tres apps de vídeo no arrancan"
fi

if [ "$GPU_KIND" = nvidia ]; then
  if   [ "${VRAM_MB:-0}" -ge 24000 ] 2>/dev/null; then info "tramo 24 GB+: Maestro estima 1–3 min por clip"
  elif [ "${VRAM_MB:-0}" -ge 12000 ] 2>/dev/null; then info "tramo 12–16 GB: Maestro con perfil de offload, 4–10 min por clip"
  elif [ "${VRAM_MB:-0}" -ge 6000 ] 2>/dev/null;  then info "tramo 6–8 GB: funciona con offload fuerte, clips de ~10 s a 720p"
  else info "menos de 6 GB: por debajo del mínimo de Maestro"; fi
fi

# ------------------------------------------------------------ RAM / swap
h "Memoria"
if [ "$OS" = Darwin ]; then
  RAM_GB=$(( $(sysctl -n hw.memsize 2>/dev/null || echo 0) / 1024 / 1024 / 1024 ))
else
  RAM_GB=$(awk '/MemTotal/ {printf "%d", $2/1024/1024}' /proc/meminfo 2>/dev/null || echo 0)
fi
if [ "${RAM_GB:-0}" -ge 32 ]; then ok "RAM: ${RAM_GB} GB (recomendado)"
elif [ "${RAM_GB:-0}" -ge 16 ]; then warn "RAM: ${RAM_GB} GB (mínimo de Maestro; clips cortos y paciencia)"
else bad "RAM: ${RAM_GB} GB (por debajo del mínimo de 16 GB)"; fi

if [ "$OS" = Linux ]; then
  SWAP_GB=$(awk '/SwapTotal/ {printf "%.1f", $2/1024/1024}' /proc/meminfo 2>/dev/null || echo 0)
  if awk "BEGIN{exit !($SWAP_GB >= 20)}"; then ok "Swap: ${SWAP_GB} GB"
  else warn "Swap: ${SWAP_GB} GB — con 6–8 GB de VRAM se sufre: apunta a 32–64 GB"; fi
fi

# ------------------------------------------------------------ disco
h "Disco"
FREE_GB=$(df -Pk "${HOME:-/}" 2>/dev/null | awk 'NR==2 {printf "%d", $4/1024/1024}')
if   [ "${FREE_GB:-0}" -ge 500 ]; then ok "Libre: ${FREE_GB} GB (alcanza para la colección completa de Maestro)"
elif [ "${FREE_GB:-0}" -ge "$MIN_DISK_GB" ]; then ok "Libre: ${FREE_GB} GB (mínimo de Maestro: ${MIN_DISK_GB} GB)"
elif [ "${FREE_GB:-0}" -ge 75 ]; then warn "Libre: ${FREE_GB} GB — alcanza para H3 ComfyUI (75 GB) pero no para Maestro"
else bad "Libre: ${FREE_GB} GB — insuficiente incluso para H3 ComfyUI"; fi
info "desglose: Maestro 150 GB · H3 ComfyUI ~75 GB · FramePack ~30 GB · VideoCrafter 2 ~5 GB"

# ------------------------------------------------------------ red
h "Red"
check() {
  code=$(curl -sS -o /dev/null -m 10 -w '%{http_code}' "$1" 2>/dev/null); [ -z "$code" ] && code=000
  case "$code" in
    2*|3*|401|403) ok "$2 alcanzable (HTTP $code)" ;;
    *) bad "$2 NO alcanzable (HTTP $code): las descargas de pesos fallarán" ;;
  esac
}
check "https://github.com" "github.com (clones)"
check "https://huggingface.co" "huggingface.co (todos los pesos)"

h "Puertos"
busy=0
if have ss; then
  for p in 7860 8188; do
    if ss -ltn 2>/dev/null | awk '{print $4}' | grep -q ":${p}\$"; then
      warn "puerto $p ocupado (ComfyUI/Maestro usan 8188/7860)"; busy=1
    fi
  done
fi
[ "$busy" -eq 0 ] && ok "7860 y 8188 libres"

# ------------------------------------------------------------ veredicto por app
h "Veredicto por app"
vram="${VRAM_MB:-0}"
ram="${RAM_GB:-0}"
disk="${FREE_GB:-0}"
viable=0

judge() { # nombre, condición_ok, condición_justa, motivo_fallo
  if [ "$GPU_KIND" != nvidia ]; then printf "  %sNO%s    %-22s %s\n" "$c_red" "$c_off" "$1" "requiere NVIDIA (tienes: $GPU_KIND)"; return; fi
  if eval "$2"; then printf "  %sSÍ%s    %-22s %s\n" "$c_grn" "$c_off" "$1" "$4"; viable=$((viable+1))
  elif eval "$3"; then printf "  %sJUSTA%s %-22s %s\n" "$c_ylw" "$c_off" "$1" "$5"; viable=$((viable+1))
  else printf "  %sNO%s    %-22s %s\n" "$c_red" "$c_off" "$1" "$6"; fi
}

judge "Maestro" \
  '[ "$vram" -ge 12000 ] && [ "$ram" -ge 32 ] && [ "$disk" -ge 150 ]' \
  '[ "$vram" -ge 6000 ] && [ "$ram" -ge 16 ] && [ "$disk" -ge 150 ]' \
  "24 GB+: 1–3 min por clip" "tu tramo: clips más lentos, pero viables" \
  "necesita ≥6 GB VRAM y ≥150 GB libres (tienes ${vram} MB y ${disk} GB)"

judge "MiniMax H3 ComfyUI" \
  '[ "$vram" -ge 24000 ] && [ "$disk" -ge 75 ]' \
  '[ "$vram" -ge 8000 ] && [ "$disk" -ge 75 ]' \
  "32 GB: un modelo por vez sin sudar" "con menos VRAM, offload de ComfyUI" \
  "necesita ~75 GB libres y NVIDIA (tienes ${disk} GB)"

judge "FramePack" \
  '[ "$vram" -ge 8000 ] && [ "$disk" -ge 30 ]' \
  '[ "$vram" -ge 6000 ] && [ "$disk" -ge 30 ]' \
  "8 GB+: sin apuros" "probado en 6 GB; lento" \
  "necesita ≥6 GB VRAM y ~30 GB libres"

printf "  %s—%s    %-22s %s\n" "$c_dim" "$c_off" "VideoCrafter 2" "instalable en casi cualquier GPU, pero 512 px y de 2024: no lo recomiendo"
printf "  %s—%s    %-22s %s\n" "$c_dim" "$c_off" "arena-hard-auto" "no genera imagen ni vídeo: es un benchmark de LLM (necesita API keys de pago)"

h "Resumen"
if [ "$viable" -gt 0 ]; then
  printf "  %s%d app(s) viable(s).%s Para la historia: Maestro. Para la landing y el 3D: código, no generación.\n" "$c_grn" "$viable" "$c_off"
  exit 0
else
  printf "  %sNinguna viable en esta máquina.%s Alternativas: API en la nube para los clips, o el pipeline offline de abyss-historia-15s (sin GPU).\n" "$c_red" "$c_off"
  exit 1
fi
