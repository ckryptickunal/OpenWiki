#!/usr/bin/env bash
# The 30-second edit of take b: from the first sung word (16.2 s) to the end of the chorus (47.6 s),
# sped up 4.7 % without changing pitch so it lands on exactly 30 s; the drums drop at 15.0 s.
set -euo pipefail
cd "$(dirname "$0")"
ffmpeg -v error -y -i take-b-1.mp3 -af "atrim=16.2:47.6,asetpts=PTS-STARTPTS,atempo=1.047,afade=t=in:d=0.05,afade=t=out:st=29.3:d=0.7,atrim=0:30,loudnorm=I=-14:TP=-2:LRA=11" -ar 48000 -c:a pcm_s16le song-30.wav
ffmpeg -v error -y -i song-30.wav -b:a 192k song-30.mp3
