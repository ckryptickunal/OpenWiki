# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- `openwiki youtube --asr`: when a video has no captions, or the captions endpoint blocks or rate-limits your IP, the audio is downloaded with yt-dlp and transcribed locally with Whisper (`mlx-whisper` on Apple Silicon, `faster-whisper` or `openai-whisper` elsewhere; `pip install "openwiki-cli[asr]"`). The transcript keeps the `[m:ss]` format and its header names the speech-to-text backend. Model via `OPENWIKI_ASR_MODEL`.
- `YOUTUBE_TOR_CONTROL_PORT`: with `YOUTUBE_PROXY` pointing at a local Tor, a blocked or rate-limited caption request asks Tor for a new circuit and retries at once instead of failing.
- `docs/BLOCKED_CAPTIONS.md`: a measured field report on caption IP blocks and which workaround to use when.
- `docs/case-studies/proastro.md`: using OpenWiki as the ingestion layer for a 10,000-video Hindi/English domain knowledge base.

## [0.3.1] - 2026-09-27

### Fixed
- Listing a channel or playlist without `YOUTUBE_API_KEY` no longer prints yt-dlp's own notices (for example about the Python version) into OpenWiki's output. yt-dlp errors still go to stderr.

## [0.3.0] - 2026-09-27

Shaped by public feedback research (Reddit r/ObsidianMD, r/PKMS, r/notebooklm, r/ClaudeAI, r/LocalLLaMA; see `docs/research/2026-09-icp-and-roadmap.md`).

### Added
- `openwiki search`: offline full-text search across transcripts, articles and wiki pages (BM25, no LLM). Transcript hits link to the exact second in the video.
- `openwiki ask`: answers from your own sources with numbered citations and timestamp links; replies "Not in your sources." when nothing relevant is found.
- Channels and playlists no longer need `YOUTUBE_API_KEY`: without a key they are listed with yt-dlp (now a dependency). `openwiki sync` uses the same fallback.
- Long transcripts are analyzed in parts and merged instead of being cut off at `--max-chars`.
- `openwiki ingest --dry-run` shows how many files, characters, LLM calls and approximate input tokens a run would use.
- Entity and topic pages record the moment each source first mentions them, with a timestamp link.
- YouTube transcripts keep caption timestamps as `[m:ss]` lines. Quotes that appear in the source get a timestamp link; quotes that do not appear are left out of the wiki page.
- Caption failures record a reason. HTTP 429 is `rate_limited` (wait and rerun) and is separate from `ip_blocked`.

### Fixed
- Ingest no longer writes a wiki page for an empty transcript or an empty model analysis.
- Consecutive quotes on a source page render as separate blockquotes.

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
