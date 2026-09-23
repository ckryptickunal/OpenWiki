# Architecture

Wiki-Blocks is a small Python package around two artifacts: **raw `.txt` sources** and a generated **Markdown wiki**.

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
              analysis JSON or Gemini
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

YouTube header (from `transcriptor.write_transcript_file`):

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

Essay header (from `fetch_essays.write_essay_file`):

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

## YouTube block (`wikiblocks/youtube.py`)

1. `extract_video_id` — watch URL, `youtu.be`, shorts, or bare ID.
2. `resolve_channel_id` / `get_all_videos` — YouTube Data API v3. Needs `YOUTUBE_API_KEY`.
3. `select_new_ids` — walk uploads newest-first; stop after two pages that add nothing new (`auto_sync.py`).
4. `fetch_transcript` — `youtube-transcript-api`, optional `YOUTUBE_PROXY`.
5. `classify_fetch_error` — `no_captions` and `unplayable` are permanent skips; they are not retries.
6. `_extract_state.json` — `done` and `permanent_skip` lists so a rerun does not refetch.

A single video works without the Data API. Metadata fields then stay `Unknown`.

## Essay block (`wikiblocks/essays.py`)

1. Fetch the index URL (or accept saved HTML).
2. Parse links with `kind=generic` (only URLs under `base_url`) or a named parser.
3. Diff against files already in `folder`.
4. Fetch each new page, `html_to_text`, reject bodies shorter than `--min-chars` (default 400).
5. Write the essay header format.

`fetch_url` is injectable so tests never hit the network.

## Wiki block (`wikiblocks/wiki.py`)

For each `.txt` not already in `wiki/ingested.json` with the same `mtime`:

1. Parse header + body.
2. Analyze: Gemini (`GEMINI_MODEL`, default `gemini-3.1-flash-lite`) **or** caller-supplied JSON.
3. Write `wiki/sources/<video_id>-<slug>.md` with YAML frontmatter and `[[wikilinks]]`.
4. Upsert `wiki/entities/<slug>.md` and `wiki/topics/<slug>.md`. If the source link is already on the page, return; otherwise append a Source Mention. That is what prevents duplicate mentions and graph loops on re-ingest.
5. Record `{source_file, wiki_page, title, mtime, ingested_at}` in `ingested.json`.
6. Rebuild `wiki/index.md`.

`lint` walks every wiki page, counts inbound links, reports missing `[[targets]]`, missing frontmatter, and non-source orphans. `walk_wiki_graph` BFS-follows wikilinks with a visited set.

## Module map

| Wiki-Blocks module | Founder Book source |
|--------------------|---------------------|
| `textfmt.py` | `transcriptor.write_transcript_file`, `fetch_essays.write_essay_file`, `ingest.parse_transcript_file` |
| `youtube.py` | `transcriptor.py`, `fetch_transcript.py`, `extract_channel.py`, `auto_sync.discover_new_video_ids` |
| `essays.py` | `fetch_new_essays.py` |
| `wiki.py` | `ingest.py` (render, upsert, manifest, index) |
| `gemini.py` | `ingest.configure_gemini`, `analyze_transcript`, `extract_json` |
| `lint.py` | `lint_wiki.py` |
| `links.py` | link regex from `lint_wiki.py`, plus a cycle-safe walk |

Not extracted: `query_wiki.py` / RAG Q&A, HuggingFace essay dumps, the Founder Book corpus, `auto_sync` as a background daemon, Tor worker-pool internals (proxy env is supported instead).
