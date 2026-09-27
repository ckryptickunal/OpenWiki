# OpenWiki: who it is for and what to build next

**Researched:** 2026-09-27. **Method:** Reddit archive search (Arctic Shift, Jan 2025 to Sep 2026, 546 posts across r/ObsidianMD, r/PKMS, r/notebooklm, r/ClaudeAI, r/LocalLLaMA, r/NoteTaking, r/DataHoarder, r/SecondBrain; 17 full comment threads read), a last-30-days sweep (/last30days: Reddit, Hacker News, GitHub, YouTube), web search, and the earlier corpus in [`OPENWIKI_PUBLIC_FEEDBACK_2026-09-25.md`](../../OPENWIKI_PUBLIC_FEEDBACK_2026-09-25.md).

**Reading note:** these are public discussions in the problem space, not feedback from OpenWiki users. Engagement numbers are the archive's snapshot. Comments are paraphrased; links go to the original threads.

## TL;DR

- **The demand is real and large.** The Obsidian Web Clipper post announcing YouTube transcripts drew 1,836 upvotes; the follow-up on interactive transcripts drew 1,087. Karpathy's "LLM Wiki" posts pull hundreds of upvotes and a steady stream of "is there an actual product for this?" questions.
- **The best-fit user** is a technical self-learner who already lives in Obsidian or Markdown, watches long-form YouTube (talks, lectures, podcasts) and wants that knowledge searchable and linked without doing the filing by hand.
- **The three blockers people hit:** getting many videos in at once (playlists, whole channels, 50-source caps), trusting what the AI wrote (invented quotes, links with no reason), and finding things again later.
- **0.3.0 ships the fixes for all three:** keyless channel/playlist import with no cap, transcript-grounded quotes with timestamp links, first-mention timestamps on every entity link, offline `search`, and cited `ask` that says "Not in your sources." Remaining big bets: a human review step, an MCP server for agents, podcasts/audio, and a PyPI release.

## Who uses this (ICP)

### Primary: the self-directed learner with an Obsidian vault

Developers, founders, grad students and AI builders who consume long-form YouTube and blogs for work, are comfortable in a terminal, and keep notes in Obsidian or plain Markdown.

