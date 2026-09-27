# OpenWiki launch film: script and plan

**Message:** Everything you watch and read can compile itself into a wiki you own.
**Format:** 16:9 master at 1920x1080 for Product Hunt (YouTube link), X and LinkedIn on desktop. A 1:1 or 4:5 cut for mobile feeds is a follow-up.
**Length:** 57 seconds. No voiceover and no music: sound effects only, each tied to something on screen (chips, typing, cuts, cards, the lockup).
**Message:** the same problem hurts people and agents. You save hours of video and can't find the part that mattered; an agent faces a pile of raw text where one idea is spread across 68 files. OpenWiki compiles it once into linked pages that both can use.

## Look (v3)
- Craft modelled on Anthropic's "Introducing Claude Opus 4.6": full-bleed documentary photos, each carrying a small caption chip of real, specific text, alternating with macro type on paper. Notion Mail's rhythm: one short claim, then real product.
- OpenWiki's own warm paper (`#faf6f2`) and brown ink; real Unsplash photography (PHOTOS.md) with a light warm grade; no grain.
- Type: Inter Display Bold at most; Fraunces italic for two accent words only; JetBrains Mono for the terminal.
- Everything on screen is real: YC titles and durations from Founder Book, real OpenWiki 0.3.0 terminal, page, search and ask output (research/demo-0.3.0), Founder Book's real link graph.
- Motion (Emil Kowalski): 0.8–0.9s ease-out entrances, ease-in-out moves, faster exits, slow documentary pushes on photos, holds of 1.5s or more.

## Shots

| # | Time | Shot | On screen |
|---|------|------|-----------|
| A | 0.0–3.2 | Photo: watching at night | Chip: Y Combinator · 43:49 · *How To Get AI Startup Ideas* (progress bar fills). "You watched it." |
| B | 3.2–6.4 | Photo: paper pile | Chip: paulgraham.com · saved for later · *Do Things that Don't Scale*. "You saved it." |
| C | 6.4–10.2 | Photo: sticky-note wall | Chip types: "which video had the warm network advice?". "Now find the part that mattered." |
| D | 10.2–13.2 | Paper type | "Your AI agent has the *same* problem." |
| E | 13.2–17.0 | Photo: laptop at night | Chip: search the raw files for "don't scale" → 68 files, 611,954 tokens. "One idea, spread across 68 files." |
| F | 17.0–20.6 | Paper type | "Longer inputs make models less reliable." Footnote: Chroma, Context Rot (2025), 18 models. |
| G | 20.6–23.6 | Paper type | "OpenWiki compiles it *once*." / "Videos, essays and notes become linked Markdown pages you keep." |
| H | 23.6–29.0 | Terminal | Real commands and output: two `openwiki youtube` runs, `openwiki ingest --all` → processed=2; comment: a whole channel works too, no API key. |
| I | 29.0–35.2 | The real page | The generated Dylan Field page; highlights become Person, Company, Topic and checked-quote cards. "People, companies and ideas get their own pages." → "Every quote is checked against the transcript." |
| J | 35.2–39.2 | Graph (night) | The pipeline behind Founder Book: 1,219 videos + 354 essays → 8,768 linked pages. |
| K | 39.2–43.4 | Photo: woman at laptop | Real `openwiki search warm network` → *Why You're Getting Zero Replies To Your Cold Emails [3:46]*. "For you: the exact moment, one search away." |
| L | 43.4–48.0 | Photo: hands typing | Real `openwiki ask` answer with citations; medians 786 vs 3,397 tokens. "For your agents: short pages, with sources." |
| M | 48.0–51.4 | Paper type | Works with Gemini, OpenAI, OpenRouter, or a local model. Free and open source (MIT). |
| N | 51.4–57.0 | Lockup | >OW OpenWiki · "Turn what you watch into what you know." · github.com/ckryptickunal/OpenWiki |

Every line is traced to its evidence in [CLAIMS.md](CLAIMS.md).

## Render
```bash
npx hyperframes@0.8.80 render -f 60 -o renders/openwiki-launch-v5.mp4
```
Bake the poster (shot A at 2.9s) into frame 0 and lift the SFX mix by 7 dB with a limiter:
```bash
ffmpeg -ss 2.9 -i renders/openwiki-launch-v5.mp4 -frames:v 1 -q:v 2 renders/openwiki-launch-poster.jpg
ffmpeg -i renders/openwiki-launch-v5.mp4 -loop 1 -i renders/openwiki-launch-poster.jpg \
  -filter_complex "[0:v][1:v]overlay=enable='eq(n,0)':shortest=1[v];[0:a]volume=7dB,alimiter=limit=0.7:level=disabled[a]" -map "[v]" -map "[a]" \
  -c:v libx264 -crf 16 -preset slow -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart renders/openwiki-launch.mp4
```
