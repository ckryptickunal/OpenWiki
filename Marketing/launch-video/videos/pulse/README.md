# OpenWiki "Pulse": a 30-second film

Black-and-white footage cut on the beat of the Lyria 3.5 instrumental from `../certain-kind` (re-edited to 30 s: build, drop, a 0.33 s silence, the final hit).

| Time | On screen |
|---|---|
| 0–7.7 s | you watched it. / you saved it. / you lost it. (cuts speed up with the music) |
| 7.7 s | the drop: **OpenWiki.** |
| 8.3–12.3 s | every talk. / every essay. / every note. |
| 12.3 s | becomes a page: the real page OpenWiki 0.3.0 wrote for a YC talk (`../../research/demo-0.3.0/source-page-dylan-field.md`), its real path, links and a quote checked against the transcript at 34:39 |
| 14–17 s | a fly-through of Founder Book's real link graph: linked. searchable. yours. |
| 17 s | your AI reads it too. |
| 24 s | the final hit: OpenWiki · turn what you watch into what you know · free and open source · github.com/ckryptickunal/OpenWiki |

Claims: "becomes a page" (one source page per imported video, essay or note), "linked" (`[[wikilinks]]`), "searchable" (`openwiki search`, offline), "yours" (Markdown files on your disk, MIT), "your AI reads it too" (the wiki is plain Markdown an AI agent can read; `openwiki ask` answers from it with citations).

## Build

1. Footage: Pexels (free licence). `pexels-clips.txt` lists each clip's Pexels id and HD file; download them into `../certain-kind/footage/hd/<key>.mp4` (`https://videos.pexels.com/video-files/<id>/<file>`). Clips are not committed.
2. Music: `ffmpeg` edit of `../certain-kind/assets/music.mp3` into `assets/music.wav` (13.41–21.08 s, 21.08–37.08 s, 0.33 s silence, 53.40–59.40 s; loudnorm -14 LUFS).
3. `python3 build.py` cuts and grades the shots into `assets/shots/` and writes `index.html` from `src/template.html`.
4. `npx hyperframes@0.8.80 render -f 60 --workers 1 -o renders/pulse-silent.mp4`, then mux `assets/music.wav`.
