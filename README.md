<div align="center">

# OpenWiki

**Turn YouTube videos, playlists, channels, blogs, and notes into a linked Markdown knowledge base.**

An open-source Python CLI that downloads YouTube transcripts and web articles, then uses an LLM (Gemini, OpenAI, OpenRouter, or a local model through Ollama / LM Studio) to build an Obsidian-compatible wiki of sources, people, companies, and topics, all cross-linked with `[[wikilinks]]`.

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Sponsor](https://img.shields.io/badge/sponsor-%E2%9D%A4-db61a2?logo=githubsponsors&logoColor=white)](https://github.com/sponsors/ckryptickunal)

[Website](https://openwiki-delta.vercel.app/openwiki/) · [Quickstart](#quickstart) · [Commands](#commands) · [LLM providers](#llm-providers) · [FAQ](#faq) · [Sponsor](https://github.com/sponsors/ckryptickunal)

<a href="https://openwiki-delta.vercel.app/openwiki/#film"><img src="site/img/launch-poster.jpg" alt="Watch the 57-second OpenWiki launch film" width="760"></a>

<sub>57-second launch film · <a href="https://openwiki-delta.vercel.app/openwiki/#film">watch on the website</a> · <a href="site/assets/openwiki-launch.mp4">MP4</a> · every claim in it is sourced in <a href="Marketing/launch-video/CLAIMS.md">CLAIMS.md</a></sub>

</div>

---

## Why OpenWiki?

Hours of talks, lectures, podcasts, and essays are hard to search and easy to forget. OpenWiki turns them into a **second brain made of plain Markdown files you own**:

- **YouTube to text:** captions for a single video, a URL list, a whole playlist, or every upload on a channel, with no API key and no source cap. Each line keeps its `[m:ss]` timestamp. Non-English captions work too.
- **Blog and essay scraper:** any article URL or blog index page, with the main text, title, and publish date pulled out automatically.
- **Your own notes:** add local `.txt`, `.md`, or `.html` files.
- **LLM wiki builder:** each source becomes a page with a summary, key ideas, claims, and quotes. People, companies, and topics get their own pages with backlinks to every source that mentions them, and the moment in the video where they come up.
- **Grounded, not invented:** quotes are checked against the transcript and link to the second they were said; quotes the model made up are dropped. Long videos are read in full, in parts, not truncated.
- **Find it again:** `openwiki search` is offline full-text search across everything you saved, and `openwiki ask` answers from your own sources with citations, or says "Not in your sources."
- **Obsidian-ready:** YAML frontmatter and `[[wikilinks]]`. Open the `wiki/` folder as an Obsidian vault and the graph view just works.
- **Incremental:** re-run any time. Downloaded videos and essays are skipped, unchanged files are not re-ingested, and videos without captions are remembered.
- **Works offline:** point it at Ollama or LM Studio and nothing leaves your machine.
- **Good RAG input:** clean, chunked-by-topic Markdown to feed a retrieval pipeline or a long-context model.

OpenWiki implements the [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) pattern described by Andrej Karpathy: instead of retrieving from raw documents at query time, an LLM compiles your sources into a persistent, cross-linked wiki that keeps getting richer with everything you add.

It is the engine behind [Founder Book](https://github.com/ckryptickunal/Founder-Book), a wiki built from Y Combinator videos and Paul Graham and Sam Altman essays.

## Contents

- [Quickstart](#quickstart)
- [What you get](#what-you-get)
- [Commands](#commands)
- [LLM providers](#llm-providers)
- [sources.json](#sourcesjson)
- [Configuration](#configuration)
- [How it works](#how-it-works)
- [FAQ](#faq)
- [Contributing](#contributing)
- [Support the project](#support-the-project)

## Quickstart

Requires Python 3.10 or newer.

```bash
pip install "git+https://github.com/ckryptickunal/OpenWiki.git"
```

Create a workspace (a folder that holds your raw sources and the generated wiki):

```bash
openwiki init --root my-wiki
cd my-wiki
```

Grab a video and an article. Neither needs an API key:

```bash
openwiki youtube "https://www.youtube.com/watch?v=jNQXAC9IVRw" --folder Talks
openwiki essay --url https://www.paulgraham.com/greatwork.html --folder Essays --id-prefix pg
```

Add an LLM key to `.env` in the workspace (or use a [local model](#ollama-or-lm-studio-fully-offline)), then build the wiki:

```bash
echo "GEMINI_API_KEY=your-key" >> .env
openwiki ingest --all
openwiki lint --fix-index
```

Open `my-wiki/wiki/` in Obsidian or any Markdown editor.

<details>
<summary>Install from a clone (for development)</summary>

```bash
git clone https://github.com/ckryptickunal/OpenWiki.git
cd OpenWiki
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python -m pytest
```

</details>

## What you get

```
my-wiki/
├── sources.json                 # channels and blogs to follow
├── .env                         # API keys (git-ignored)
├── Talks/jNQXAC9IVRw.txt        # raw transcript with a metadata header
├── Essays/pg-how-to-do-great-work.txt
└── wiki/
    ├── index.md                 # catalog of every page
    ├── sources/jNQXAC9IVRw-me-at-the-zoo.md
    ├── entities/jawed-karim.md  # people, companies, products
    ├── topics/internet-history.md
    ├── synthesis/               # saved lint reports
    ├── ingested.json            # dedupe manifest
    └── log.md
```

A source page looks like this:

```markdown
---
type: source
title: Why You're Getting Zero Replies To Your Cold Emails
video_id: wr6PMD06hP0
url: https://www.youtube.com/watch?v=wr6PMD06hP0
channel: Y Combinator
published: 2026-09-12T14:00:16Z
tags:
  - sales
  - cold-email
---

# Why You're Getting Zero Replies To Your Cold Emails

## Summary
...
## Key Ideas
...
## Entities
- [[entities/y-combinator|Y Combinator]] (organization): ...
## Topics
- [[topics/founder-led-sales|Founder-led sales]]: ...
## Notable Claims
## Quotes
```

Entity and topic pages collect a **Source Mentions** list that links back to every source, so the wiki grows denser with each ingest.

## Commands

Every command accepts `--root DIR` (before or after the command name). Without it, OpenWiki uses `$OPENWIKI_ROOT` or the current directory. Run `openwiki COMMAND --help` for all options.

| Command | What it does | Keys needed |
|---|---|---|
| `openwiki init` | Create `wiki/`, `sources.json`, `wiki/schema.md`, and a `.gitignore` | none |
| `openwiki youtube URL` | Captions for one video (title and channel via YouTube oEmbed) | none |
| `openwiki youtube --urls-file urls.txt --folder X` | Captions for a list of videos | none |
| `openwiki youtube --playlist URL --folder X` | Every video in a playlist | none (uses yt-dlp; `YOUTUBE_API_KEY` adds metadata) |
| `openwiki youtube --channel @handle` | Every upload on a channel, newest first | none (uses yt-dlp; `YOUTUBE_API_KEY` adds metadata) |
| `openwiki essay --url URL` | One article (title and date detected) | none |
| `openwiki essay [--source NAME]` | New articles from the blogs in `sources.json` | none |
| `openwiki text notes.md ...` | Add local `.txt`, `.md`, or `.html` files | none |
| `openwiki ingest --all` | Build wiki pages for new or changed sources | an [LLM](#llm-providers) |
| `openwiki ingest --file F --analysis-file A.json` | Ingest with precomputed analysis | none |
| `openwiki ingest --dry-run` | Show files, characters, LLM calls and approximate tokens before spending anything | none |
| `openwiki search WORDS` | Offline full-text search; transcript hits link to the exact second | none |
| `openwiki ask "QUESTION"` | Answer from your own sources with numbered citations | an LLM |
| `openwiki sync` | Pull every channel and blog in `sources.json`, then ingest | LLM for ingest |
| `openwiki lint --fix-index` | Report broken links, missing frontmatter, orphans; rebuild the index | none |
| `openwiki lint --review` | Also ask the LLM for maintenance suggestions | an LLM |

Useful options:

- `--lang es,en` on `youtube`/`sync`: preferred caption languages. If none match, the first available track is used instead of skipping the video.
- `--limit N`: cap how many new items are fetched or ingested.
- `--dry-run`: show what would be downloaded (on `ingest`: what the LLM run would cost in calls and tokens).
- `ingest --max-chars N`: characters per LLM call (default 120,000). Longer sources are analyzed in parts and merged.
- `search --scope sources|wiki`: search only raw sources or only wiki pages. `ask -k N`: how many passages to send to the LLM.
- `ingest --force`: re-ingest files even if they have not changed.
- `lint --strict`: exit with status 1 on broken links or missing frontmatter (handy in CI).

## LLM providers

Ingest needs an LLM to write the summaries and pick out entities and topics. Set `LLM_PROVIDER` to choose one explicitly; otherwise OpenWiki uses Gemini if `GEMINI_API_KEY` is set, then an OpenAI-compatible server if `OPENAI_BASE_URL` or `OPENAI_API_KEY` is set.

### Google Gemini

```bash
GEMINI_API_KEY=...            # https://aistudio.google.com/apikey
# GEMINI_MODEL=gemini-3.1-flash-lite   (default)
```

### OpenAI, OpenRouter, Groq, or any OpenAI-compatible API

```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=...
OPENAI_MODEL=<model id>
# OPENAI_BASE_URL=https://api.openai.com/v1       (default)
# OPENAI_BASE_URL=https://openrouter.ai/api/v1
# OPENAI_BASE_URL=https://api.groq.com/openai/v1
```

### Ollama or LM Studio (fully offline)

```bash
ollama pull llama3.1
LLM_PROVIDER=openai
OPENAI_BASE_URL=http://localhost:11434/v1   # LM Studio: http://localhost:1234/v1
OPENAI_MODEL=llama3.1
```

No key is needed for a local server. Larger models give better entity and topic extraction; small models may return malformed JSON more often (OpenWiki retries and repairs common mistakes).

### No LLM at all

Pass `--analysis-file` with JSON containing `summary`, `key_ideas`, `entities`, `topics`, `claims`, `quotes`, and `tags`. See [`examples/demo-talk.analysis.json`](examples/demo-talk.analysis.json).

## sources.json

`openwiki init` writes this file. List the channels and blogs you want to follow, then run `openwiki sync` whenever you want to catch up.

```json
{
  "youtube_channels": [
    { "name": "Y Combinator", "query": "@ycombinator", "channel_id": null, "folder": "Y Combinator" }
  ],
  "essay_sources": [
    {
      "name": "Some Blog",
      "kind": "generic",
      "index_url": "https://example.com/blog/",
      "base_url": "https://example.com/blog",
      "folder": "Some Blog",
      "id_prefix": "sb"
    }
  ]
}
```

- `query` can be a channel URL, `@handle`, name, or `UC...` id. Setting `channel_id` skips the lookup.
- Essay `kind` is `generic` (any same-site links under `base_url`), `paulgraham`, or `samaltman`.

More detail: [docs/ADDING_SOURCES.md](docs/ADDING_SOURCES.md).

## Configuration

Put these in `.env` in your workspace (see [`.env.example`](.env.example)) or export them. `.env` is git-ignored; never commit it.

| Variable | Used for | Default |
|---|---|---|
| `YOUTUBE_API_KEY` | Full video metadata (publish date, views, description) and API-based listing | unset (listing falls back to yt-dlp) |
| `YOUTUBE_PROXY` | Route caption requests through a proxy, e.g. `socks5://127.0.0.1:9050` (Tor) | direct |
| `LLM_PROVIDER` | `gemini` or `openai` | auto-detect |
| `GEMINI_API_KEY` | Gemini ingest and review | unset |
| `GEMINI_MODEL` / `GEMINI_MODEL_LINT` | Gemini model for ingest / `lint --review` | `gemini-3.1-flash-lite` |
| `OPENAI_BASE_URL` | OpenAI-compatible endpoint | `https://api.openai.com/v1` |
| `OPENAI_API_KEY` | Key for that endpoint (not needed for local servers) | unset |
| `OPENAI_MODEL` / `OPENAI_MODEL_LINT` | Model for ingest / `lint --review` | required for `openai` |
| `OPENWIKI_ROOT` | Workspace when `--root` is omitted | current directory |

Get a YouTube Data API key in the [Google Cloud Console](https://console.cloud.google.com/apis/library/youtube.googleapis.com) (free daily quota).

## How it works

```
sources.json ─┬─ youtube ─→ <folder>/<videoId>.txt ─┐
              ├─ essay   ─→ <folder>/<prefix>-<slug>.txt
              └─ text    ─→ Notes/note-<slug>.txt ──┤
                                                    ▼
                           ingest (LLM or analysis JSON)
                                                    ▼
        wiki/sources/  wiki/entities/  wiki/topics/  wiki/index.md
                                                    ▼
                           lint: links, frontmatter, orphans
```

Raw `.txt` files are the source of truth, and the wiki can always be regenerated from them. File formats and module layout are in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). Everything is also importable as a Python library (`from openwiki import Workspace, parse_source_file`).

## FAQ

### How do I download the transcript of a YouTube video as text?

`openwiki youtube <url> --folder Talks` writes `Talks/<videoId>.txt` with the title, channel, language, and full transcript. No API key is needed.

### How do I turn a whole YouTube channel or playlist into notes?

Run `openwiki youtube --channel @handle` or `openwiki youtube --playlist <url> --folder Course`, then `openwiki ingest --all`. No API key is needed: listing uses yt-dlp. There is no cap on the number of videos; run `openwiki ingest --dry-run` first to see how many LLM calls it will take. A free `YOUTUBE_API_KEY` adds publish dates, view counts and descriptions.

### How do I find something I watched but can't remember where?

`openwiki search cold email reply rates` searches every transcript, article and wiki page offline and prints the matching passage with a link to the exact second in the video. For a direct answer, `openwiki ask "What reply rate is good for cold email?"` answers from those passages with numbered citations, or says "Not in your sources." instead of guessing.

### Does the AI change or overwrite my own notes?

No. OpenWiki only writes inside the workspace's `wiki/` folder (and the raw `.txt` source folders it creates). Your own notes are never edited. Every generated page has frontmatter and links back to its source, and quotes are checked against the transcript before they are written. Keeping the workspace in git lets you review and undo any ingest.

### Does it work with non-English videos?

Yes. Pass `--lang` to prefer certain languages; if none match, OpenWiki uses whatever caption track the video has. Page names for people and topics keep non-Latin scripts.

### Can I use it with Obsidian?

Yes. Open the `wiki/` folder as a vault. Pages use YAML frontmatter and `[[folder/page|Title]]` links, so backlinks and the graph view work.

### Can I run it without sending data to the cloud?

Yes. Use Ollama or LM Studio as described in [LLM providers](#ollama-or-lm-studio-fully-offline). Caption and article downloads still come from YouTube and the websites you choose. With a cloud LLM (Gemini, OpenAI), your transcripts are sent to that provider during `ingest` and `ask`; `search` never leaves your machine.

### What does it cost?

OpenWiki is free and MIT-licensed. You pay only for the LLM calls your provider charges for, and nothing with a local model. The YouTube Data API has a free daily quota.

### YouTube is blocking my requests. What can I do?

Caption downloads can fail in two different ways. An IP block (`ip_blocked`) is common from cloud servers: retry later or set `YOUTUBE_PROXY` (for example a local Tor proxy; install `pysocks` for SOCKS). An HTTP 429 (`rate_limited`) means wait and rerun, or use `--limit`; it is not treated as a ban and is not retried in the same run. Neither is marked as a permanent skip. The reason is stored in `<folder>/_extract_state.json`.

### Is it legal to download transcripts and articles?

OpenWiki is meant for personal research and note-taking. Respect each site's terms of service and copyright, and do not republish content you do not have rights to. This repository ships no third-party transcripts or essays.

## Contributing

Bug reports, new essay-site parsers, and new LLM providers are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md). Tests run offline:

```bash
pip install -e ".[dev]"
python -m pytest
ruff check .
```

## Support the project

OpenWiki is built and maintained by [Kunal](https://github.com/ckryptickunal) in spare time. If it saves you hours, please:

- ⭐ **Star the repo** so others can find it
- 💖 **[Sponsor on GitHub](https://github.com/sponsors/ckryptickunal)** to keep new sources and providers coming
- 🐛 [Open an issue](https://github.com/ckryptickunal/OpenWiki/issues) with ideas or bugs

## License

[MIT](LICENSE) © 2026 Kunal (ckryptickunal). This repository contains no third-party transcripts or essays.
