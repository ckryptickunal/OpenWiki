// Every number shown on screen lives here, with where it came from.
// Measured 2026-09-27 on Founder Book (git-tracked files at commit 6104879), tokenizer tiktoken o200k_base.
// Reproduce with the stats.py / lookup.py scripts described in Marketing/launch-video/FACTS.md.
window.FACTS = {
  // corpus
  videos: 1219,          // YouTube transcripts: Y Combinator 887, Garry Tan 175, YC Root Access 157
  ycVideos: 887,
  essays: 354,           // Paul Graham 233, Sam Altman 121
  pgEssays: 233,
  hours: 466,            // sum of Duration headers (57 files lack one, so "466+")
  pages: 8768,           // wiki pages: 1,616 sources, 3,686 entities, 3,464 topics, index, schema
  links: 38437,          // [[wikilinks]] across the wiki
  // question: "What does Paul Graham say about doing things that don't scale?"
  naiveFiles: 68,        // raw files a plain text search for the phrase hits
  naiveTokens: 611954,   // tokens in those 68 files
  // three real questions, wiki path vs the raw files behind the same pages
  rawTokens3: 65097,
  wikiTokens3: 8171,
  ratio3: 8,             // 7.97x, shown as "8x"
  // showcase pages (backlink/source counts from the wiki)
  figmaSources: 19,
  dylanSources: 4,
  entrepreneurshipSources: 41,
  ycBacklinks: 945,
  pgBacklinks: 336,
};
