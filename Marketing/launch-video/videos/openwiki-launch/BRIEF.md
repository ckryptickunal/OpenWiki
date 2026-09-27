# Brief: OpenWiki launch film v4

Made with the [motion-launch-videos](https://github.com/Kimeur/motion-launch-videos) skill (MIT): one canvas HTML file, closed-form springs, per-glyph motion, real subframe motion blur, a seamless loop. Every line on screen traces to a row below; the evidence behind each row is in [../../CLAIMS.md](../../CLAIMS.md).

## Deliverable

| | |
|---|---|
| Product | OpenWiki, github.com/ckryptickunal/OpenWiki |
| Format | 1920 x 1080 (16:9) for X, LinkedIn, Product Hunt, YouTube |
| Duration | 26 s (13 bars), seamless loop |
| Frame rate | 60 fps, 120 BPM grid |
| Sound | sound effects on on-screen events only, no music (`mix-sfx.sh`); the film works muted |
| Deliverables | MP4 (H.264, BT.709) silent and with SFX, preview GIF, poster, the single HTML file |

## Facts

| # | On screen | Evidence | Source |
|---|---|---|---|
| F1 | "You watched it." · `Y COMBINATOR · HOW TO GET AI STARTUP IDEAS · 43:49` | rhetorical; a real YC video, duration from its transcript header (`PT43M49S`) | Founder Book transcript |
| F2 | "You saved it." · `PAULGRAHAM.COM · DO THINGS THAT DON’T SCALE` | rhetorical; a real public essay | paulgraham.com/ds.html |
| F3 | "You can’t find it." · `which video had the warm network advice?` | rhetorical; the README's own words: "hard to search and easy to forget" | README.md line 25 |
| F4 | "Your AI starts over." · `ONE IDEA MATCHES 68 RAW FILES · 611,954 TOKENS` | an agent answering from raw files reads them again for each question (Karpathy's LLM Wiki gist: RAG "rediscovering knowledge from scratch on every question", not quoted, no endorsement); the numbers are measured: files matching `don['’]?t scale` in Founder Book's raw sources, tiktoken o200k | research/naive_list.py, FACTS.md |
| F5 | "OpenWiki compiles it once." | `openwiki ingest` writes pages once; re-runs read only new or changed sources (mtime) | openwiki/wiki.py |
| F6 | "A wiki you own." · `FOUNDER BOOK, SAME PIPELINE:` `1,219 VIDEOS + 354 ESSAYS → 8,768 PAGES` + the real Founder Book link graph | plain Markdown files on your disk, MIT; Founder Book was built by the pipeline OpenWiki was extracted from (1,219 videos + 354 essays; 8,768 linked Markdown pages) | README.md, research/stats.py, CLAIMS.md |
| F7 | "You find the moment." · `$ openwiki search warm network` `→ Why You're Getting Zero Replies To Your Cold Emails [3:46]` | real OpenWiki 0.3.0 output (offline BM25, timestamps) | research/demo-0.3.0/search-output.txt |
| F8 | "Your AI reads less." · `MEDIAN SUMMARY PAGE: 786 TOKENS` `MEDIAN RAW SOURCE: 3,397 TOKENS` | medians across all 1,573 Founder Book sources (raw transcript or essay) and their source summary pages (`median_source_page_tokens`, `median_raw_tokens`), no hand-picked questions | research/stats.py (`per_source`) |
| F9 | `OpenWiki` · `github.com/ckryptickunal/OpenWiki` · `FREE AND OPEN SOURCE · MIT` | LICENSE | LICENSE |

## Not on screen

- `pip install openwiki-cli`: not on PyPI yet.
- "8× fewer tokens": the three questions were hand-picked; the film shows corpus medians. 21 % of pages are longer than their source, so "reads less" is shown with the medians, not as a multiplier.
- "Founder Book was built with OpenWiki": it was built by the pipeline OpenWiki was extracted from; the crumb says "same pipeline".
- Any "% forgotten" statistic; "doesn't fit in the context window"; any endorsement.

## Palette (OpenWiki night mode)

| Role | Hex | Use |
|---|---|---|
| bg | #15100C | espresso, the site's night background |
| fg | #FAF6F2 | paper |
| accent | #F5C451 | highlighter amber: the payoff line of each beat, the rule |
| ember | #E5895A | misregistration pass, topic nodes in the graph |
| muted | #B3A293 | metadata crumbs |

## Type

| Role | Face | Use |
|---|---|---|
| display | Inter Display Bold (Inter 4.0 variable, opsz 32, wght 700) | the beats, sentence case |
| label | Inter Display SemiBold | the URL in the lockup |
| mono | JetBrains Mono Medium | crumbs: real titles, commands and numbers |
