# Wiki Schema

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
