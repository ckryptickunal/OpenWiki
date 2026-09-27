#!/usr/bin/env bash
# Score: Lyria 3.5 take f (music/score.mp3). Removed on bar lines (120 BPM, 2 s bars):
#   0-8.08 s (the first 4-bar intro phrase) and 52.065-60.07 s (4 bars of the final section).
# The beat lands at 8.00 s and the final hit at 45.74 s of the 49.4 s result.
set -euo pipefail
cd "$(dirname "$0")"
ffmpeg -v error -y -i score.mp3 -filter_complex "[0]atrim=8.08:52.085,asetpts=PTS-STARTPTS,afade=t=in:d=0.25[a];[0]atrim=60.07,asetpts=PTS-STARTPTS[b];[a][b]acrossfade=d=0.02:c1=tri:c2=tri,atrim=0:49.42,afade=t=out:st=48.5:d=0.9,loudnorm=I=-14:TP=-1.5:LRA=11" -ar 48000 -c:a pcm_s16le score-49.wav
