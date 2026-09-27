# Where every number in the launch film comes from

Measured on 2026-09-27 against [Founder Book](https://github.com/ckryptickunal/Founder-Book) at commit `6104879`, counting only git-tracked files. Tokens are counted with tiktoken `o200k_base`. The scripts in `research/` reproduce every figure:

```bash
export FOUNDER_BOOK=/path/to/Founder-Book
uv run --with tiktoken python research/stats.py      # corpus, wiki and token totals
uv run --with tiktoken python research/lookup.py     # the three agent questions
uv run --with igraph python research/graph.py        # the graph shown in scene 6
```

The raw results are in `research/founderbook-stats.json`.

| On screen | Value | Method |
|---|---|---|
| "68 files. 611,954 tokens. One question." | 68 files, 611,954 tokens | A plain-text search of the raw corpus for `don['’]?t scale`, then the tokens in every matching file. The scene lists all 68 real file names with their real token counts. |
| "8× fewer tokens" (65,097 vs 8,171) | 7.97× | Three questions: Paul Graham on doing things that don't scale, Dylan Field on design and AI, and "default alive". The wiki path is one entry page plus three source pages. The raw path is the three raw files behind those same pages. |
| 887 transcripts / 233 essays | Y Combinator folder / Paul Graham folder | File counts. |
| 1,219 videos, 354 essays | 887 + 175 + 157 videos; 233 + 121 essays | File counts, one per video ID, no duplicates. |
| 8,768 linked Markdown pages | 1,616 sources, 3,686 entities, 3,464 topics, `index.md` and `schema.md` | Tracked `.md` files under `wiki/`. |
| Graph | 8,653 pages, 15,699 page-to-page links | The largest connected component of the `[[wikilink]]` graph, laid out with Fruchterman–Reingold. |
| Hub labels (Y Combinator 945, Paul Graham 336, Sam Altman 187, Garry Tan 175) | Pages linking to each | `stats.py` top-10 backlinks. |
| Figma 19, Dylan Field 4, Entrepreneurship 41 | Source mentions on each page | Count of `[[sources/…]]` links on the page. |
| Dylan Field transcript with `[m:ss]` cues | Real output | `openwiki youtube https://www.youtube.com/watch?v=-7Qz7tSTfUU` with OpenWiki at `35765bb`. The quote was checked word for word. |
| `openwiki ask "What does default alive mean?"` | Real output | Run on Founder Book with OpenWiki 0.3.0. The answer text is shown verbatim, trimmed to the first two sentences and the first two sources. |

## Caveats, stated plainly
- The wiki is a lossy summary; the raw transcripts stay the source of truth, and OpenWiki keeps them.
- 8× is a small sample (three questions). Per question it ranged from 4.4× to 10.9×. Across the whole corpus, the wiki is 2.87× smaller than the raw text (2,739,706 vs 7,854,123 tokens).
- `index.md` is 147,646 tokens, too big for an agent's first read. Agents should open topic and entity pages directly or use `openwiki search` / `openwiki ask`.
- Founder Book's own `schema.md` says its wiki was built with Gemini 2.5 Flash; the OpenWiki README calls OpenWiki "the engine behind" it.
- Offline with Ollama covers the LLM step. Downloading transcripts and articles still needs the internet.

## Music and sound
Music: "Happy Beats / Business Moves vol. 1" by [ende.app](https://ende.app/en), CC BY 4.0. Commercial use is allowed; ende.app says attribution is appreciated but optional and that its tracks are not registered with YouTube Content ID (checked 2026-09-27). The film uses 16.02s–60.02s of the track. Sound effects: [Kenney](https://kenney.nl) (CC0) plus whooshes synthesized with ffmpeg. Audio files are not committed; `assets/audio/` is rebuilt from those sources.
