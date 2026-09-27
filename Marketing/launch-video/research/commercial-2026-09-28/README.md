# Evidence for the commercial (measured 2026-09-28)

OpenWiki 0.3.1 (editable install of this repo), default model Gemini 3.1 Flash-Lite, on this Mac over home Wi-Fi.

Five Y Combinator talks, `talks.txt`, 3 h 57 min 48 s in total (durations from the Founder Book transcript headers):
wr6PMD06hP0 12:42 · -7Qz7tSTfUU 40:37 · 0LNQxT9LvM0 58:37 · 12D8zEdOPYo 48:20 · 1D2j8nTjOZ4 1:17:32

**Clean end-to-end run** (the one the film shows): `openwiki init`, `openwiki youtube --urls-file talks.txt`, `openwiki ingest --all`.
Fetch 8.13 s, compile 26.49 s, **total 34.62 s**. Output: `yt-out.txt` (`ok=5 exists=0 skip=0 failed=0`), `ingest-out.txt` (`processed=5 skipped=0 failed=0`).
The wiki: 5 source pages, 26 entity pages, 18 topic pages = **49 linked pages**; graph in `videos/commercial/assets/js/mini-graph.js`.

**Cost** (`bench.py` → `bench.json`, an earlier run of the same five talks with Gemini's own `usage_metadata` recorded):
102,288 input + 5,016 output tokens = **$0.0331** at $0.25 / $1.50 per 1M tokens (ai.google.dev/gemini-api/docs/pricing, standard paid tier, checked 2026-09-28).
$0.0331 / 3.963 h = **0.84¢ per hour of video**. Per talk: $0.0030 (12 min) to $0.0091 (77 min). That run: 1.2–2.3 s fetch and 4.3–5.9 s compile per talk, 32.5 s in total.
With a local model through Ollama there is no API bill (the README documents Ollama; your own hardware and electricity still apply).

**Search**, Founder Book at `6104879`: `candidate_files` = 10,339 files (1,573 raw sources + 8,766 wiki pages).
Six queries through the CLI, wall time including Python start-up: 1.19, 0.51, 1.77, 1.70, 0.45, 1.06 s. All under 2 s. BM25, offline, no LLM.

**Ask** on the five-talk wiki: `openwiki ask "Who should I email first when I start selling?"` answered in 1.74 s with a citation to *Why You're Getting Zero Replies To Your Cold Emails [1:39]*.
