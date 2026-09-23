"""Render the static website into site/.

    python scripts/build_site.py

Pages share one head, footer, and stylesheet. All links and assets are
relative, so the output works at any base path (/openwiki/, /OpenWiki/, /).
SITE_URL is only used for canonical/Open Graph/sitemap URLs.
"""

from __future__ import annotations

import html
import json
from dataclasses import dataclass, field
from pathlib import Path

SITE_URL = "https://openwiki-delta.vercel.app/openwiki/"
REPO = "https://github.com/ckryptickunal/OpenWiki"
SPONSOR = "https://github.com/sponsors/ckryptickunal"
INSTALL = 'pip install "git+https://github.com/ckryptickunal/OpenWiki.git"'
UPDATED = "2026-09-24"
OUT = Path(__file__).resolve().parents[1] / "site"

FONTS = (
    "https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@1,9..144,400..600"
    "&family=Inter:wght@400..600&family=Playwrite+US+Trad&display=swap"
)

ICON_BACK = '<svg viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M10 3 5 8l5 5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def code(*lines: str) -> str:
    """A code card. Lines starting with '#' are comments; others are copyable commands."""
    rendered = []
    for line in lines:
        if line.startswith("#"):
            rendered.append(f'<span class="c">{esc(line)}</span>')
        else:
            rendered.append(f'<span class="p">$ </span><span class="cmd">{esc(line)}</span>')
    return f'<div class="code"><pre><code>{chr(10).join(rendered)}</code></pre></div>'


@dataclass
class Page:
    slug: str                 # "" for home
    title: str                # <title>
    description: str
    name: str                 # short name used in rows and titles
    kicker: str = ""
    image: str = ""
    image_alt: str = ""
    meta: str = ""            # right-hand label on the home row
    links: list[tuple[str, str]] = field(default_factory=list)
    body: str = ""
    tilt: str = "0deg"

    @property
    def url(self) -> str:
        return SITE_URL + (f"{self.slug}/" if self.slug else "")


