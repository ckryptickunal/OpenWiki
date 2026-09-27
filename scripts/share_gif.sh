#!/bin/bash
# Build the link-preview GIF (site/img/share.gif) and still (site/img/share.jpg)
# from the launch film's HyperFrames project in brag-output/composition.
#
#   scripts/share_gif.sh
#
# The GIF uses a "GIF cut" of the film: grain off, the music-reactive glow held
# steady, and the slow photo zoom frozen. Those three effects change every pixel
# on every frame, which made the GIF 13-20 MB; without them it is ~3.5 MB.
# It starts at 2.6s so the first frame (what X, LinkedIn and Facebook show) is the
# full hook: headline, one-line pitch and the three source polaroids.
# Needs: node (npx), ffmpeg, gifsicle, python3 with numpy + Pillow.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
PY="${PYTHON:-python3}"

cp -R "$ROOT/brag-output/composition" "$WORK/cut"
rm -rf "$WORK/cut/snapshots"
"$PY" - "$WORK/cut/index.html" <<'EOF'
import sys
from pathlib import Path
p = Path(sys.argv[1])
css = ('<style id="gif-cut">.grain{display:none!important}'
       '.music-glow{opacity:.18!important;transform:none!important}'
       '#vault-image{transform:scale(1.05)!important}</style>\n</head>')
p.write_text(p.read_text().replace("</head>", css, 1))
EOF
(cd "$WORK/cut" && npx --yes hyperframes@0.8.75 render --quality looks --fps 20 --output "$WORK/cut.mp4")

VF="crop=1920:1008,scale=1200:630:flags=lanczos"
mkdir "$WORK/fr"
ffmpeg -v error -y -ss 2.6 -i "$WORK/cut.mp4" -vf "fps=12,$VF" "$WORK/fr/%04d.png"
ffmpeg -v error -y -ss 2.6 -i "$WORK/cut.mp4" -frames:v 1 -vf "$VF" -q:v 3 "$ROOT/site/img/share.jpg"

# Hold pixels that change by less than 6 levels (encoder shimmer), re-syncing any
# drift every 5 frames so nothing ghosts. Keeps unchanged areas out of GIF frames.
"$PY" - "$WORK/fr" <<'EOF'
import glob, sys
import numpy as np
from PIL import Image
held = None
for i, f in enumerate(sorted(glob.glob(f"{sys.argv[1]}/*.png"))):
    src = np.asarray(Image.open(f).convert("RGB")).astype(np.int16)
    if held is None:
        held = src
    else:
        limit = 3 if i % 5 == 0 else 6
        held = np.where((np.abs(src - held).max(axis=2) < limit)[..., None], held, src)
    Image.fromarray(held.astype(np.uint8)).save(f)
EOF

ffmpeg -v error -y -framerate 12 -i "$WORK/fr/%04d.png" -vf "palettegen=max_colors=192:stats_mode=full" "$WORK/pal.png"
ffmpeg -v error -y -framerate 12 -i "$WORK/fr/%04d.png" -i "$WORK/pal.png" \
  -lavfi "[0:v][1:v]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle" "$WORK/raw.gif"
gifsicle -O3 --lossy=60 "$WORK/raw.gif" -o "$ROOT/site/img/share.gif"
ls -la "$ROOT/site/img/share.gif" "$ROOT/site/img/share.jpg"
