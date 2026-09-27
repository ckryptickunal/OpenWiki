#!/usr/bin/env bash
# Put the Lyria instrumental under the silent render: trimmed to the film, a short fade at the end,
# loudness normalised for social platforms (-14 LUFS integrated, -1.5 dBTP).
set -euo pipefail
cd "$(dirname "$0")"
ffmpeg -v error -y -i renders/certain-kind-silent.mp4 -i assets/music.mp3 \
  -filter_complex "[1:a]atrim=0:61.6,afade=t=out:st=60.2:d=1.4,loudnorm=I=-14:TP=-2.5:LRA=11[a]" \
  -map 0:v -map "[a]" -c:v libx264 -crf 18 -preset slow -pix_fmt yuv420p -c:a aac -b:a 256k -ar 48000 -shortest -movflags +faststart renders/certain-kind.mp4
ffmpeg -hide_banner -i renders/certain-kind.mp4 -map 0:a -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I:|Peak:)"
echo "wrote renders/certain-kind.mp4"
