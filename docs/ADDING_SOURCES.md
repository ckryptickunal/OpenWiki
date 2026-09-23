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
- `channel_id` is optional. When set, `sync` uses it directly and skips the lookup.
- `folder` is created under `--root`. Transcripts are `<videoId>.txt`.

Pull every channel and essay site at once, then ingest what is new:

```bash
openwiki sync
```

```bash
openwiki youtube --channel "https://www.youtube.com/@somehandle" --folder "My Channel"
```

A playlist (a course, a conference, a podcast season):

```bash
openwiki youtube --playlist "https://www.youtube.com/playlist?list=PL..." --folder "My Course"
```

Or a URL list (one watch URL per line):

```bash
openwiki youtube --urls-file urls.txt --folder "My Channel"
```

Channels and playlists need `YOUTUBE_API_KEY` for the listing. Individual URLs and URL lists work without it (titles come from YouTube oEmbed).

Captions: `--lang hi,en` sets preferred languages. When none match, the first available track is used. Videos with no captions at all, private videos, and age-restricted videos are recorded as `permanent_skip`; rate-limit blocks are not, so they are retried next run.

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

- `generic` — every same-site link under `base_url` (relative links resolved against `index_url`), link text of 5+ characters, feeds/images/PDFs ignored
- `paulgraham` — `*.html` links on a Paul Graham–style index
- `samaltman` — `https://blog.samaltman.com/...` links

```bash
openwiki essay --source "Some Blog"
openwiki essay --url https://example.com/essays/one --folder "Some Blog" --id-prefix sb
```

A file is skipped when `<folder>/<id_prefix>-<slug>.txt` already exists. Bodies shorter than 400 characters (`--min-chars`) are skipped so navigation pages are not saved as essays. When a page has an `<article>` or `<main>` element, only that part is kept. The publish date comes from `article:published_time`, JSON-LD `datePublished`, or `<time datetime>` when present.

For a single URL, the title comes from `og:title`, `<title>`, or the first `<h1>` unless you pass `--title`.

## Local notes and exports

```bash
openwiki text meeting-notes.md research/*.txt --folder Notes
```

The title is the first `# heading` (Markdown), the page title (HTML), or the file name.

## After files land on disk

```bash
openwiki ingest --folder "My Channel"
openwiki ingest --folder "Some Blog"
openwiki lint --fix-index
```

Ingest needs an LLM (see the README's LLM providers section), or `--analysis-file` pointing at JSON with `summary`, `key_ideas`, `entities`, `topics`, `claims`, `quotes`, and `tags`. Failed files are listed in `wiki/ingest_failures.json` and retried next run.

## Adding a site-specific parser

If a blog's index needs special handling, add a function `parse_<site>_index(index_html, base_url, index_url=None) -> list[{"title", "url"}]` to `openwiki/essays.py`, register it in `INDEX_PARSERS`, and add a test with a saved HTML fixture under `tests/fixtures/`.
