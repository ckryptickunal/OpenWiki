# Case study: ProAstro, a domain knowledge base from 10,000 Hindi videos

ProAstro is a private Vedic astrology (Jyotish) research system. It turns what four astrology teachers say in
their YouTube videos and shorts into **structured, cited rules** ("Saturn in the 7th house delays marriage but
makes it durable", source: channel, video, timestamp, the teacher's reasoning), then matches those rules
against a birth chart computed locally. OpenWiki is the ingestion layer. This page records how it was used and
what had to change, so the next domain project can start from here.

## Why OpenWiki

- Channel and shorts listing without an API key (yt-dlp), and captions with `[m:ss]` timestamps, which become
  "jump to the exact second" citations.
- `--lang hi,en`: most of these channels speak Hindi or Hinglish. The fallback to "any track" mattered.
- The `.txt` header format is a clean contract: everything downstream (triage, extraction, verification)
  reads the same files whether they came from captions or speech-to-text.
- `openwiki search` gives an offline full-text lookup across all transcripts when a structured rule is missing.

## What the scale looked like

| Channel | Videos | Shorts | Notes |
|---|---|---|---|
| AstroIndia666 | 22 | 6,671 | One rule per short ("Rahu in the 9th: rags to riches"), Hindi |
| CookingAstrology | 735 | 23 | English long-form |
| astroarunpandit | 610 | 1,684 | Hindi; many time-bound horoscope videos |
| achosenson29 | 52 | 246 | Hindi/English, philosophical |

## Pipeline

1. **Catalog** every video and short with `yt-dlp --flat-playlist` (titles, durations).
2. **Title triage**, deterministic: regexes for planets, houses, yogas and nakshatras (English, Hindi and
   Devanagari) put rule-shaped titles in tier A and concepts in tier B. Time-bound content (monthly
   horoscopes, dated transits), podcasts and promos go in tier X and are never fetched. This removed about 2,800
   of the 10,000 items before any network or LLM cost.
3. **Transcripts**: `openwiki youtube --urls-file` per channel, in small chunks. After the IP block (see
   [BLOCKED_CAPTIONS.md](../BLOCKED_CAPTIONS.md)): local Whisper for shorts, and Tor with circuit rotation for long
   videos in parallel. That work became `--asr` and `YOUTUBE_TOR_CONTROL_PORT`.
4. **Domain extraction instead of `openwiki ingest`**: the generic entity/topic wiki wasn't the right shape. We
   needed rules whose conditions a program can test against a chart. So extraction writes to a fixed
   **fact vocabulary** (`house:Saturn=7`, `lord_in_house:7=10`, `conj:Jupiter+Moon`, `md=Rahu`), with a
   validator that rejects anything outside it. The extraction was done by low-cost Claude Sonnet sub-agents
   given a written brief, one batch of transcripts each, and the validator was run until it reported 0 errors.
5. **Verification**: a sampler pairs each rule with the transcript lines around its timestamp so a
   fresh-context agent can label it supported, partial, not said, or contradicted.

## Lessons for OpenWiki

- **Precomputed analysis is the extension point.** `ingest --analysis-file` already lets an external
  process supply the analysis. A domain project can keep OpenWiki for fetching, search and file format, and
  plug its own schema in at that point.
- **Speech-to-text belongs in the fetch step.** Regional-language channels often have no captions, and
  caption blocks arrive quickly at volume. `--asr` keeps the same output contract.
- **Triage before fetch.** On big channels most of the cost is in videos you don't need. A title filter is
  cheap, explainable and easy to tune.
- **Keep provenance in the text.** ASR transcripts say so in their header, so later steps can treat
  misheard words with more caution.
