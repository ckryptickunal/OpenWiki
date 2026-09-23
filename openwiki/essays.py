"""Essay, article, and local-note extraction.

Default mode is `generic`: any index page whose links point at articles on the
same site. `paulgraham` and `samaltman` are optional site-specific parsers.
"""

from __future__ import annotations

import html
import re
import urllib.request
from collections.abc import Callable
from pathlib import Path
from urllib.parse import urljoin, urlparse

from openwiki import __version__
from openwiki.textfmt import slugify, write_essay_file, write_source_file

USER_AGENT = f"Mozilla/5.0 (compatible; OpenWiki/{__version__}; +https://github.com/ckryptickunal/OpenWiki)"
DEFAULT_MIN_CHARS = 400
SKIP_LINK_EXTENSIONS = (
    ".css", ".js", ".json", ".xml", ".rss", ".atom", ".png", ".jpg", ".jpeg",
    ".gif", ".svg", ".webp", ".ico", ".pdf", ".zip", ".mp3", ".mp4",
)


def fetch_url(url: str, timeout: int = 30) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        return resp.read().decode(charset, errors="replace")


def _strip_tags(value: str) -> str:
    return html.unescape(re.sub(r"(?s)<[^>]+>", " ", value)).strip()


def _main_region(raw: str) -> str:
    """Return the <article> or <main> element when it holds most of the page text."""
    for tag in ("article", "main"):
        blocks = re.findall(rf"(?is)<{tag}\b[^>]*>(.*?)</{tag}>", raw)
        if not blocks:
            continue
        best = max(blocks, key=len)
        if len(_strip_tags(best)) >= 200:
            return best
    return raw


