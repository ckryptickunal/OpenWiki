# Security Policy

## Reporting a vulnerability

Please do not open a public issue for security problems. Report them privately through GitHub's [private vulnerability reporting](https://github.com/ckryptickunal/OpenWiki/security/advisories/new). You should get a response within a week.

## Scope

OpenWiki runs locally, downloads web pages and captions, and sends source text to the LLM provider you configure. Relevant issues include:

- API keys leaking into logs, generated files, or error messages
- Path traversal or file writes outside the workspace from crafted titles, URLs, or feeds
- Unsafe handling of downloaded HTML or model output

## Keeping keys safe

- Keep keys in `.env` (git-ignored by `openwiki init`) or your environment, never in `sources.json` or code.
- Restrict your YouTube Data API key to the YouTube Data API in the Google Cloud Console.
- Use a local model (Ollama, LM Studio) if your sources are private.
