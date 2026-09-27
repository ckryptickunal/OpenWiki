# OpenWiki launch film: script and plan

**Message:** Everything you watch and read can compile itself into a wiki you own.
**Format:** 16:9 master at 1920x1080 for Product Hunt (YouTube link), X and LinkedIn on desktop. A 1:1 or 4:5 cut for mobile feeds is a follow-up.
**Length:** 56 seconds. No voiceover: sound-off autoplay means the type tells the story.
**Music:** 120 BPM bed (Happy Beats vol. 1 by ende.app, CC BY 4.0, starting at 16.02s). Sparse, quiet SFX: typing, soft whooshes on transitions, soft impacts on the big numbers.

## Look (v2): Revolut's visual system, researched on Mobbin
- Pure black and deep-navy fields; an electric-blue hero gradient (`#2437ff` → `#0a1260` → black) for the turn and the lockup; one light scene (`#f2f2f4`) for the ingest step.
- Dark glass cards (`#141418`, 1px white 8% border, 26–36px radius), transaction-style rows (round icon, title, grey meta, value on the right), balance-style big numbers over a pill label, round action buttons, a white pill CTA.
- Type: **Inter Display** (opsz 32), Bold 700 at most, uppercase for headlines with tight tracking; JetBrains Mono for terminals. No serif, no grain.
- Accents: blue `#3d5afe` / `#6f86ff`, teal `#2ec4a0` (good), red `#f0506e` (cost).
- Motion (Emil Kowalski's rules): entrances 0.7–1.0s on `cubic-bezier(0.23, 1, 0.32, 1)`; on-screen moves and scene changes 0.8–1.0s on `cubic-bezier(0.77, 0, 0.175, 1)`; exits 0.35–0.4s and always faster than entrances; staggers 60–80ms; blur ≤ 3px; nothing enters from scale(0); every headline holds for 1.5s or more.

## Beat sheet (v2, 56s)

| # | Time | Scene | On screen |
|---|------|-------|-----------|
| 1 | 0.0–6.0 | **Hook** | Saved videos, essays and notes arrive as Revolut-style rows. "YOU WATCHED IT." → "SAVED" → "FORGOT"; the rows dim and the line fades letter by letter. |
| 2 | 6.0–10.3 | **The turn** | A search-style prompt types `openwiki`; the rows are pulled into it; the blue hero rises; "COMPILE IT." |
| 3 | 10.2–16.5 | **The agent problem** | "YOUR AI STARTS FROM ZERO." An analytics card counts the 68 real files a plain search hits: 611,954 tokens. "THAT'S ONE QUESTION." |
| 4 | 16.3–23.2 | **Ingest** (light) | "POINT IT AT [a video / a playlist / a channel / a blog / your notes / all of it]." Real commands in a terminal, flanked by balance cards: 887 YC videos, 233 Paul Graham essays → 8,768 pages. |
| 5 | 23.0–30.2 | **Compile** | A real Dylan Field transcript with `[m:ss]` cues; blue highlights become Person, Company, Topic and verified-quote cards linked back to the text. "EVERY PERSON, COMPANY AND IDEA GETS A PAGE." |
| 6 | 30.0–35.6 | **The graph** | Founder Book's real link graph as a planet horizon under "8,768 · Linked Markdown pages". |
| 7 | 35.5–45.0 | **Tokens** | Two cards: 65,097 vs 8,171 tokens → "8× FEWER TOKENS." Then "YOUR AGENT READS THE PAGE, NOT THE PILE." with a real `openwiki ask` answer and its citations. |
| 8 | 45.0–49.2 | **Works with** | Gemini, OpenAI, OpenRouter, Ollama as round buttons (official marks), then three facts as pills. |
| 9 | 48.8–56.0 | **Lockup** | Blue hero: `>OW` OpenWiki, "Turn what you watch into what you know.", white pill `pip install openwiki-cli`, GitHub URL. |

Every number is sourced in [FACTS.md](FACTS.md).

## Facts checked for the copy
- The CTA uses `pip install openwiki-cli`. The package is built from the 0.3.0 tag and published to PyPI before launch.
- The commands and flags shown come from the README: `openwiki youtube`, `openwiki essay --url … --folder … --id-prefix`, `openwiki ingest --all`, `openwiki lint --fix-index`.
- Providers come from the README: Gemini, OpenAI, OpenRouter, Ollama and LM Studio.
- Karpathy's LLM Wiki gist (2026-04-04) is the idea the README cites. An optional small credit line reads "Built on the LLM Wiki pattern". The film never implies endorsement.
- The cards show real public titles, like PG's "How to Do Great Work". Their thumbnails are the site's own photography, not third-party images.

## Render
```bash
npx hyperframes@0.8.80 render -f 60 -o renders/openwiki-launch-v4.mp4
```
Bake the poster (the scene 6 graph, frame at 34.0s) into frame 0:
```bash
ffmpeg -ss 34.0 -i renders/openwiki-launch-v4.mp4 -frames:v 1 -q:v 2 renders/openwiki-launch-poster.jpg
ffmpeg -i renders/openwiki-launch-v4.mp4 -loop 1 -i renders/openwiki-launch-poster.jpg \
  -filter_complex "[0:v][1:v]overlay=enable='eq(n,0)':shortest=1[v]" -map "[v]" -map 0:a \
  -c:v libx264 -crf 16 -preset slow -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart renders/openwiki-launch.mp4
```