PAGES: list[Page] = [
    Page(
        slug="youtube",
        name="YouTube",
        title="YouTube Transcripts to Markdown Notes | OpenWiki",
        description="Download YouTube transcripts from a video, playlist or whole channel as clean text, then turn them into linked Markdown notes. Free, open source, non-English captions supported.",
        kicker="Videos, playlists and whole channels",
        image="img/youtube.jpg",
        image_alt="A small cream vintage television on a wooden desk, glowing with a blurred lecture.",
        meta="videos · playlists · channels",
        tilt="-.6deg",
        links=[("docs: adding sources", REPO + "/blob/main/docs/ADDING_SOURCES.md"), ("source code", REPO + "/blob/main/openwiki/youtube.py")],
        body=f"""
<p>Talks, lectures and interviews are some of the best material on the internet, and some of the hardest to search. OpenWiki downloads their captions as plain text so you can read, grep and build on them.</p>
<h3>One video, no key needed</h3>
<p>Paste a link. The title and channel come from YouTube's public oEmbed endpoint, so you don't need an API key for single videos or lists of links.</p>
{code("openwiki youtube https://www.youtube.com/watch?v=jNQXAC9IVRw --folder Talks")}
<p>That writes <code>Talks/jNQXAC9IVRw.txt</code>: a short header (title, channel, language) followed by the full transcript.</p>
<h3>Playlists and channels</h3>
<p>With a free <a class="link" href="https://console.cloud.google.com/apis/library/youtube.googleapis.com">YouTube Data API key</a>, OpenWiki lists every upload on a channel, newest first, or every video in a playlist, and only downloads what you don't have yet.</p>
{code("openwiki youtube --channel @ycombinator --limit 20", "openwiki youtube --playlist https://www.youtube.com/playlist?list=PL... --folder Course")}
<h3>Any language</h3>
<p>Pass <code>--lang hi,en</code> to prefer certain caption languages. If none match, OpenWiki uses whatever track the video has instead of skipping it. Videos with no captions at all are remembered and never retried; rate limits are retried on the next run.</p>
<h3>Next</h3>
<p>Turn the transcripts into wiki pages with <code>openwiki ingest --all</code>. See <a class="link" href="../wiki/">how the wiki is built</a>.</p>
""",
    ),
    Page(
        slug="blogs",
        name="Blogs & essays",
        title="Save Blog Posts & Essays as Markdown | OpenWiki",
        description="Save any article or a whole blog as clean text with its title and date, then turn it into linked Markdown notes. Works with any site, no API key needed.",
        kicker="Any article, or every post on a blog",
        image="img/essays.jpg",
        image_alt="A stack of printed essays with a brass clip, a pencil and reading glasses.",
        meta="any site",
        tilt=".5deg",
        links=[("docs: essay sites", REPO + "/blob/main/docs/ADDING_SOURCES.md#essay--article-site"), ("source code", REPO + "/blob/main/openwiki/essays.py")],
        body=f"""
<p>Point OpenWiki at an article and it keeps only the part worth reading. It finds the main <code>&lt;article&gt;</code>, drops navigation and footers, and detects the title and publish date.</p>
{code("openwiki essay --url https://www.paulgraham.com/greatwork.html --folder Essays --id-prefix pg")}
<h3>Follow a whole blog</h3>
<p>Add the blog's index page to <code>sources.json</code>. Each time you run <code>openwiki sync</code>, only new posts are downloaded.</p>
<div class="code"><pre><code><span class="c">// sources.json</span>
{esc('{ "essay_sources": [{')}
{esc('  "name": "Some Blog", "kind": "generic",')}
{esc('  "index_url": "https://example.com/blog/",')}
{esc('  "base_url": "https://example.com/blog",')}
{esc('  "folder": "Some Blog", "id_prefix": "sb"')}
{esc('}] }')}</code></pre></div>
<p>The generic parser follows same-site links under <code>base_url</code> and ignores feeds, images and PDFs. There are dedicated parsers for Paul Graham and Sam Altman, and adding one for another site takes a few lines.</p>
<h3>Next</h3>
<p>Mix essays with <a class="link" href="../youtube/">video transcripts</a> and <a class="link" href="../notes/">your own notes</a> in the same wiki.</p>
""",
    ),
    Page(
        slug="notes",
        name="Your notes",
        title="Turn Your Notes into a Linked Markdown Wiki | OpenWiki",
        description="Add your own Markdown, text or HTML notes to OpenWiki and get a linked wiki of the people, companies and topics they mention.",
        kicker="Markdown, text and HTML files",
        image="img/notes.jpg",
        image_alt="An open notebook of handwritten notes with a fountain pen and index cards.",
        meta=".md · .txt · .html",
        tilt="-.4deg",
        links=[("docs: local notes", REPO + "/blob/main/docs/ADDING_SOURCES.md#local-notes-and-exports")],
        body=f"""
<p>Meeting notes, research logs, exported highlights and old blog drafts belong in the same knowledge base as the videos and essays that inspired them.</p>
{code("openwiki text meeting-notes.md research/*.txt --folder Notes")}
<p>The title comes from the first <code># heading</code> in Markdown, the page title in HTML, or the file name. Each file gets the same header as every other source, so ingest treats them all alike.</p>
<h3>Next</h3>
<p>Run <code>openwiki ingest --all</code> and your notes start linking to <a class="link" href="../wiki/">the same people and topics</a> as everything else.</p>
""",
    ),
    Page(
        slug="wiki",
        name="Linked pages",
        title="An LLM Wiki of Sources, People & Topics | OpenWiki",
        description="OpenWiki uses an LLM to write a page for every source, person, company and topic, all cross-linked with backlinks. Plain Markdown you own, ready for RAG.",
        kicker="Sources, people, companies and topics",
        image="img/wiki.jpg",
        image_alt="A wooden card catalogue with index cards linked together by red thread.",
        meta="sources · people · topics",
        tilt=".6deg",
        links=[("docs: architecture", REPO + "/blob/main/docs/ARCHITECTURE.md")],
        body=f"""
<p>Every source becomes a page with a summary, key ideas, notable claims and quotes. The people, companies, products and topics it mentions get pages of their own, and each of those keeps a list of every source that mentions it.</p>
{code("openwiki ingest --all", "openwiki lint --fix-index")}
<p>The more you add, the denser the web gets. A founder who appears in ten talks ends up with one page linking to all ten.</p>
<h3>What a folder looks like</h3>
<div class="code"><pre><code>my-wiki/
  Talks/jNQXAC9IVRw.txt          <span class="c"># raw transcript</span>
  wiki/index.md                  <span class="c"># catalog of every page</span>
  wiki/sources/jNQXAC9IVRw-me-at-the-zoo.md
  wiki/entities/jawed-karim.md
  wiki/topics/internet-history.md</code></pre></div>
<h3>Incremental and safe to re-run</h3>
<p>Unchanged files are skipped, failures are listed in <code>wiki/ingest_failures.json</code> and retried next time, and <code>openwiki lint</code> reports broken links, missing frontmatter and orphan pages. The raw text files stay the source of truth, so you can always rebuild the wiki.</p>
""",
    ),
    Page(
        slug="obsidian",
        name="Obsidian vault",
        title="Build an Obsidian Vault from YouTube & Blogs | OpenWiki",
        description="Open OpenWiki's output as an Obsidian vault: YAML frontmatter, [[wikilinks]], backlinks and a graph view built from YouTube videos, blogs and your notes.",
        kicker="Frontmatter, [[wikilinks]] and backlinks",
        image="img/obsidian.jpg",
        image_alt="A polished black obsidian stone on linen next to index cards tied with twine.",
        meta="[[wikilinks]]",
        tilt="-.5deg",
        links=[("docs: page format", REPO + "#what-you-get")],
        body="""
<p>Open the <code>wiki/</code> folder as a vault and it just works. Every page has YAML frontmatter (type, title, url, channel, published date, tags) and links with <code>[[folder/page|Title]]</code>, so backlinks, tags and the graph view light up straight away.</p>
<p>Because it is plain Markdown on disk, the same folder works in VS Code, iA Writer, Logseq or a static-site generator, and it makes clean input for a RAG pipeline or a long-context model.</p>
<h3>Names in any script</h3>
<p>Page names keep non-Latin scripts, so a person named in Hindi or Chinese gets their own page instead of colliding with everyone else.</p>
""",
    ),
    Page(
        slug="providers",
        name="Any LLM",
        title="Use Gemini, OpenAI or Ollama Offline | OpenWiki",
        description="OpenWiki works with Google Gemini, OpenAI, OpenRouter, Groq, or a local model through Ollama or LM Studio for fully offline use.",
        kicker="Gemini, OpenAI-compatible, or fully offline",
        image="img/providers.jpg",
        image_alt="A beige vintage computer terminal with a soft green glow and a brass desk key.",
        meta="gemini · openai · ollama",
        tilt=".4deg",
        links=[("docs: LLM providers", REPO + "#llm-providers")],
        body="""
<p>The LLM reads each source and writes the summary, claims and entity and topic lists. Pick whichever fits your budget and privacy needs; put the settings in <code>.env</code> in your workspace.</p>
<h3>Google Gemini</h3>
<div class="code"><pre><code>GEMINI_API_KEY=...
<span class="c"># optional, this is the default:</span>
GEMINI_MODEL=gemini-3.1-flash-lite</code></pre></div>
<h3>OpenAI, OpenRouter, Groq</h3>
<div class="code"><pre><code>LLM_PROVIDER=openai
OPENAI_API_KEY=...
OPENAI_MODEL=&lt;model id&gt;
OPENAI_BASE_URL=https://openrouter.ai/api/v1   <span class="c"># or Groq, or leave unset for OpenAI</span></code></pre></div>
<h3>Ollama or LM Studio, fully offline</h3>
<div class="code"><pre><code>LLM_PROVIDER=openai
OPENAI_BASE_URL=http://localhost:11434/v1   <span class="c"># LM Studio: :1234/v1</span>
OPENAI_MODEL=llama3.1</code></pre></div>
<p>No key is needed for a local server, and nothing leaves your machine except the caption and article downloads. Larger models extract entities and topics more reliably.</p>
<h3>No model at all</h3>
<p>Pass <code>--analysis-file</code> with precomputed JSON and OpenWiki builds the pages without calling any LLM.</p>
""",
    ),
]

