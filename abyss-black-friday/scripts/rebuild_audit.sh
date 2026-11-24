#!/bin/bash
# Re-render + re-encode con tagging BT.709 completo tras la auditoría.
set -e
cd "$(dirname "$0")/.."
FF=bin/ffmpeg
BSF="h264_metadata=colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1"

encode () {  # $1 nombre  $2 con audio (1/0)
  local n="$1"; local au="$2"
  local ac="-an"; [ "$au" = "1" ] && ac="-c:a copy"
  mv "out/${n}_1080x1920_30fps.mp4" "out/masters/${n}_master.mp4"
  "$FF" -hide_banner -loglevel error -y -i "out/masters/${n}_master.mp4" \
    -c:v libx264 -preset slow -crf 21 -tune film -pix_fmt yuv420p -profile:v high -level 4.2 \
    -colorspace bt709 -color_primaries bt709 -color_trc bt709 -bsf:v "$BSF" \
    $ac -movflags +faststart "out/${n}_1080x1920_30fps.mp4"
  echo "encode+tag OK $n"
}

PYTHONPATH=src python3 -u src/render.py reel
encode reel_black_friday_abyss 1
PYTHONPATH=src python3 -u src/render.py reel --reel-dur 15
encode reel_black_friday_abyss_15s 1
PYTHONPATH=src python3 -u src/render.py stories
encode story_1_pre_black_friday 0
encode story_2_categorias 0
encode story_3_black_friday_cta 0
PYTHONPATH=src python3 src/verify.py
PYTHONPATH=src python3 src/render.py manifest > /dev/null
echo "REBUILD AUDIT COMPLETO"
