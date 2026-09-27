# OpenWiki: a 30-second music video

An original song (vocals and music generated with Lyria 3.5 from our lyrics, `music/prompt.txt`), cut to 30 s, with footage redrawn as text: every character is a word from the real page OpenWiki 0.3.0 wrote for a YC talk. Inspired by John Knopf's Claude music video (x.com/johnknopf/status/2103698854399099057): warm dark palette, typed lyrics, footage made of text, a glowing particle form.

**Lyrics** (checked against the audio, typed on screen as they are sung):
i watched a thousand hours of light, / saved every word, then lost it overnight. / now every talk, every page i read / comes back to me the moment i need. / turn what you watch into what you know.

**Picture:** 0–13 s text-rendered footage (an eye, glasses reflecting a screen, crumpled paper, a person thinking); 13 s a single warm point; 15 s the drums drop (a talk, pages turning); 18.6 s the real `openwiki search warm network` result (`research/demo-0.3.0/search-output.txt`); 23.4 s Founder Book's real link graph blooms into the name; end: free and open source · github.com/ckryptickunal/OpenWiki.

## Build
1. Song: `python3 music/lyria.py b` (needs GEMINI_API_KEY), then the edit in `music/edit.sh`.
2. Footage: Pexels clips listed in `../pulse/pexels-clips.txt` into `../certain-kind/footage/hd/`; `python3 shots.py` renders the text-footage shots with `ascii.py`.
3. `npx hyperframes@0.8.80 render -f 60 --workers 1 -o renders/song-silent.mp4`, then mux `music/song-30.wav`.