SECTIONS = [
    ("sources", ["youtube", "blogs", "notes"]),
    ("the wiki", ["wiki", "obsidian", "providers"]),
]

FAQ = [
    ("How do I download the transcript of a YouTube video as text?",
     "Run openwiki youtube <url> --folder Talks. It writes a .txt file with the title, channel, language and full transcript. No API key is needed."),
    ("How do I turn a whole YouTube channel or playlist into notes?",
     "Set a free YOUTUBE_API_KEY, run openwiki youtube --channel @handle or --playlist <url>, then openwiki ingest --all to build the wiki pages."),
    ("Does it work with non-English videos?",
     "Yes. Use --lang to prefer languages; if none match, OpenWiki uses whatever caption track exists. Page names keep non-Latin scripts."),
    ("Can I use it with Obsidian?",
     "Yes. Open the wiki folder as a vault. Pages use YAML frontmatter and [[wikilinks]], so backlinks and the graph view work."),
    ("Can I run it without sending data to the cloud?",
     "Yes. Point it at Ollama or LM Studio. Only the caption and article downloads touch the internet."),
    ("What does it cost?",
     "OpenWiki is free and MIT-licensed. You only pay for LLM calls if your provider charges; a local model costs nothing."),
]

PILE_VARS = [
    "--tilt:-7deg;--tx:-2px;--ty:-2px;--fan-tilt:-12deg;--fan-tx:-7px;--fan-ty:-3px",
    "--tilt:5deg;--tx:1px;--ty:-1px;--fan-tilt:9deg;--fan-tx:6px;--fan-ty:-4px",
    "--tilt:-4deg;--tx:-1px;--ty:1px;--fan-tilt:-10deg;--fan-tx:-6px;--fan-ty:2px",
]
TOP_VARS = ["--rot:-1.5deg;--rot-from:-9deg;--hover-tilt:3deg", "--rot:1deg;--rot-from:8deg;--hover-tilt:-3deg", "--rot:-.5deg;--rot-from:-7deg;--hover-tilt:2.5deg"]