def html_to_text(raw: str) -> str:
    """Dependency-free HTML to plain text, keeping paragraph breaks."""
    raw = re.sub(r"(?s)<!--.*?-->", " ", raw)
    raw = re.sub(r"(?is)<(script|style|head|noscript|svg|template)\b.*?</\1>", " ", raw)
    raw = _main_region(raw)
    raw = re.sub(r"(?is)<(nav|footer|form|aside|header)\b.*?</\1>", " ", raw)
    raw = re.sub(r"(?i)<br\s*/?>", "\n", raw)
    raw = re.sub(r"(?i)</p>", "\n\n", raw)
    raw = re.sub(r"(?i)</(div|h[1-6]|li|tr|blockquote|pre)>", "\n", raw)
    text = re.sub(r"(?s)<[^>]+>", " ", raw)
    text = html.unescape(text)
    text = re.sub(r"[ \t\u00a0]+", " ", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _meta_content(raw: str, *names: str) -> str | None:
    for name in names:
        for pattern in (
            rf'<meta[^>]+(?:property|name)=["\']{re.escape(name)}["\'][^>]*content=["\']([^"\']+)["\']',
            rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]*(?:property|name)=["\']{re.escape(name)}["\']',
        ):
            match = re.search(pattern, raw, re.I)
            if match:
                return html.unescape(match.group(1)).strip()
    return None


def extract_title(raw: str) -> str | None:
    """Best-effort page title: og:title, then <title>, then the first <h1>."""
    title = _meta_content(raw, "og:title", "twitter:title")
    if not title:
        match = re.search(r"(?is)<title[^>]*>(.*?)</title>", raw)
        title = _strip_tags(match.group(1)) if match else None
    if not title:
        match = re.search(r"(?is)<h1[^>]*>(.*?)</h1>", raw)
        title = _strip_tags(match.group(1)) if match else None
    return re.sub(r"\s+", " ", title).strip() if title else None


def extract_published(raw: str) -> str | None:
    """Best-effort publish date (YYYY-MM-DD) from meta tags, JSON-LD, or <time datetime>."""
    candidates = [_meta_content(raw, "article:published_time", "datePublished", "date", "pubdate")]
    match = re.search(r'"datePublished"\s*:\s*"([^"]+)"', raw)
    candidates.append(match.group(1) if match else None)
    match = re.search(r'<time[^>]+datetime=["\']([^"\']+)["\']', raw, re.I)
    candidates.append(match.group(1) if match else None)
    for value in candidates:
        if value:
            date = re.match(r"\d{4}-\d{2}-\d{2}", value.strip())
            if date:
                return date.group(0)
    return None


def _same_site(url: str, base_url: str) -> bool:
    target, base = urlparse(url), urlparse(base_url)
    if target.scheme not in ("http", "https"):
        return False
    if target.netloc.removeprefix("www.") != base.netloc.removeprefix("www."):
        return False
    return target.path.startswith(base.path.rstrip("/"))


def parse_generic_index(index_html: str, base_url: str, index_url: str | None = None) -> list[dict]:
    """Every same-site link under `base_url` whose text looks like a title (5+ chars)."""
    essays = []
    page_url = index_url or base_url
    skip = {page_url.rstrip("/"), base_url.rstrip("/")}
    seen: set[str] = set()
    for href, title in re.findall(
        r'<a\s[^>]*?href=["\']([^"\'#]+)["\'][^>]*>(.*?)</a>', index_html, re.I | re.S
    ):
        title = re.sub(r"\s+", " ", _strip_tags(title))
        if len(title) < 5:
            continue
        url = urljoin(page_url, href.strip())
        if not _same_site(url, base_url) or url.rstrip("/") in skip or url in seen:
            continue
        if urlparse(url).path.lower().endswith(SKIP_LINK_EXTENSIONS):
            continue
        seen.add(url)
        essays.append({"title": title, "url": url})
    return essays


def parse_paulgraham_index(index_html: str, base_url: str, index_url: str | None = None) -> list[dict]:
    essays = []
    seen: set[str] = set()
    for href, title in re.findall(
        r'<a\s+href="([\w./-]+\.html)"[^>]*>(.*?)</a>', index_html, re.I | re.S
    ):
        if href.startswith(("index", "rss", "articles")):
            continue
        title = re.sub(r"<[^>]+>", "", title).strip()
        if not title or href in seen:
            continue
        seen.add(href)
        url = href if href.startswith("http") else base_url.rstrip("/") + "/" + href.lstrip("/")
        essays.append({"title": html.unescape(title), "url": url})
    return essays


def parse_samaltman_index(index_html: str, base_url: str, index_url: str | None = None) -> list[dict]:
    essays = []
    seen: set[str] = set()
    for href, title in re.findall(
        r'<a\s+href="(https?://blog\.samaltman\.com/[^"#]+)"[^>]*>(.*?)</a>',
        index_html,
        re.I | re.S,
    ):
        if href.rstrip("/").endswith(("archive", "blog.samaltman.com")):
            continue
        title = re.sub(r"<[^>]+>", "", title).strip()
        if not title or len(title) < 3 or href in seen:
            continue
        seen.add(href)
        essays.append({"title": html.unescape(title), "url": href})
    return essays


INDEX_PARSERS: dict[str, Callable[..., list[dict]]] = {
    "generic": parse_generic_index,
    "paulgraham": parse_paulgraham_index,
    "samaltman": parse_samaltman_index,
}


def parse_index(index_html: str, source: dict) -> list[dict]:
    kind = source.get("kind", "generic")
    if kind not in INDEX_PARSERS:
        raise ValueError(f"Unknown essay kind {kind!r}. Use one of: {', '.join(INDEX_PARSERS)}")
    index_url = source.get("index_url", "")
    base = source.get("base_url") or index_url
    return INDEX_PARSERS[kind](index_html, base, index_url)


def essay_id(title: str, prefix: str) -> str:
    return f"{prefix}-{slugify(title)}"


def discover_new_from_html(source: dict, index_html: str, folder: Path) -> list[dict]:
    """Return index entries that do not yet have a .txt file on disk."""
    folder.mkdir(parents=True, exist_ok=True)
    prefix = source.get("id_prefix", "essay")
    new = []
    for essay in parse_index(index_html, source):
        source_id = essay_id(essay["title"], prefix)
        if (folder / f"{source_id}.txt").exists():
            continue
        essay = dict(essay)
        essay["video_id"] = source_id
        new.append(essay)
    return new


def write_article_from_html(
    html_text: str,
    *,
    folder: Path,
    title: str,
    url: str,
    channel: str,
    prefix: str = "essay",
    published: str | None = None,
    min_chars: int = DEFAULT_MIN_CHARS,
) -> Path | None:
    text = html_to_text(html_text)
    if len(text) < min_chars:
        return None
    source_id = essay_id(title, prefix)
    filepath = folder / f"{source_id}.txt"
    published = published or extract_published(html_text) or "Unknown"
    write_essay_file(filepath, source_id, title, published, channel, url, text)
    return filepath


def fetch_one_essay(
    source: dict,
    essay: dict,
    folder: Path,
    *,
    fetch_url_fn: Callable[[str], str] = fetch_url,
    min_chars: int = DEFAULT_MIN_CHARS,
) -> bool:
    page = fetch_url_fn(essay["url"])
    path = write_article_from_html(
        page,
        folder=folder,
        title=essay["title"],
        url=essay["url"],
        channel=f"{source.get('name', 'Essays')} (web)",
        prefix=source.get("id_prefix", "essay"),
        min_chars=min_chars,
    )
    return path is not None


def fetch_source(
    source: dict,
    root: Path,
    *,
    dry_run: bool = False,
    fetch_url_fn: Callable[[str], str] = fetch_url,
    min_chars: int = DEFAULT_MIN_CHARS,
    limit: int | None = None,
) -> tuple[int, int, list[dict]]:
    folder = root / source["folder"]
    folder.mkdir(parents=True, exist_ok=True)
    index_html = fetch_url_fn(source["index_url"])
    new = discover_new_from_html(source, index_html, folder)
    if limit is not None:
        new = new[:limit]
    if dry_run:
        return 0, 0, new

    created = failed = 0
    for essay in new:
        try:
            if fetch_one_essay(
                source, essay, folder, fetch_url_fn=fetch_url_fn, min_chars=min_chars
            ):
                created += 1
            else:
                failed += 1
        except Exception:
            failed += 1
    return created, failed, new


def import_text_file(
    path: Path,
    folder: Path,
    *,
    title: str | None = None,
    url: str = "",
    prefix: str = "note",
    channel: str | None = None,
    published: str = "Unknown",
) -> Path:
    """Wrap a local .txt/.md/.html file in the source header so it can be ingested."""
    raw = Path(path).read_text(encoding="utf-8", errors="replace")
    is_html = Path(path).suffix.lower() in {".html", ".htm"}
    body = html_to_text(raw) if is_html else raw.strip()
    if not title:
        heading = re.search(r"^#\s+(.+)$", raw, re.M) if not is_html else None
        title = (extract_title(raw) if is_html else heading.group(1).strip() if heading else None) or Path(path).stem
    source_id = essay_id(title, prefix)
    extra = {"Source": url or str(Path(path).resolve())}
    return write_source_file(
        folder / f"{source_id}.txt",
        title=title,
        source_id=source_id,
        body=body,
        channel=channel or folder.name,
        published=published,
        extra=extra,
    )
