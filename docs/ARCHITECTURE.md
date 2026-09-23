# Architecture

OpenWiki is a small Python package around two artifacts: **raw `.txt` sources** and a generated **Markdown wiki**.

```
sources.json
        │
        ├──────── YouTube Data API (optional) ────────┐
        │                                             │
        ▼                                             ▼
  essay index HTML                          channel uploads feed
        │                                             │
        ▼                                             ▼
  html → text                               youtube-transcript-api
        │                                             │
        └──────────── <folder>/<id>.txt ──────────────┘
                            │
                            ▼
                      parse header
                            │
      analysis JSON, Gemini, or OpenAI-compatible LLM
                            │
                            ▼
              wiki/sources/<id>-<slug>.md
              wiki/entities/<slug>.md      (upsert + backlink)
              wiki/topics/<slug>.md
              wiki/ingested.json           (dedupe by id + mtime)
              wiki/index.md
```

## Raw source format

Every video, essay, or local article becomes one `.txt` file. The header is `Key: value` lines, then a `TRANSCRIPT` marker, then the body. Ingest never modifies these files.

YouTube header:

```
Title: …
Video ID: <youtubeId>
URL: https://www.youtube.com/watch?v=<youtubeId>
Channel: …
Published: …
Duration: …          # optional
Views: …             # optional
Likes: …             # optional
Tags: …              # optional
Transcript Language: English (en)
Auto-generated: False
Snippets: 12

Description:
…

============================================================
TRANSCRIPT
============================================================

<body>
```

Essay header (local notes use the same format):

```
Title: …
Video ID: <prefix>-<slug>
Channel: …
Published: …
Source: https://…

============================================================
TRANSCRIPT
============================================================

<body>
```

Filename rules:

- YouTube: `<videoId>.txt` in the channel folder
- Essay: `<id_prefix>-<slug>.txt` in the site folder
- Skip `_new_urls.txt` during ingest

## YouTube block (`openwiki/youtube.py`)

1. `extract_video_id` — watch URL, `youtu.be`, shorts, live, embed, or bare ID. `extract_playlist_id` for `list=` URLs.
2. `resolve_channel_id` — `channels.list` by id, `forHandle`, or `forUsername` (1 quota unit each); free-text names fall back to `search.list` (100 units). Needs `YOUTUBE_API_KEY`.
3. `select_new_ids` — walk uploads newest-first; stop after two pages that add nothing new.
4. `fetch_transcript` / `pick_transcript` — `youtube-transcript-api`; preferred languages first, then any manual track, then any auto-generated track. Optional `YOUTUBE_PROXY`.
5. `classify_fetch_error` — by exception class first, then message. `no_captions` and `unplayable` are permanent skips; `ip_blocked` and other errors are retried on the next run.
6. `_extract_state.json` — `done` and `permanent_skip` lists so a rerun does not refetch.

A single video works without the Data API: title and channel come from YouTube's public oEmbed endpoint; published date and view counts stay `Unknown`.

## Essay block (`openwiki/essays.py`)

1. Fetch the index URL (or accept saved HTML).
2. Parse links with `kind=generic` (same-site URLs under `base_url`, resolved with `urljoin`) or a named parser.
3. Diff against files already in `folder`.
4. Fetch each new page, keep the `<article>`/`<main>` region if present, `html_to_text`, reject bodies shorter than `--min-chars` (default 400).
5. Detect the publish date, then write the essay header format.

`fetch_url` is injectable so tests never hit the network.

## Wiki block (`openwiki/wiki.py`)

For each `.txt` not already in `wiki/ingested.json` with the same `mtime`:

1. Parse header + body.
2. Analyze with the configured LLM (`openwiki/llm.py`: Gemini, default `gemini-3.1-flash-lite`, or any OpenAI-compatible endpoint) **or** caller-supplied JSON.
3. Write `wiki/sources/<video_id>-<slug>.md` with YAML frontmatter (values quoted when YAML needs it) and `[[wikilinks]]`. Slugs are ASCII when the name has Latin letters and keep Unicode letters otherwise.
4. Upsert `wiki/entities/<slug>.md` and `wiki/topics/<slug>.md`. If the source link is already on the page, return; otherwise append a Source Mention. That is what prevents duplicate mentions and graph loops on re-ingest.
5. Record `{source_file, wiki_page, title, mtime, ingested_at}` in `ingested.json`.
6. Record failures in `wiki/ingest_failures.json` (cleared when a file later succeeds).
7. Rebuild `wiki/index.md`.

`lint` walks every wiki page, counts inbound links, reports missing `[[targets]]`, missing frontmatter, and non-source orphans. `walk_wiki_graph` BFS-follows wikilinks with a visited set.

## Module map

| Module | Responsibility |
|--------|----------------|
| `cli.py` | `openwiki` command and subcommands |
| `textfmt.py` | Raw `.txt` header format: write, parse, slugify |
| `youtube.py` | Channel/playlist discovery, caption download, extract state |
| `essays.py` | Blog index parsing, HTML to text, title/date detection, local notes |
| `llm.py` | Gemini and OpenAI-compatible clients, analysis prompt, JSON repair |
| `wiki.py` | Source/entity/topic pages, manifest, failures, index |
| `lint.py` | Link/frontmatter/orphan report, optional LLM review |
| `links.py` | Wikilink parsing and a cycle-safe graph walk |
| `workspace.py` | Workspace paths and source discovery |
| `env.py` | `.env` loading (workspace and current directory) |
| `templates.py` | Files written by `openwiki init` |

Not included (yet): question answering over the wiki (RAG), a background scheduler (run `openwiki sync` from cron or a GitHub Action instead), and podcast/audio transcription.