def head(page_title: str, description: str, url: str, depth: int, jsonld: list[dict], image: str = "img/og.jpg") -> str:
    prefix = "../" * depth
    ld = "\n".join(f'<script type="application/ld+json">{json.dumps(item, ensure_ascii=False)}</script>' for item in jsonld)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(page_title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#faf6f2">
<meta name="author" content="Kunal">
<meta property="og:type" content="website">
<meta property="og:site_name" content="OpenWiki">
<meta property="og:title" content="{esc(page_title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE_URL}{image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:creator" content="@kunalbairwa232">
<meta name="twitter:title" content="{esc(page_title)}">
<meta name="twitter:description" content="{esc(description)}">
<meta name="twitter:image" content="{SITE_URL}{image}">
<link rel="icon" href="{prefix}favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="{prefix}assets/site.css">
<script>document.documentElement.classList.add("js")</script>
{ld}
</head>
"""


def footer(depth: int) -> str:
    prefix = "../" * depth
    return f"""<footer class="foot stagger" style="--s:12">
<a class="link" href="{REPO}">github</a>
<a class="link" href="{SPONSOR}">sponsor</a>
<a class="link" href="{REPO}/issues">issues</a>
<a class="link" href="{REPO}/discussions">discussions</a>
<a class="link" href="https://github.com/ckryptickunal/Founder-Book">founder book</a>
<a class="link" href="{prefix}sitemap.xml">sitemap</a>
<p class="foot-note">MIT licensed. Built by <a class="link" href="https://github.com/ckryptickunal">Kunal</a>.</p>
</footer>"""


def pile(index: int, image: str, alt: str) -> str:
    back = PILE_VARS[index % len(PILE_VARS)]
    top = TOP_VARS[index % len(TOP_VARS)]
    return f"""<div class="pile" aria-hidden="true">
<div class="pile-card" style="{back}"><div class="polaroid polaroid--blank"></div></div>
<div class="pile-card pile-card--top"><div class="polaroid" style="{top}"><img src="{image.replace("img/", "img/thumbs/")}" alt="" width="57" height="34" decoding="async"></div></div>
</div>"""


def home() -> str:
    by_slug = {p.slug: p for p in PAGES}
    stagger = 1
    sections = []
    index = 0
    for label, slugs in SECTIONS:
        rows = []
        sections.append(f'<section class="section" aria-labelledby="h-{label.replace(" ", "-")}">')
        sections.append(f'<h2 class="h2 stagger" id="h-{label.replace(" ", "-")}" style="--s:{stagger}">{label}</h2>')
        stagger += 1
        for slug in slugs:
            page = by_slug[slug]
            rows.append(
                f'<a class="row divider stagger" style="--s:{stagger}" href="{slug}/">'
                f'{pile(index, page.image, page.image_alt)}'
                f'<span class="row-title">{esc(page.name)}</span>'
                f'<span class="row-meta">{esc(page.meta)}</span></a>'
            )
            stagger += 1
            index += 1
        sections.extend(rows)
        sections.append("</section>")

    faq_items = "\n".join(
        f'<details class="faq divider"><summary><h3>{esc(q)}</h3><span class="faq-sign" aria-hidden="true"></span></summary>'
        f'<div class="faq-answer"><p>{esc(a)}</p></div></details>'
        for q, a in FAQ
    )
    jsonld = [
        {
            "@context": "https://schema.org",
            "@type": "SoftwareSourceCode",
            "name": "OpenWiki",
            "description": PAGES_HOME_DESC,
            "codeRepository": REPO,
            "programmingLanguage": "Python",
            "runtimePlatform": "Python 3.10+",
            "license": "https://opensource.org/licenses/MIT",
            "url": SITE_URL,
            "author": {"@type": "Person", "name": "Kunal", "url": "https://github.com/ckryptickunal"},
            "keywords": "YouTube transcript, knowledge base, LLM wiki, Obsidian, Markdown, second brain, RAG",
        },
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ
            ],
        },
    ]
    return head(
        "OpenWiki | Turn YouTube & Blogs into a Markdown Knowledge Base",
        PAGES_HOME_DESC,
        SITE_URL,
        0,
        jsonld,
    ) + f"""<body>
<a class="skip" href="#main">Skip to content</a>
<main class="ow" id="main">
<div class="page">
<header class="head">
<h1 class="stagger" style="--s:0;margin:0"><a href="./" class="wordmark" aria-label="OpenWiki home">openwiki<span class="wordmark-veil"></span></a><span class="sr-only">: turn YouTube videos, blogs and notes into a Markdown knowledge base</span></h1>
<p class="body3 stagger" style="--s:0">OpenWiki turns YouTube videos, blogs and your own notes into a linked Markdown wiki you keep. It's an open-source command-line tool: it downloads transcripts and articles, then an LLM writes a page for every source, person, company and topic, all cross-linked and ready for <a class="link" href="obsidian/">Obsidian</a>.</p>
<p class="body3 secondary stagger" style="--s:1"><a class="link" href="{REPO}">source on github</a>, <a class="link" href="#start">get started</a>, or <a class="link" href="{SPONSOR}">sponsor the project</a>.</p>
</header>
{chr(10).join(sections)}
<section class="section" id="start" aria-labelledby="h-start">
<h2 class="h2 stagger" id="h-start" style="--s:{stagger}">get started</h2>
<div class="stagger" style="--s:{stagger + 1}">
<p class="body3">Python 3.10 or newer. Grab a video and an essay without any keys, then add an LLM to build the wiki.</p>
{code(INSTALL, "openwiki init --root my-wiki && cd my-wiki", "openwiki youtube https://youtu.be/jNQXAC9IVRw --folder Talks", "openwiki ingest --all")}
<ul class="tags" aria-label="Highlights"><li>free &amp; MIT</li><li>no key for single videos</li><li>runs offline with Ollama</li><li>incremental</li></ul>
</div>
</section>
<section class="section" aria-labelledby="h-faq">
<h2 class="h2 stagger" id="h-faq" style="--s:{stagger + 2}">questions</h2>
<div class="stagger" style="--s:{stagger + 3}">
{faq_items}
</div>
</section>
{footer(0)}
</div>
</main>
<script src="assets/site.js" defer></script>
</body>
</html>
"""


PAGES_HOME_DESC = (
    "Open-source Python CLI that turns YouTube videos, playlists, channels, blogs and notes into a "
    "linked, Obsidian-compatible Markdown wiki. Works with Gemini, OpenAI or offline with Ollama."
)


def detail(page: Page, next_page: Page) -> str:
    links = "\n".join(f'<li><a class="link" href="{href}">{esc(label)}</a></li>' for label, href in page.links)
    links += f'\n<li><a class="link" href="{REPO}">OpenWiki on GitHub</a></li>'
    jsonld = [
        {
            "@context": "https://schema.org",
            "@type": "TechArticle",
            "headline": page.title.split(" | ")[0],
            "description": page.description,
            "url": page.url,
            "image": SITE_URL + page.image,
            "dateModified": UPDATED,
            "author": {"@type": "Person", "name": "Kunal", "url": "https://github.com/ckryptickunal"},
            "about": {"@type": "SoftwareSourceCode", "name": "OpenWiki", "codeRepository": REPO},
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "OpenWiki", "item": SITE_URL},
                {"@type": "ListItem", "position": 2, "name": page.name, "item": page.url},
            ],
        },
    ]
    return head(page.title, page.description, page.url, 1, jsonld, image=page.image) + f"""<body>
<a class="skip" href="#main">Skip to content</a>
<a class="back" href="../" aria-label="Back to OpenWiki home">{ICON_BACK}</a>
<main class="ow" id="main">
<div class="page entry">
<p class="rise" style="--s:0;margin:0 0 20px"><a href="../" class="wordmark wordmark--small" aria-label="OpenWiki home">openwiki</a></p>
<figure class="hero rise" style="--s:1;--tilt:{page.tilt}"><img src="../{page.image}" alt="{esc(page.image_alt)}" width="1500" height="1000" fetchpriority="high"></figure>
<article>
<h1 class="entry-title rise" style="--s:2">{esc(page.name)}</h1>
<p class="entry-kicker rise" style="--s:3">{esc(page.kicker)}</p>
<ul class="entry-links rise" style="--s:4">
{links}
</ul>
<div class="prose rise" style="--s:5">
{page.body.strip()}
</div>
</article>
<a class="next divider rise" style="--s:6" href="../{next_page.slug}/"><span class="secondary">next</span><span>{esc(next_page.name)} &rarr;</span></a>
{footer(1)}
</div>
</main>
<script src="../assets/site.js" defer></script>
</body>
</html>
"""


def not_found() -> str:
    # Served from any path, so assets use the absolute Vercel base path with a relative fallback.
    return head("Page not found | OpenWiki", "This page does not exist.", SITE_URL + "404.html", 0, []).replace(
        'href="assets/site.css"', 'href="/openwiki/assets/site.css"'
    ).replace('<link rel="canonical"', '<meta name="robots" content="noindex">\n<link rel="canonical"') + f"""<body>
<main class="ow" id="main">
<div class="page">
<header class="head">
<p class="stagger" style="--s:0;margin:0"><a href="/openwiki/" class="wordmark">openwiki<span class="wordmark-veil"></span></a></p>
<h1 class="h2 stagger" style="--s:1">nothing filed here</h1>
<p class="body3 stagger" style="--s:2">This page isn't in the index. Try the <a class="link" href="/openwiki/">home page</a> or the <a class="link" href="{REPO}">project on GitHub</a>.</p>
</header>
</div>
</main>
</body>
</html>
"""


def sitemap() -> str:
    urls = [SITE_URL] + [p.url for p in PAGES]
    entries = "\n".join(f"  <url><loc>{u}</loc><lastmod>{UPDATED}</lastmod></url>" for u in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{entries}\n</urlset>\n'


FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#faf6f2"/><rect x="10" y="14" width="44" height="36" rx="2" fill="#fff" stroke="#e5dbd7" stroke-width="2" transform="rotate(-6 32 32)"/><text x="32" y="42" text-anchor="middle" font-family="Georgia, serif" font-style="italic" font-weight="700" font-size="30" fill="#432818">w</text></svg>
"""


def thumbnails() -> None:
    """Small copies for the 57x34 row polaroids (2x for sharp screens)."""
    from PIL import Image

    (OUT / "img/thumbs").mkdir(parents=True, exist_ok=True)
    for page in PAGES:
        image = Image.open(OUT / page.image).convert("RGB")
        image.thumbnail((180, 180))
        image.save(OUT / page.image.replace("img/", "img/thumbs/"), "JPEG", quality=80, optimize=True)


def main() -> None:
    thumbnails()
    (OUT / "index.html").write_text(home(), encoding="utf-8")
    for i, page in enumerate(PAGES):
        folder = OUT / page.slug
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "index.html").write_text(detail(page, PAGES[(i + 1) % len(PAGES)]), encoding="utf-8")
    (OUT / "404.html").write_text(not_found(), encoding="utf-8")
    (OUT / "sitemap.xml").write_text(sitemap(), encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}sitemap.xml\n", encoding="utf-8")
    (OUT / "favicon.svg").write_text(FAVICON, encoding="utf-8")
    print(f"Built {1 + len(PAGES)} pages into {OUT}")


if __name__ == "__main__":
    main()
