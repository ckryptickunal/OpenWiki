"""Files written by `openwiki init`."""

SCHEMA_MD = """# Wiki Schema

Generated pages live under `wiki/`. Raw `.txt` transcripts and essays are the source of truth.

## Directory roles

- `sources/`: one page per transcript, essay, or local file.
- `entities/`: people, companies, products, organizations, named projects.
- `topics/`: reusable concepts.
- `synthesis/`: lint reports and cross-source notes.
- `index.md`: catalog rebuilt after ingest.
- `log.md`: append-only ingest/lint log.
- `ingested.json`: dedupe manifest keyed by source id + file mtime.

## Page format

Every generated page uses YAML frontmatter:

```yaml
---
type: source | entity | topic | synthesis
title: Page title
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: []
tags:
  - tag
---
```

Source pages also include `video_id`, `url`, `channel`, and `published`.

## Linking

Use Obsidian-style wikilinks: `[[entities/some-name|Some Name]]`.
Entity and topic pages keep a `## Source Mentions` list that points back at sources.

## Filename conventions

- Raw YouTube file: `<videoId>.txt` inside a per-channel folder.
- Raw essay file: `<id_prefix>-<slug>.txt` inside a per-site folder.
- Source wiki page: `<video_id>-<slugified-title>.md`.
- Entity/topic page: `<slugified-name>.md`.
"""

# Kept byte-identical to the repo-root sources.example.json (a test checks this).
SOURCES_EXAMPLE = """{
  "_comment": "Copy to sources.json (or run `openwiki init`) and edit. Only youtube_channels and essay_sources are read. For a channel, `query` can be a URL, @handle, or name; set `channel_id` (UC...) to skip the lookup. Essay `kind` is generic, paulgraham, or samaltman.",
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
  ],
  "_examples_not_loaded": {
    "_comment": "Documentation only; the loader ignores this key. Move an entry into the lists above to use it.",
    "youtube_channels": [
      {
        "name": "Y Combinator",
        "query": "https://www.youtube.com/@ycombinator",
        "channel_id": "UCcefcZRL2oaA_uBNeo5UOWg",
        "folder": "Y Combinator"
      }
    ],
    "essay_sources": [
      {
        "name": "Paul Graham",
        "kind": "paulgraham",
        "index_url": "https://www.paulgraham.com/articles.html",
        "base_url": "https://www.paulgraham.com/",
        "folder": "Paul Graham",
        "id_prefix": "pg"
      },
      {
        "name": "Sam Altman",
        "kind": "samaltman",
        "index_url": "https://blog.samaltman.com/",
        "base_url": "https://blog.samaltman.com",
        "folder": "Sam Altman",
        "id_prefix": "sa"
      }
    ]
  }
}
"""

WORKSPACE_GITIGNORE = """# API keys: never commit
.env

# Crawl state and logs
**/_extract_state.json
wiki/ingest_failures.json
*.log
"""
