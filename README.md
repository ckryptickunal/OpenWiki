# Wiki-Blocks

Reusable building blocks for turning YouTube videos and web essays into a Markdown wiki.

This is the extraction + ingest engine used by [Founder Book](https://github.com/ckryptickunal/Founder-Book), shipped **without** that project's transcript corpus, wiki pages, or API keys. Point it at your own channels and article indexes.

```
sources.json
    │
    ├─ youtube  →  <folder>/<videoId>.txt
    └─ essay    →  <folder>/<prefix>-<slug>.txt
                    │
                    ▼
                 ingest  →  wiki/sources  wiki/entities  wiki/topics
                    │
                    ▼
                  lint   →  wiki/index.md   (optional Gemini review)
```

## What each block does

| Block | Command | Founder Book script it comes from |
|-------|---------|-----------------------------------|
| YouTube | `python -m wikiblocks youtube` | `transcriptor.py`, `fetch_transcript.py`, `extract_channel.py`, `auto_sync.py` discovery |
| Essay / article | `python -m wikiblocks essay` | `fetch_new_essays.py`, `fetch_essays.write_essay_file` |
| Wiki ingest | `python -m wikiblocks ingest` | `ingest.py` |
| Lint / index | `python -m wikiblocks lint` | `lint_wiki.py` |

A new YouTube channel or essay site is a JSON object in `sources.json`. See [docs/ADDING_SOURCES.md](docs/ADDING_SOURCES.md). File formats are in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Prerequisites

- Python 3.10+
- For **channel discovery** and video titles: a YouTube Data API v3 key
- For **Gemini ingest** and `lint --gemini`: a Gemini API key
- Optional: Tor (`brew install tor && tor`) and `pip install pysocks` if YouTube blocks your IP. Set `YOUTUBE_PROXY=socks5://127.0.0.1:9050`

Caption fetch uses `youtube-transcript-api`. Videos with no captions are skipped and recorded in `<folder>/_extract_state.json` under `permanent_skip`.

## Install

```bash
git clone https://github.com/ckryptickunal/Wiki-Blocks.git
cd Wiki-Blocks
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env          # add keys if you have them
cp sources.example.json sources.json
python -m wikiblocks init --root .
```

`init` creates `wiki/sources`, `wiki/entities`, `wiki/topics`, `wiki/synthesis`, and `wiki/schema.md`.

## What works with no API keys

| Step | Keys needed |
|------|-------------|
| Parse / write `.txt` headers | none |
| Extract a **saved** HTML article (`essay --html-file`) | none |
| Ingest with `--analysis-file` (precomputed JSON) | none |
| `lint` and `lint --fix-index` | none |
| Single-video caption download | none (title/channel will be `Unknown` without `YOUTUBE_API_KEY`) |
| Channel discovery / video metadata | `YOUTUBE_API_KEY` |
| Live fetch of a remote article (`essay --url` or `essay` from `sources.json`) | none (HTTP only) |
| Ingest without `--analysis-file` | `GEMINI_API_KEY` |
| `lint --gemini` | `GEMINI_API_KEY` |

There is **no bundled offline LLM**. If `GEMINI_API_KEY` is unset, ingest stops unless you pass `--analysis-file`.

## Environment variables

Copy `.env.example` to `.env`. Values stay empty until you fill them. Never commit `.env`.

| Variable | Required for | Default if unset |
|----------|--------------|------------------|
| `YOUTUBE_API_KEY` | channel listing, titles, dates, view counts | — |
| `GEMINI_API_KEY` | ingest (unless `--analysis-file`), `lint --gemini` | — |
| `GEMINI_MODEL` | ingest model | `gemini-3.1-flash-lite` |
| `GEMINI_MODEL_LINT` | `lint --gemini` | `GEMINI_MODEL`, else `gemini-2.5-flash` |
| `YOUTUBE_PROXY` | caption fetches through SOCKS/HTTP | direct |
| `WIKI_BLOCKS_ROOT` | workspace if you omit `--root` | current directory |

## Copy-paste commands

Run these from a workspace directory (`--root` can be `.`).

### Extract one YouTube video

```bash
python -m wikiblocks youtube https://www.youtube.com/watch?v=jNQXAC9IVRw --folder Talks
```

Writes `Talks/jNQXAC9IVRw.txt`. If the video has no captions the command prints `SKIP` and exits 0.

### Extract one article (local HTML, no network)

```bash
python -m wikiblocks essay \
  --url https://example.com/why-indexes-beat-memory \
  --html-file examples/sample-article.html \
  --title "Why indexes beat memory" \
  --folder Essays \
  --id-prefix ex \
  --min-chars 40
```

### Ingest into the wiki (no Gemini)

```bash
python -m wikiblocks ingest \
  --file examples/demo-talk.txt \
  --analysis-file examples/demo-talk.analysis.json
```

### Ingest with Gemini

```bash
python -m wikiblocks ingest --file Talks/jNQXAC9IVRw.txt
python -m wikiblocks ingest --folder Talks
python -m wikiblocks ingest --all
```

### Lint and rebuild the index

```bash
python -m wikiblocks lint --fix-index
```

## sources.json

`sources.example.json` is the schema. Copy it to `sources.json` and edit the live lists.

```json
{
  "youtube_channels": [
    {
      "name": "Example Channel",
      "query": "https://www.youtube.com/@example",
      "channel_id": null,
      "folder": "Example Channel"
    }
  ],
  "essay_sources": [
    {
      "name": "Example Essays",
      "kind": "generic",
      "index_url": "https://example.com/articles",
      "base_url": "https://example.com",
      "folder": "Example Essays",
      "id_prefix": "ex"
    }
  ]
}
```

`kind` is `generic` (any index of `<a href>` under `base_url`), or the optional site parsers `paulgraham` and `samaltman`. Founder Book channel IDs are listed only under `_examples_not_loaded` in `sources.example.json` and are not read.

Channel extract:

```bash
python -m wikiblocks youtube --channel "https://www.youtube.com/@example" --folder "Example Channel" --dry-run
```

Essay index (only files not already on disk):

```bash
python -m wikiblocks essay --source "Example Essays" --dry-run
```

## Tests

```bash
python -m pytest
```

Tests use local fixtures only. They do not need the network or API keys. Optional live smoke tests run only when `YOUTUBE_API_KEY` / `GEMINI_API_KEY` are already set in the environment; they use a short public video or the tiny fixture transcript, never a third-party corpus.

## License

MIT. Same license as the Founder Book source code. This repo does not ship third-party transcripts or essays.