- They lose what they watched: one r/ObsidianMD user built a searchable YouTube knowledge base because they could never find the video where someone explained a concept, and YouTube search only matches titles ([r/ObsidianMD, 53 pts](https://www.reddit.com/r/ObsidianMD/comments/1sgl1jc/)).
- They want the raw transcript in the vault: the Web Clipper transcript feature is the most-upvoted thread in the whole sample ([1,836 pts, 109 comments](https://www.reddit.com/r/ObsidianMD/comments/1rrvbr4/)).
- A near-identical tool ("any YouTube video into Obsidian notes, one file per entity, with wikilinks and frontmatter") drew 64 upvotes and 33 comments, mostly about whether "local" was honest ([r/ObsidianMD](https://www.reddit.com/r/ObsidianMD/comments/1setkmb/)).

### Secondary: AI power users building agent memory

Claude Code, Codex and Hermes Agent users who want an LLM Wiki as persistent context for their agent.

- A pre-compiled wiki cut one user's session context from about 47K tokens to 360 ([r/ClaudeAI, 649 pts, 154 comments](https://www.reddit.com/r/ClaudeAI/comments/1sfdztg/)).
- "How many of you are running an LLM wiki with Claude Code?" ([32 pts](https://www.reddit.com/r/ClaudeAI/comments/1v4rdiv/)) and "Are there actual products built around Karpathy's LLM Wiki idea?" ([r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/comments/1sgtpsg/)) show people looking for a product rather than a script.
- In the last 30 days, the most-starred implementation is [lucasastorian/llmwiki](https://github.com/lucasastorian/llmwiki) (about 1,650 stars, MCP + Claude), and Nous Research bundles an LLM Wiki skill in Hermes Agent.

### Tertiary: bulk researchers and NotebookLM refugees

People who want a whole channel or thousands of documents, or who hit NotebookLM limits.

- A user asked how to summarize a 6,500-video channel after browser extensions stopped at NotebookLM's 50-source limit ([r/notebooklm](https://www.reddit.com/r/notebooklm/comments/1vbweor/)).
- One market researcher described adding YouTube videos one by one as their new nightmare ([r/notebooklm](https://www.reddit.com/r/notebooklm/comments/1sdvzik/)); a batch playlist/channel workaround drew 90 upvotes ([thread](https://www.reddit.com/r/notebooklm/comments/1q1qtzy/)).
- In a thread about ingesting 1K to 100K papers into an LLM wiki, one researcher who ingested about 2,000 papers reported high cost, lower quality in batch mode, and a need to roll back bad ingests ([r/LocalLLaMA, 35 comments](https://www.reddit.com/r/LocalLLaMA/comments/1wmabd3/)).

### Not the target: PKM purists

A vocal part of r/PKMS and r/ObsidianMD wants no AI in their notes, because writing the note is where learning happens ([r/PKMS, 101 pts](https://www.reddit.com/r/PKMS/comments/1tk8g6p/); [r/ObsidianMD, 109 pts, top comment 202 pts](https://www.reddit.com/r/ObsidianMD/comments/1uai1w2/)). OpenWiki should not argue with them. It should make clear that it never edits their own notes, and it can win them later as a searchable reference layer under their hand-written notes.

## What people say (themes)

1. **Bulk import is the first wall.** Playlists and channels are the natural unit, but tools force one URL at a time or cap sources at 50. Workarounds are Chrome extensions and asking Gemini to list links.
2. **Trust decides adoption.** The strongest objections are that LLMs silently corrupt documents when you delegate (a Microsoft paper is cited), that incorrect data is worse than no data, and that users want a clear accept/reject/rename moment. One user asked for a lightweight way to see why a link was created ([r/PKMS](https://www.reddit.com/r/PKMS/comments/1wg8aqc/)). An r/PKMS benchmark of 12 AI memory systems found a plain Markdown wiki tied for first, which a commenter put down to inspectability and predictable retrieval ([r/PKMS](https://www.reddit.com/r/PKMS/comments/1wjr8ki/)).
3. **Finding things again beats capturing more.** In one thread about revisiting video notes, the top answer was that 90% gets buried, so search matters more than organizing upfront ([r/ObsidianMD](https://www.reddit.com/r/ObsidianMD/comments/1sz28fp/)).
4. **"Local" must be literal.** The most-upvoted comment on the competing YouTube-to-Obsidian tool (48 pts) attacked its use of "local" while it sent data to a cloud model.
5. **Cost and scale.** Readers flagged $256 per 1,000 questions as far too expensive for personal use; paper-scale ingest was described as very expensive, with degraded batch quality.
6. **Transcript reliability.** YouTube blocks most cloud IPs, and 429s and empty transcripts are common ([youtube-transcript-api #593](https://github.com/jdepoix/youtube-transcript-api/issues/593)). Users want to know which failure happened.
7. **Timestamps both ways.** People want timestamps as provenance and deep links, but also a clean reading view. The most-upvoted question on the Web Clipper launch asked for a toggle to remove them.

## Change list

Priority is impact on the ICP divided by effort. Evidence refers to the themes above.

| # | Change | Why (evidence) | Status |
|---|---|---|---|
| 1 | Import whole channels and playlists with **no API key and no cap** (yt-dlp listing; API optional for metadata) | Theme 1: one-by-one import pain, 50-source cap, 6,500-video channel | **Shipped in 0.3.0** |
| 2 | **Grounded quotes**: verify every quote against the transcript, drop invented ones, link each to its second | Theme 2: corruption and trust objections | **Shipped in 0.3.0** |
| 3 | **Why was this linked**: entity/topic mentions carry the timestamp where the source first names them | Theme 2: explicit request to see why a link exists | **Shipped in 0.3.0** |
| 4 | `openwiki search`: offline full-text search with timestamp deep links | Theme 3: could not find a video again, 90% of notes buried | **Shipped in 0.3.0** |
| 5 | `openwiki ask`: cited answers from your own sources, "Not in your sources." when unsupported | Theme 2 + earlier corpus: closed-corpus Q&A with abstention | **Shipped in 0.3.0** |
| 6 | Long transcripts analyzed in parts and merged instead of truncated at 120K characters | Theme 5: long podcasts/lectures silently lost content | **Shipped in 0.3.0** |
| 7 | `ingest --dry-run`: files, characters, LLM calls and approximate tokens before spending | Theme 5: cost surprises at scale | **Shipped in 0.3.0** |
| 8 | Honest failure states: `rate_limited` vs `ip_blocked`, reasons stored, no empty pages | Theme 6 | **Shipped in 0.3.0** |
| 9 | Clear privacy copy: what leaves the machine with a cloud LLM vs Ollama; OpenWiki never edits notes outside `wiki/` | Theme 4 and the PKM purists | **Shipped in 0.3.0** (README FAQ, site) |
| 10 | **Review mode**: `ingest --review` writes proposed pages to `wiki/_inbox/` with an accept/reject step before they join the wiki | Theme 2: "clear moment where I accept, reject, rename" | Next |
| 11 | **MCP server** (`openwiki mcp`) exposing search/ask/read-page so Claude Code, Codex and Hermes can use the wiki as memory | Secondary ICP; token-savings thread (649 pts) | Next |
| 12 | Publish `openwiki-cli` to PyPI (`pipx install openwiki-cli`) | Install friction for the primary ICP | In progress (launch session) |
| 13 | Podcasts and local audio/video: RSS feeds plus local transcription (Whisper) for sources without captions | Zoom/voice-memo/podcast workflows; videos without captions are skipped today | Later |
| 14 | Keep entity pages small: periodic consolidation of long "Source Mentions" lists into a summary | A paper-scale user reports their wiki skill inflating to megabytes | Later |
| 15 | Git-friendly safety: `openwiki init --git` and one-command undo of the last ingest | Theme 5: need to roll back bad ingests | Later |
| 16 | Transcript reading view without timestamps (keep them in the raw file) | Theme 7 | Later |
| 17 | Obsidian plugin wrapping search/ask/ingest | Primary ICP lives in Obsidian | Later |

## Positioning

- **Against NotebookLM:** your files, your model, no source cap, works offline with Ollama, and every claim links back to the second it was said.
- **Against DIY LLM-wiki scripts:** a maintained tool that does ingest, lint, search and ask, with tests, and reports YouTube blocking and rate limits as distinct, retryable states instead of failing silently.
- **Against AI-free PKM:** OpenWiki is a reference layer, not a ghost-writer. It never touches your notes, and it keeps receipts.

## Method and limits

- Arctic Shift keyword queries on large subreddits time out, so searches used title matching over bounded date windows. Posts whose titles use other words are missed. Sample: 546 unique posts, 17 comment trees.
- The last-30-days sweep was thin (22 items, several off-topic Hacker News stories), so recent evidence leans on Reddit threads from 2026.
- These are signals from people discussing the problem space, not OpenWiki users. The next step is to ask real users once 0.3.0 is out (GitHub Discussions, r/ObsidianMD showcase).

<details>
<summary>/last30days run footer (2026-09-27)</summary>

```
🌐 last30days v3.25.0 · synced 2026-09-27
✅ All agents reported back!
├─ 🟠 Reddit: 6 threads │ 58 upvotes │ 89 comments
├─ 🔴 YouTube: 1 video │ 11,374 views │ 0/1 with transcripts
├─ 🟡 HN: 14 storys │ 280 points │ 209 comments
├─ 🐙 GitHub: 1 item │ 1,646 stars │ 30 comments
├─ 🗣️ Top voices: r/PKMS, r/LocalLLaMA, r/ChatGPTCoding
├─ 🕒 Recent evidence is thin: only 8 of 22 dated items are from the last 7 days.
└─ 📎 Raw results saved to ~/Documents/Last30Days/karpathy-llm-wiki-raw-v3-2026-09-27.md
```

</details>
