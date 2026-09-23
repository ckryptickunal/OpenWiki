# Contributing to OpenWiki

Thanks for helping. Bug fixes, new essay-site parsers, new LLM providers, docs, and tests are all welcome.

## Setup

```bash
git clone https://github.com/ckryptickunal/OpenWiki.git
cd OpenWiki
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python -m pytest
ruff check .
```

The test suite runs offline and needs no API keys. Two live smoke tests run only when `YOUTUBE_API_KEY` or `GEMINI_API_KEY` is already set in your environment.

## Making a change

1. Open an issue first for anything larger than a small fix, so we can agree on the approach.
2. Create a branch, make the change, and add a test that fails without it.
3. Mock the network in tests. Save HTML/JSON fixtures under `tests/fixtures/` instead of fetching live pages.
4. Keep `ruff check .` and `python -m pytest` green.
5. Update the README or `docs/` if commands, flags, or file formats change, and add a line to `CHANGELOG.md` under "Unreleased".
6. Open a pull request and fill in the template.

## Updating the website

The landing page lives in `site/`. After changing it and pushing to `main`, publish it with:

```bash
scripts/deploy-site.sh
```

## Good first contributions

- A parser for a blog whose index the `generic` parser handles badly (see "Adding a site-specific parser" in [docs/ADDING_SOURCES.md](docs/ADDING_SOURCES.md)).
- A new source type (podcast RSS, PDF, subtitles files) that writes the standard `.txt` header format described in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).
- Better prompts or post-processing in `openwiki/llm.py` and `openwiki/wiki.py`.

## Rules

- Never commit API keys, `.env` files, or downloaded third-party transcripts and essays.
- Keep dependencies minimal. Standard library first.
- Be kind. See the [Code of Conduct](CODE_OF_CONDUCT.md).

By contributing, you agree that your contributions are licensed under the [MIT License](LICENSE).
