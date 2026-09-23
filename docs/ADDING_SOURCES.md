# Adding a YouTube channel or essay site

All live sources live in `sources.json` at the workspace root. Start from `sources.example.json`.

## YouTube channel

```json
{
  "name": "My Channel",
  "query": "https://www.youtube.com/@somehandle",
  "channel_id": null,
  "folder": "My Channel"
}
```

- `query` can be a channel URL, `@handle`, name, or `UCxxxxxxxxxxxxxxxxxxxxxx` id.
- `channel_id` is optional. Discovery resolves it from `query` when you run `youtube --channel`.
- `folder` is created under `--root`. Transcripts are `<videoId>.txt`.

```bash
python -m wikiblocks youtube --channel "https://www.youtube.com/@somehandle" --folder "My Channel"
```

Or a URL list (one watch URL per line):

```bash
python -m wikiblocks youtube --urls-file urls.txt --folder "My Channel"
```

Needs `YOUTUBE_API_KEY` for the channel listing. Individual URLs still download captions without it.

Already-downloaded IDs and `permanent_skip` entries in `_extract_state.json` are not fetched again.

## Essay / article site

```json
{
  "name": "Some Blog",
  "kind": "generic",
  "index_url": "https://example.com/essays",
  "base_url": "https://example.com",
  "folder": "Some Blog",
  "id_prefix": "sb"
}
```

`kind`:

- `generic` — every `<a href>` whose URL contains `base_url`, title length ≥ 5
- `paulgraham` — `*.html` links on a Paul Graham–style index
- `samaltman` — `https://blog.samaltman.com/...` links

```bash
python -m wikiblocks essay --source "Some Blog"
python -m wikiblocks essay --url https://example.com/essays/one --folder "Some Blog" --id-prefix sb
```

A file is skipped when `<folder>/<id_prefix>-<slug>.txt` already exists. Bodies shorter than 400 characters (configurable) are skipped so index chrome is not saved as an essay.

## After files land on disk

```bash
python -m wikiblocks ingest --folder "My Channel"
python -m wikiblocks ingest --folder "Some Blog"
python -m wikiblocks lint --fix-index
```

Ingest needs `GEMINI_API_KEY`, or `--analysis-file` pointing at JSON with `summary`, `key_ideas`, `entities`, `topics`, `claims`, `quotes`, and `tags`.
