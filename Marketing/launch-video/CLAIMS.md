# Claims ledger: every line in the film and why it is true

Rule: a line goes into the film only if it is either (a) a measured fact with a reproducible method, (b) verified behaviour of OpenWiki 0.3.0 code, (c) a primary-sourced external finding, or (d) plainly rhetorical and not a factual claim. Checked 2026-09-27.

## v4 (26 s kinetic-type cut, current)

Source: `videos/openwiki-launch/` (made with the motion-launch-videos skill). Every line reuses evidence from the v3 rows below; the row-by-row table is in `videos/openwiki-launch/BRIEF.md`.

| On screen | Evidence |
|---|---|
| "You watched it." / "You saved it." / "You can’t find it." + real YC and Paul Graham titles, the typed question | rhetorical; see "The problem, for people" |
| "Your AI starts over." · `ONE IDEA MATCHES 68 RAW FILES · 611,954 TOKENS` | an agent answering from raw files re-reads them per question; numbers from `research/naive_list.py` ("matches", not "reads") |
| "OpenWiki compiles it once." | ingest writes pages once; re-runs read only new or changed sources |
| "A wiki you own." · `FOUNDER BOOK, SAME PIPELINE:` `1,219 VIDEOS + 354 ESSAYS → 8,768 PAGES` + the real link graph | Markdown files on your disk, MIT; "same pipeline", not "built with OpenWiki" |
| "You find the moment." · `$ openwiki search warm network` → the real 0.3.0 result at `[3:46]` | `research/demo-0.3.0/search-output.txt` |
| "Your AI reads less." · `MEDIAN SUMMARY PAGE: 786 TOKENS` · `MEDIAN RAW SOURCE: 3,397 TOKENS` | `founderbook-stats.json`: `median_source_page_tokens` 786, `median_raw_tokens` 3397, over all 1,573 sources. A median statement, not a guarantee: 21% of pages are longer than their source |
| End card: github.com/ckryptickunal/OpenWiki · FREE AND OPEN SOURCE · MIT | LICENSE; no pip line until PyPI is live |

## The problem, for people

| On screen | Type | Evidence |
|---|---|---|
| "You watched it." over a real YC talk chip: *How To Get AI Startup Ideas · 43:49* | rhetorical + real data | Title and duration from the transcript header in Founder Book (`Duration: PT43M49S`). |
| "You saved it." over *Do Things that Don't Scale · paulgraham.com* | rhetorical + real data | A real, public Paul Graham essay. |
| "Now find the part that mattered." with the chip *"which video had the warm network advice?"* | rhetorical | The film does not claim a statistic. Supporting research (not on screen): Bergman, Whittaker & Schooler (2020), 50 participants: only 41 of 250 bookmarked targets (16%) were retrieved through bookmarks. |

Not used: any "% forgotten" or "% of Watch Later never opened" figure. There is no primary source for either.

## The problem, for agents

| On screen | Type | Evidence |
|---|---|---|
| "Your AI agent has the same problem." | rhetorical | An agent answering from raw files has to find and read them each time. Karpathy's gist describes RAG as "rediscovering knowledge from scratch on every question". It is not quoted on screen and implies no endorsement. |
| "One idea, searched in the raw files: 68 files. 611,954 tokens." | measured | `research/naive_list.py`: files matching `don['’]?t scale` in the 1,573 raw sources, tokens by tiktoken o200k. The film says "matched", not "read". |
| "Longer inputs make models less reliable." with a footnote to Chroma, *Context Rot*, 2025 (18 models) | primary source | trychroma.com/research/context-rot: "performance grows increasingly unreliable as input length grows." |

Not used: "it doesn't fit in the context window" (it fits in the 1M-token windows of today's flagship models); "RAG doesn't work"; any endorsement by Karpathy, Anthropic or Chroma.

## What OpenWiki does (0.3.0)

| On screen | Evidence (code on main, 0.3.0) |
|---|---|
| `openwiki youtube --channel @ycombinator` (a channel URL or @handle, or a playlist, with no API key) | `youtube.py:ytdlp_list` plus tests. A channel given by free-text name still needs a key, so the film shows an @handle. Videos without captions are skipped. |
| `openwiki essay`, `openwiki text` | README commands, verified in code. |
| `openwiki ingest --all`: a page for each source, plus pages for people, companies and topics, linked with `[[wikilinks]]` | wiki.py; Founder Book shows the output shape. The film says "people, companies and ideas get their own pages", not "every". |
| "Every quote is checked against the transcript." | `wiki.py:ground_quotes` plus a test. Quotes not found are dropped; YouTube quotes get a timestamp link. Summaries and claims are not checked, so the film says quotes only. |
| `openwiki search warm network` → *Why You're Getting Zero Replies To Your Cold Emails [3:46]* | Real 0.3.0 output (offline BM25, no LLM). |
| `openwiki ask`: "answers from your top passages, with citations" | `search.py:ask` sends the top 6 passages and cites them (verified). The exact "Not in your sources." is guaranteed only when search finds nothing, so the film doesn't claim it. |
| Works with Gemini, OpenAI, OpenRouter, or a local model with Ollama | README providers, verified in code. |
| Re-runs read only new or changed sources | Incremental ingest by file modification time. |
| "Free and open source (MIT). Bring your own LLM, or run one locally." | LICENSE. LLM calls cost money unless you run a local model. |
| End card: github.com/ckryptickunal/OpenWiki | `openwiki-cli` is not on PyPI yet (404 on 2026-09-27), so the film does not show `pip install openwiki-cli`. |

## Real product output on screen

The terminal, wiki page, `search` and `ask` scenes show real OpenWiki 0.3.0 output, captured 2026-09-27 in a workspace of two YouTube videos. The captures are saved in `research/demo-0.3.0/`. Two cosmetic edits only: the workspace path is shown as `~/my-wiki` instead of the scratch path, and long outputs are trimmed with "…". No words are changed.

## Proof, measured on Founder Book

| On screen | Evidence |
|---|---|
| "The pipeline behind Founder Book" | OpenWiki's second commit ships "the Founder Book pipeline as a standalone toolkit". Founder Book was built by that pipeline's original scripts. The film does not say "built with OpenWiki". |
| 1,219 videos + 354 essays → 8,768 linked pages | `research/stats.py`, re-run 2026-09-27, identical. |
| "A typical page: 786 tokens. The source it summarizes: 3,397." | Medians across all 1,573 sources (`stats.py` `per_source`). Corpus-wide, no hand-picked questions. The median ratio is 3.49×; 21% of pages are longer than their source (short clips), so the film shows medians, not a multiplier. |

Not used anymore: the hand-picked "8× fewer tokens on 3 questions" headline. It is kept in FACTS.md as a note only.
