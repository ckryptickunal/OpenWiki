# OpenWiki: the commercial (49 s)

An Apple-style product film for artists, coders, engineers, geeks and the endlessly curious. Every number on screen was measured on 28 Sep 2026; the evidence is in `../../research/commercial-2026-09-28/`.

| Time | Beat | On screen |
|---|---|---|
| 0–7 s | the human truth | Some people learn from everything. / A lecture on the train. / A talk at 2 a.m. / Most of it, you’ll never find again. |
| 7 s | silence | black |
| 8 s | the beat lands | **OpenWiki** · Everything you watch and read, compiled into a wiki you own. |
| 12 s | Speed | **34.6 s**: four hours of talks, compiled into a linked wiki (real `openwiki youtube` / `openwiki ingest` output) |
| 15.5 s | Structure | **49** linked pages, the real link graph of those five talks |
| 18.5 s | Search | **< 2 s** across 10,339 files, offline (real `openwiki search` result) |
| 21.2 s | Ask | **[1:39]**: the answer cites the minute (real `openwiki ask` output, trimmed) |
| 24 s | Cost | **< 1¢** per hour of video |
| 28 s | Or | **$0** with a model on your own machine |
| 31.7 s | | Free. Open source. Yours. |
| 33.7 s | who it is for | Artists. Coders. Engineers. Geeks. Creatives. The endlessly curious. |
| 40 s | montage on the beat | Turn what you watch into what you know. |
| 45.7 s | final hit | OpenWiki · github.com/ckryptickunal/OpenWiki |

Footage behind the numbers keeps running, blurred, so the film never leaves the people.

## Build
1. Footage: Pexels (free licence), listed in `pexels-clips.txt`; download each HD file to `footage/hd/<name>.mp4` from `https://videos.pexels.com/video-files/<id>/<file>`. Then `python3 shots.py` and `python3 backdrops.py`.
2. Music: Lyria 3.5 instrumental (`music/prompt.txt` was the brief for this take), saved as `music/score.mp3`; `bash music/edit.sh` makes the 49.4 s cut.
3. `npx hyperframes@0.8.80 render -f 60 --workers 1 -o renders/silent.mp4`, then mux `music/score-49.wav`.
