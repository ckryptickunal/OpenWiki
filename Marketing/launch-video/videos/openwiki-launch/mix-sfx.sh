#!/usr/bin/env bash
# Lay the sound effects under the silent render. No music: every sound sits on an on-screen event.
# Cue times follow the FILM timeline in src/film-block.js (120 BPM, a beat is 0.5 s).
# Usage: bash mix-sfx.sh  ->  renders/openwiki-launch-sfx.mp4
set -euo pipefail
cd "$(dirname "$0")"
A=../../assets/audio
IN=renders/openwiki-launch.mp4
OUT=renders/openwiki-launch-sfx.mp4

# time  file                 gain(dB)  skip(s)  length(s, 0 = to the end)  what
# skip drops a file's leading silence so the sound lands on the cue.
CUES="
0.00  swish.wav            12   0     0     lockup leaves, 'You watched it.' rises
2.00  swish.wav            12   0     0     'You saved it.'
4.00  impact-soft.ogg      -9   0     0     hard cut to 'You can't find it.'
4.50  typing.mp3           -5   0.43  0.70  the question types itself
7.00  whoosh-short.mp3     -7   0     0     smash-pan to 'Your AI starts over.'
9.90  whoosh-short.mp3     -5   0     0     mask wipe into 'OpenWiki compiles it once.'
12.00 swish.wav            12   0     0     lines leave upward
12.38 dissolve.wav          9   0     0     the Founder Book graph blooms
15.50 impact-soft.ogg      -9   0     0     hard cut to 'You find the moment.'
16.25 typing.mp3           -5   0.43  0.52  '$ openwiki search warm network'
17.00 click-soft.mp3       -9   0     0     the result appears
18.25 swish.wav            12   0     0     'Your AI reads less.'
21.50 whoosh-short.mp3     -7   0     0     pan to the lockup
21.95 chime.mp3             2   0.41  0     'OpenWiki' lands
"

inputs=(-i "$IN"); filters=""; labels=""; n=1
while read -r t f g skip len _; do
  [ -z "${t:-}" ] && continue
  inputs+=(-i "$A/$f")
  ms=$(awk "BEGIN{printf \"%d\", $t*1000}")
  tr="atrim=start=$skip,asetpts=PTS-STARTPTS,"
  [ "$len" != "0" ] && tr+="atrim=0:$len,afade=t=out:st=$(awk "BEGIN{print $len-0.25}"):d=0.25,"
  filters+="[$n:a]aformat=sample_rates=48000:channel_layouts=stereo,${tr}volume=${g}dB,adelay=${ms}|${ms}[s$n];"
  labels+="[s$n]"; n=$((n+1))
done <<< "$CUES"
count=$((n-1))
filters+="${labels}amix=inputs=$count:normalize=0:duration=longest,apad,atrim=0:26,alimiter=limit=0.7:level=disabled[a]"

ffmpeg -v error -y "${inputs[@]}" -filter_complex "$filters" -map 0:v -map "[a]" \
  -c:v copy -c:a aac -b:a 192k -movflags +faststart "$OUT"
ffmpeg -hide_banner -i "$OUT" -map 0:a -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I:|Peak:)"
echo "wrote $OUT"
