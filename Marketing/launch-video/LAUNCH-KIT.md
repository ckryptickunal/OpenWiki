# OpenWiki launch kit

Everything below uses only numbers from [FACTS.md](FACTS.md). Before posting, publish `openwiki-cli` to PyPI; every post says `pip install openwiki-cli`.

Assets:
- `renders/openwiki-launch.mp4`: master, 56s, 1080p60, 19 MB. Use it for X, LinkedIn and YouTube.
- `site/assets/openwiki-launch.mp4`: web copy, 30 fps, 6 MB.
- `site/img/launch-poster.jpg`: poster/thumbnail, 1280x720.

Links: repo https://github.com/ckryptickunal/OpenWiki · site https://openwiki-delta.vercel.app/openwiki/ · showcase https://github.com/ckryptickunal/Founder-Book

Voice note: I had no sample of your past posts, so the voice is unverified. Read each post aloud and change anything you wouldn't say.

---

## X (thread, video on tweet 1, links in the first reply)

**1/**
One question about "do things that don't scale", asked of 1,219 YC videos and 354 Paul Graham and Sam Altman essays.

A plain text search hits 68 files. 611,954 tokens.

I built OpenWiki so my agents read one linked page instead. Open source, MIT.

[attach video]

**2/**
It's a Python CLI. You point it at a YouTube video, a playlist, a whole channel, a blog, or your own notes:

openwiki youtube --channel @ycombinator --folder "Y Combinator"
openwiki essay --source paulgraham
openwiki ingest --all

No API key needed to pull channels or playlists.

**3/**
An LLM (Gemini, OpenAI, OpenRouter, or a local model through Ollama) writes a page for every source, person, company and topic, then links them with [[wikilinks]].

Quotes are checked against the transcript and linked to their timestamp in the video.

**4/**
The numbers, measured on my own corpus (Founder Book):

1,219 videos + 354 essays → 8,768 Markdown pages, 38,437 links.
The same 3 questions: 65,097 tokens reading raw transcripts vs 8,171 reading the wiki pages. About 8x fewer.

The scripts that produced these numbers are in the repo.

**5/**
New in 0.3.0:
openwiki search: offline full-text search with timestamps
openwiki ask: answers with citations, and prints "Not in your sources." when it can't find one

It's plain Markdown, so Obsidian opens it and any agent can read it.

**First reply:**
pip install openwiki-cli
github.com/ckryptickunal/OpenWiki

Founder Book, the wiki in the video: github.com/ckryptickunal/Founder-Book

---

## LinkedIn (video native, link in the first comment)

Ask an AI agent one question about Paul Graham's "do things that don't scale" across 1,573 YC transcripts and essays, and a plain text search pulls in 68 files: 611,954 tokens of context.

So I built OpenWiki, an open-source CLI that turns YouTube channels, essays and notes into a linked Markdown wiki.

I tested it on 1,219 Y Combinator and founder videos plus 354 Paul Graham and Sam Altman essays. That became 8,768 pages with 38,437 links between them.

What that changes for an agent: on three real questions, reading the wiki pages took 8,171 tokens. Reading the raw transcripts behind those same pages took 65,097. That's about 8x less context per answer, and every answer points back to its source.

For people, the same folder opens in Obsidian as a searchable graph.

It works with Gemini, OpenAI, OpenRouter, or a local model through Ollama, and it's free under MIT.

The 56-second film shows the whole flow. Link to the repo is in the first comment.

**First comment:**
Repo: https://github.com/ckryptickunal/OpenWiki
Install: pip install openwiki-cli
The wiki from the video: https://github.com/ckryptickunal/Founder-Book

---

## Product Hunt

The video must be a YouTube link (Product Hunt only accepts YouTube). Upload the master to YouTube first; the description is below.

**Name:** OpenWiki
**Tagline (59/60 chars):** Turn YouTube, essays and notes into a wiki your agents read
**Description (≤260 chars):**
Open-source CLI that compiles YouTube channels, playlists, blogs and notes into a linked Markdown wiki. Your AI agents read one short page instead of raw transcripts, and it opens in Obsidian. Works with Gemini, OpenAI or Ollama. MIT.
**Topics:** Developer Tools, Artificial Intelligence, Open Source, Productivity
**Gallery (1270x760, 2+):** the YouTube film, then stills from the film at 34.0s (graph), 39.8s (8x fewer tokens), 28.9s (pages), 22.2s (ingest) and 53.0s (lockup).
**Thumbnail (240x240):** the >OW app icon.

**Maker comment:**
Hi Product Hunt, I'm Kunal.

[Your one or two sentences: why you started. For example, the YC talks and Paul Graham essays you kept saving, and what you wanted your agents to do with them. Only you can write this part.]

OpenWiki is my fix. It downloads transcripts and articles, and an LLM compiles them into Markdown pages for each source, person, company and topic, all cross-linked. Andrej Karpathy described this "LLM Wiki" pattern in April; OpenWiki is a CLI that does it for YouTube channels and blogs in bulk.

What I measured on my own corpus (1,219 videos and 354 essays): 8,768 pages, and about 8x fewer tokens per answer on three test questions. The method and scripts are in the repo, so you can check them.

It's free and MIT. I'd love to hear which sources you'd point it at first, and where it breaks.

---

## YouTube (for the Product Hunt link)

**Title:** OpenWiki: turn YouTube channels and essays into a linked wiki your AI agents can read
**Description:**
OpenWiki is an open-source CLI that compiles YouTube videos, playlists, channels, blogs and notes into a cross-linked Markdown wiki (Obsidian-compatible).

Install: pip install openwiki-cli
Code: https://github.com/ckryptickunal/OpenWiki
The wiki in this video (1,219 videos + 354 essays → 8,768 pages): https://github.com/ckryptickunal/Founder-Book
Every number in the video, with the method: https://github.com/ckryptickunal/OpenWiki/blob/main/Marketing/launch-video/FACTS.md

Music: "Happy Beats / Business Moves vol. 1" by ende.app (CC BY 4.0). Sound effects: Kenney (CC0).

---

## Reddit

Each post discloses that you built it. Reddit rules change, so read each sidebar on the day. Post the video natively where the subreddit allows it.

### r/ObsidianMD
**Title:** I built a CLI that turns YouTube channels and essays into an Obsidian vault (8,768 linked pages from YC talks + Paul Graham essays)
**Body:**
I made this, so full disclosure. OpenWiki downloads transcripts and articles, then an LLM writes a page per source, person, company and topic with [[wikilinks]] and YAML frontmatter. You open the `wiki/` folder as a vault and the graph view works out of the box.

My test vault: 1,219 YouTube videos and 354 essays became 8,768 pages with 38,437 links. It's public if you want to look at the output before installing anything: github.com/ckryptickunal/Founder-Book

New ingests (0.3.0) check every quote against the transcript and link it to its timestamp in the video; that vault predates the feature. Re-runs only process new or changed files.

pip install openwiki-cli · github.com/ckryptickunal/OpenWiki (MIT)

Happy to hear how you'd want pages structured differently.

### r/LocalLLaMA
**Title:** OpenWiki: compile YouTube channels and blogs into a Markdown wiki with a local model (Ollama / LM Studio)
**Body:**
Disclosure: I built this. It's an MIT Python CLI that pulls transcripts and articles, then has an LLM write linked wiki pages (sources, people, companies, topics). Set `LLM_PROVIDER=openai` and `OPENAI_BASE_URL=http://localhost:11434/v1` and the LLM step runs entirely on your machine. Downloading transcripts still needs the internet.

Small models return malformed JSON more often; OpenWiki retries and repairs the common cases. I'd like to hear which local models give the cleanest entity extraction for you.

Why a wiki instead of RAG over raw text: on three questions against my corpus, the wiki path read 8,171 tokens vs 65,097 for the raw transcripts behind the same pages. Small sample, and the scripts are in the repo so you can rerun them.

`openwiki search` is offline BM25 with timestamps, no LLM. `openwiki ask` answers with citations and says "Not in your sources." when it can't find one.

github.com/ckryptickunal/OpenWiki

### r/ClaudeAI
**Title:** Give Claude Code a compiled wiki instead of raw transcripts: 8x fewer tokens on my tests
**Body:**
I built OpenWiki (open source, MIT). It compiles YouTube channels, essays and notes into small linked Markdown pages, so Claude opens `topics/doing-things-that-don-t-scale.md` and three source pages instead of 68 raw files.

Measured on my corpus (1,219 videos, 354 essays): 8,171 vs 65,097 tokens for the same three questions. Method and scripts are in the repo. The raw transcripts stay in the folder too, so the agent can check a quote against the source.

Tip: don't point the agent at `index.md` first on a big wiki (mine is 147k tokens). Point it at topic and entity pages, or use `openwiki search`.

pip install openwiki-cli · github.com/ckryptickunal/OpenWiki

### r/Python (only if the Showcase rules allow AI tools that day; otherwise use the daily thread)
**Title:** OpenWiki: a CLI that compiles YouTube transcripts and essays into a linked Markdown wiki
**Body:**
**What My Project Does**
Downloads YouTube captions (single videos, playlists, whole channels, no API key) and web articles, then uses an LLM to write Markdown pages for each source, person, company and topic, cross-linked with [[wikilinks]]. Also `openwiki search` (offline BM25) and `openwiki ask` (answers with citations).

**Target Audience**
People who learn from long-form video and essays and want notes they own. Also anyone feeding a corpus to an agent or a RAG pipeline. It runs on a real 1,573-source corpus (Founder Book) and has an offline test suite.

**Comparison**
Karpathy's LLM Wiki gist describes the pattern; most implementations are agent skills or Obsidian plugins that need an agent session. OpenWiki is a standalone pip CLI that handles bulk YouTube channel/playlist ingestion and essay sites, and works with Gemini, any OpenAI-compatible API, or a local model.

pip install openwiki-cli · github.com/ckryptickunal/OpenWiki

---

## Hacker News (Show HN)

HN's guidelines now ask that Show HN text be written by hand, with no LLM involved, so I haven't drafted it. Fact sheet to write from:
- Title format: `Show HN: OpenWiki – compile YouTube channels and essays into a linked Markdown wiki`
- Link to the GitHub repo, not the site.
- Worth saying in your first comment: why you built it; how quote verification works (quotes are matched against the transcript, and a quote that isn't found is dropped); the 8x measurement and its caveats (three questions, lossy summaries, `index.md` too large to read first); what was hard (YouTube rate limits and IP blocks, malformed JSON from small models).
- Expect "garbage in, garbage out" and "why not just RAG" questions. The raw files stay next to the wiki, and `ask` cites both.

---

## Posting plan
1. Publish `openwiki-cli` 0.3.0 on PyPI and check `pip install openwiki-cli` in a clean environment.
2. Upload the master to YouTube (unlisted is fine) for the Product Hunt gallery.
3. Launch on Product Hunt at 12:01am PT on a Tuesday, Wednesday or Thursday. Post the maker comment immediately.
4. The same morning (US time): the X thread, then LinkedIn. Put the links in the first reply or comment on both.
5. Spread the Reddit posts over 2–3 days, one subreddit per day. Answer every comment.
6. Show HN on a weekday morning US time, written by you.
