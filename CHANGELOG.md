# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.2.0] - 2026-09-24

Renamed from Wiki-Blocks to **OpenWiki**. The Python package is now `openwiki` and the command is `openwiki` (`python -m openwiki` also works). `WIKI_BLOCKS_ROOT` is now `OPENWIKI_ROOT`.

### Added
- `openwiki sync`: pull every channel and essay site in `sources.json`, then ingest. Previously nothing read `youtube_channels` from `sources.json`.
- `openwiki youtube --playlist` for whole playlists.
- `openwiki text` to add local `.txt`, `.md`, and `.html` files.
- OpenAI-compatible LLM provider: OpenAI, OpenRouter, Groq, and local Ollama / LM Studio for fully offline ingest (`LLM_PROVIDER`, `OPENAI_BASE_URL`, `OPENAI_MODEL`, `OPENAI_API_KEY`).
- `--lang` to choose preferred caption languages.
- Single videos get their title and channel from YouTube oEmbed when no `YOUTUBE_API_KEY` is set.
- Essays: automatic title and publish-date detection; `<article>`/`<main>` extraction.
- `wiki/ingest_failures.json` lists files that failed to ingest, with the error.
- `lint --strict` exits 1 on broken links or missing frontmatter; `lint --review` replaces `lint --gemini` and works with any provider.
- `openwiki --version`; `--root` is accepted before or after the command.
- `openwiki init` writes a workspace `.gitignore` that excludes `.env`.
- CI on Python 3.10 to 3.13, issue and PR templates, contributing guide, code of conduct, security policy, project website.

### Fixed
- Videos whose captions are not in English were permanently skipped as "no captions". The first available track is now used.
- Caption errors are classified by exception type instead of message text, so age-restricted and invalid videos are skipped instead of retried on every run, and IP blocks are never recorded as permanent skips.
- Titles containing `: `, quotes, or a leading `#` produced invalid YAML frontmatter; such values are now quoted.
- Entity and topic names written only in non-Latin scripts all became `untitled.md`; slugs now keep Unicode letters.
- `lint --gemini` defaulted to the retired `gemini-2.5-flash`; the review now uses `gemini-3.1-flash-lite` unless `GEMINI_MODEL_LINT` is set.
- `.env` in the workspace was not loaded when OpenWiki was installed outside the repo.
- `openwiki init` silently skipped writing `sources.json` when installed with pip (the template lived outside the package).
- Missing LLM configuration made every file fail silently; ingest now stops with a clear message.
- Relative links on blog index pages were resolved incorrectly; feeds, images, and the index page itself are no longer treated as essays.
- `@handle` channel lookups used the 100-unit search endpoint; they now use `channels.list(forHandle=...)`.
- Non-YouTube sources with short IDs no longer get a bogus YouTube URL.
- `ingest --all` from the repo root no longer picks up `examples/` and `docs/`.

## [0.1.0] - 2026-09-24

- First release as Wiki-Blocks: YouTube caption extraction, essay extraction, Gemini wiki ingest, and lint.
