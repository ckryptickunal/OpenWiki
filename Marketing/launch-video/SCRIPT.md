# OpenWiki launch film: script and plan

**Message:** Everything you watch and read can compile itself into a wiki you own.
**Format:** 16:9 master at 1920x1080 for Product Hunt (YouTube link), X and LinkedIn on desktop. A 1:1 or 4:5 cut for mobile feeds is a follow-up.
**Length:** 44 seconds. No voiceover: sound-off autoplay means the type has to tell the story by itself.
**Music:** 120 BPM bed (Happy Beats vol. 1, starting at 16.02s so t=0 falls on a strong beat). Cuts and landings sit on the 0.5s beat grid. Sparse SFX: keyboard ticks, card slides, one whoosh, and soft impacts.

## Look: "warm paper, kinetic ink"
- The site's own world: paper `#faf6f2`, ink `#432818`, brown `#73574a`. A night-mode espresso `#15100c` for the terminal and compile scenes.
- One accent: highlighter amber `#f5c451`. It is the colour of *knowledge being marked*: highlights, `[[wikilinks]]` and the underline on the payoff.
- Type: **Fraunces Italic** (variable) for headlines, animated on its weight axis so words *swell like ink* as they land. **Inter** for UI, **JetBrains Mono** for the terminal, and **Playwrite US Trad** for handwritten margin notes.
- Motif: the **`>` prompt** from the app icon. It opens the product half of the film, drives every transition into the terminal, and closes as the logo.
- Motion rules: fast in, long settle. Masked reveals, not fades. Springy card physics. A continuous slow camera drift so no frame is ever dead. Every landing sits on a beat.

## Beat sheet (final cut, 44s)

| # | Time | Scene | On screen |
|---|------|-------|-----------|
| 1 | 0.0–3.3 | **Hook: the pile** | "You **watched** it." → "**saved**" → "**forgot**". Saved videos, essays and notes pile up, then erode. |
| 2 | 3.3–6.0 | **The turn** | `> openwiki` types; the pile is sucked into the prompt; "**Compile it.**" |
| 3 | 6.0–10.5 | **The agent problem** | "Your AI starts from zero." An agent answers one question by reading the raw pile: the 68 real files a plain search hits. "**68 files. 611,954 tokens. One question.**" |
| 4 | 10.2–16.0 | **Ingest** | "Point it at [a video / a playlist / a whole channel / a blog / your notes / all of it]." Real commands: `youtube --channel` (no API key), `essay --source paulgraham`, `ingest --all` → 8,768 pages. |
| 5 | 16.0–22.3 | **Compile** | A real Dylan Field transcript with `[m:ss]` cues. Highlights peel off into Person, Company and Topic pages plus a verified quote with its timestamp. "Every person, company and idea gets its own page." |
| 6 | 22.0–26.5 | **The graph** | Founder Book's real link graph (8,653 connected pages). 1,219 videos + 354 essays → **8,768 linked Markdown pages**. Opens in Obsidian. |
| 7 | 26.2–33.5 | **Tokens** | Same 3 questions: 65,097 vs 8,171 tokens → "**8× fewer tokens.**" Then "Your agent reads the page, not the pile." with a real `openwiki ask` answer and its citations. |
| 8 | 33.5–37.6 | **Proof** | Works with Gemini · OpenAI · OpenRouter · Ollama (the LLM runs on your machine) → "Re-run anytime. Only new or changed sources." → "Free. MIT." |
| 9 | 37.3–44.0 | **Lockup** | `>OW` **OpenWiki** · "Turn what you watch into what you know." · `pip install openwiki-cli` · github.com/ckryptickunal/OpenWiki |

Every number is sourced in [FACTS.md](FACTS.md).

## Facts checked for the copy
- The CTA uses `pip install openwiki-cli`. The package is built from the 0.3.0 tag and published to PyPI before launch.
- The commands and flags shown come from the README: `openwiki youtube`, `openwiki essay --url … --folder … --id-prefix`, `openwiki ingest --all`, `openwiki lint --fix-index`.
- Providers come from the README: Gemini, OpenAI, OpenRouter, Ollama and LM Studio.
- Karpathy's LLM Wiki gist (2026-04-04) is the idea the README cites. An optional small credit line reads "Built on the LLM Wiki pattern". The film never implies endorsement.
- The cards show real public titles, like PG's "How to Do Great Work". Their thumbnails are the site's own photography, not third-party images.

## Render
```bash
npx hyperframes@0.8.80 render -f 60 -o renders/openwiki-launch-v2.mp4
```
Bake the poster (the scene 6 graph, frame at 25.6s) into frame 0:
```bash
ffmpeg -ss 25.6 -i renders/openwiki-launch-v2.mp4 -frames:v 1 -q:v 2 renders/openwiki-launch-poster.jpg
ffmpeg -i renders/openwiki-launch-v2.mp4 -loop 1 -i renders/openwiki-launch-poster.jpg \
  -filter_complex "[0:v][1:v]overlay=enable='eq(n,0)':shortest=1[v]" -map "[v]" -map 0:a \
  -c:v libx264 -crf 16 -preset slow -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart renders/openwiki-launch.mp4
```
