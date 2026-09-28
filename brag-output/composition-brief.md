# Hyperframes Composition Brief: OpenWiki

## Objective
Create a polished, 20-second Product Hunt launch video for OpenWiki that makes the product flow immediately understandable and feels native to the project's warm editorial brand.

## Output
- Composition directory: `/Users/Kunal/Desktop/wiki-blocks/brag-output/composition/`
- Rendered video: `/Users/Kunal/Desktop/wiki-blocks/brag-output/brag.mp4`
- Format: landscape — 1920x1080
- Duration: 20 seconds

## Source Material
- Project root: `/Users/Kunal/Desktop/wiki-blocks`
- Primary files read: `site/index.html`, `site/assets/site.css`, `site/assets/site.js`, `README.md`, `pyproject.toml`
- Product name: OpenWiki
- Tagline / strongest claim: Turn YouTube videos, blogs, and notes into a linked Markdown knowledge base you keep.
- Key UI or visual moment to recreate: actual CLI ingestion leading to cross-linked Markdown source/entity/topic pages and an Obsidian-ready vault
- Copy that must appear verbatim:
  - `openwiki ingest --all`
  - `[[wikilinks]]`
  - `Free · open source · MIT`

## Creative Direction
- Tone preset: polished
- Creative direction: quiet editorial product film on a sunlit research desk
- Interpretation: spacious but not slow; tactile paper movement, precise terminal interaction, a warm photographic layer, and restrained sound design
- Angle: saved material becomes useful only when it connects; OpenWiki turns scattered sources into owned, linked knowledge
- Hook: `Your bookmarks are not a knowledge base.`
- Outro / punchline: `Turn what you save into what you know.`
- Avoid:
  - Generic SaaS language
  - Abstract filler visuals
  - Neon tech gradients
  - Overly dark terminal-first styling
  - Fast text that cannot be read

## Visual Identity
- Background: `#faf6f2`
- Text: `#432818`
- Accent: `#73574a`
- Display font: Georgia Italic as a local editorial fallback for Fraunces; logo imagery preserves the actual app mark
- Body font: Inter from local project assets
- Visual references from the project: warm archival desk photography, slightly tilted polaroids, brown ink, rounded paper cards, monospace commands, handwritten-feeling wordmark

## Storyboard
Use `/Users/Kunal/Desktop/wiki-blocks/brag-output/brag-plan.md` as the creative contract.

Scene summary:
1. Not a knowledge base — 3.2s — real source imagery arrives; hook locks in
2. Bring anything in — 4.0s — deterministic terminal runs real OpenWiki commands
3. Pages become a wiki — 5.0s — source/entity/topic cards assemble and connect with `[[wikilinks]]`
4. Plain files. Real ownership. — 4.3s — Obsidian-ready vault and provider/ownership truths
5. OpenWiki — 3.5s — actual icon, wordmark, tagline, and MIT pill

## Audio
- Audio role: warm bed with sparse professional accents
- Audio arc: low confident start, a little lift at the linked-wiki payoff, then a clean branded resolution
- Music: `happy-beats-business-moves-vol-12-by-ende-dot-app.mp3`
- Music treatment: baseline volume about 0.28, short fade-in, and a smooth fade to zero over the last 0.8s
- Music cue guidance: bundled preset `/Users/Kunal/.codex/skills/brag/assets/music/cues/happy-beats-business-moves-vol-12-by-ende-dot-app.music-cues.json`; optional locks at 8.74s, 13.11s, and 17.47s
- Audio-reactive treatment: subtle; extracted bass/RMS may slightly lift the paper glow and card presence, never text readability
- Audio-coupled moments:
  - Source cards — soft tactile placements near the early beat grid
  - Terminal — one quiet click/confirmation accent
  - Linked wiki — warm low-risk impact at the completed connection moment
  - Final logo — restrained brand confirmation
- SFX selection guidance: choose only low/medium high-frequency-risk assets; no per-character keyboard barrage
- SFX analysis guidance: `/Users/Kunal/.codex/skills/brag/assets/sfx/sfx-analysis.md`
- Exact SFX choice: use `interface/click_003.ogg`, `impact/impactSoft_medium_001.ogg`, and `interface/bong_001.ogg` sparingly based on the final animation
- Audio files: local copies only under `composition/assets/`

## Hyperframes Instructions
Use current HyperFrames conventions and the installed registry primitives where they fit. `code-terminal-run` is the selected product-demo primitive; `grain-overlay` informs the texture layer but should be adapted to finite seek-safe motion rather than an infinite CSS loop.

Requirements:
- Show the real OpenWiki app icon, project imagery, real CLI copy, and realistic wiki files.
- Keep all text readable at 1920x1080.
- Keep total duration at 20 seconds.
- Use the bundled music and sparse SFX.
- Use cue metadata as timing guidance only.
- Make at least one major reveal land within 0.15s of a strong cue and mark it in source.
- Align sequential card arrivals to the cue beat grid where readability allows and mark them in source.
- Use pre-extracted audio data for subtle visual reactivity if extraction succeeds; document and continue if it fails.
- Run `hyperframes check --snapshots` before preview.
