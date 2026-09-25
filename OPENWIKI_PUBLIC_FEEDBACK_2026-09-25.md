# OpenWiki: public problem and user-feedback corpus

**Researched:** 2026-09-25. **Project:** [ckryptickunal/OpenWiki](https://github.com/ckryptickunal/OpenWiki). **Scope:** Transcript ingestion, source retrieval and grounded reuse.

**Reading note:** These are third-party discussions in the problem space, **not feedback from users of this repo**. User posts are experiences or questions, not proof of prevalence. Relevance statements are hypotheses to test, not features claimed to exist. Each record uses stable fields for agents: date, audience, type, evidence, source, and project relevance.

## What emerges

- **Problem cluster:** People lose video insights, extraction can fail or rate-limit, and timestamp provenance matters.
- Maintain source-level provenance and distinguish user-reported failure from speculation, feature request, promotional claim or counterpoint.

## Source records

### OPENWIKI-01
- date: 2025-01-19
- audience: Obsidian user
- type: firsthand
- evidence: Long interviews and tutorials made the author "lose track of the best quotes and ideas"; they built a five-step capture-and-search workflow.
- source: https://www.reddit.com/r/ObsidianMD/comments/1i4vh5u/my_5step_workflow_for_summarizing_youtube_videos/
- OpenWiki relevance: Preserve source links, extracted claims and searchable notes; compare manual friction.

### OPENWIKI-02
- date: 2025-08-02
- audience: Obsidian Clipper user
- type: firsthand
- evidence: Clipping a YouTube video with Claude rather than Gemini returned blocked/unreadable transcripts, including videos that had transcripts.
- source: https://www.reddit.com/r/ObsidianMD/comments/1mfx5q8/obsidian_clipper_youtube_ai_interpreter_other/
- OpenWiki relevance: Distinguish transcript unavailable, provider failure and model failure; never silently produce an empty wiki page.

### OPENWIKI-03
- date: 2025-11-19
- audience: Obsidian extension maintainer
- type: reported user feedback
- evidence: A YouTube technical change broke transcript extraction for months; the maintainer says users emailed about it.
- source: https://www.reddit.com/r/ObsidianMD/comments/1p0u3l9/obsidian_easy_clipper_update_youtube_transcripts/
- OpenWiki relevance: Monitor ingestion reliability and show failures; this is a maintainer report, not direct end-user quotations.

### OPENWIKI-04
- date: 2026-01-05
- audience: Claude user processing podcasts and lectures
- type: firsthand
- evidence: The workflow was "manually ripping transcripts, cleaning up the timestamps, and then pasting them into the context window"; the author also wanted less hallucination on long videos.
- source: https://www.reddit.com/r/ClaudeAI/comments/1q4ii1r/i_got_tired_of_copypasting_transcripts_so_i_built/
- OpenWiki relevance: Automated imports need chunk provenance and timestamp evidence, not just fluent summaries.

### OPENWIKI-05
- date: 2025-06-20
- audience: Long-video summarization experimenter
- type: firsthand
- evidence: A Gemini video summarization attempt returned unsupported claims and timestamp citations outside the provided window, according to the author.
- source: https://www.reddit.com/r/LocalLLaMA/comments/1lg27hk/gemini_models_yes_even_the_recent_25_ones/
- OpenWiki relevance: Check quoted claims against the actual chunk/timestamp before publishing wiki entries.

### OPENWIKI-06
- date: 2025-10-24
- audience: Obsidian video-summarizer user
- type: firsthand
- evidence: A summarizer that had worked for months began returning errors even after new API keys and paid credits.
- source: https://www.reddit.com/r/ObsidianMD/comments/1of6to0/youtube_summary_worked_for_months_now_i_have_open/
- OpenWiki relevance: Show reproducible ingestion errors and recovery steps, not a false successful import.

### OPENWIKI-07
- date: 2025-11-11
- audience: Obsidian Web Clipper user
- type: workflow request
- evidence: The user wants to capture a YouTube transcript without timestamps and cannot change clipper output by hiding timestamps on the video page.
- source: https://www.reddit.com/r/ObsidianMD/comments/1oup9zd/web_clipper_template_for_youtube_without/
- OpenWiki relevance: Support readable transcript views while keeping timestamps as provenance metadata.

### OPENWIKI-08
- date: 2025-10-01
- audience: PKM user seeking NotebookLM alternative
- type: decision need
- evidence: The poster wants answers strictly from uploaded sources and an explicit "not in sources" response, and worries about service downtime.
- source: https://www.reddit.com/r/PKMS/comments/1nv1wjh/alternatives_to_notebooklm_for_closedcorpus_pkm/
- OpenWiki relevance: Make corpus bounds, offline access and abstention clear.

### OPENWIKI-09
- date: 2025-07-24
- audience: yt-dlp subtitle user
- type: GitHub issue
- evidence: A YouTube subtitle request hit HTTP 429 despite the video being playable in browser; the issue includes maintainer troubleshooting.
- source: https://github.com/yt-dlp/yt-dlp/issues/13831
- OpenWiki relevance: Treat rate limits as a distinct ingestion state with careful retry guidance.

### OPENWIKI-10
- date: 2025-08-26
- audience: yt-dlp user
- type: GitHub issue
- evidence: The issue reports the whole video download failing when subtitle download fails.
- source: https://github.com/yt-dlp/yt-dlp/issues/14153
- OpenWiki relevance: Decouple media/transcript failure and report partial results honestly.

### OPENWIKI-11
- date: 2026-04-06
- audience: Video-first PKM user
- type: firsthand
- evidence: The user says videos are hard to fit into PKM because notes cannot link to the exact moment as easily as article highlights.
- source: https://www.reddit.com/r/PKMS/comments/1se2md3/how_do_you_capture_knowledge_from_videos_into/
- OpenWiki relevance: Generate stable timestamp backlinks and preserve quote context.

### OPENWIKI-12
- date: 2025-12-31
- audience: AI knowledge-base experimenter
- type: firsthand
- evidence: Adding more files made answers sound plausible but miss the point, according to the author.
- source: https://www.reddit.com/r/PKMS/comments/1q04r73/the_three_things_that_actually_matter_when/
- OpenWiki relevance: Evaluate retrieval precision and source quality instead of only ingestion volume.

## Candidate checks (not an instruction to implement)

- Reproduce the cited problem with a small example before treating it as a priority.
- Compare a baseline workflow against the proposed improvement; keep failure states and confidence visible.
- Ask actual users of this repository before claiming product-market fit.

## Method and limits

Searched relevant public discussions and opened each linked page. The selected posts are independent problem-space signals; samples are small and selection-biased. Some are questions, feature requests, or interested commentary rather than reproducible bug reports. This is a dated snapshot, not an exhaustive or live feed. No private repository sources were used.
