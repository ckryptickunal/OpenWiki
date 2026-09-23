"""Essay and article extraction.

Maps to Founder Book `fetch_new_essays.py` + `fetch_essays.write_essay_file`.
Default mode is generic (any index page). Site-specific parsers are optional kinds.
"""

from __future__ import annotations

import html
import re
import urllib.request
from pathlib import Path
from typing import Callable

from wikiblocks.textfmt import slugify, write_essay_file

USER_AGENT = "Mozilla/5.0 (compatible; WikiBlocks/0.1; +https://github.com/ckryptickunal/Wiki-Blocks)"
DEFAULT_MIN_CHARS = 400


def fetch_url(url: str, timeout: int = 30) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        return resp.read().decode(charset, errors="replace")


def html_to_text(raw: str) -> str:
    """Dependency-free HTML → text. Same approach as Founder Book fetch_new_essays."""
    raw = re.sub(r"(?is)<(script|style|head|nav|footer|form).*?</\1>", " ", raw)
    raw = re.sub(r"(?i)<br\s*/?>", "\n", raw)
    raw = re.sub(r"(?i)</p>", "\n\n", raw)
    raw = re.sub(r"(?i)</(div|h[1-6]|li|tr)>", "\n", raw)
    text = re.sub(r"(?s)<[^>]+>", " ", raw)
    text = html.unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def parse_generic_index(index_html: str, base_url: str) -> list[dict]:
    essays = []
    seen: set[str] = set()
    base = base_url.rstrip("/")
    for href, title in re.findall(
        r'<a\s+href="([^"#]+)"[^>]*>(.*?)</a>', index_html, re.I | re.S
    ):
        title = re.sub(r"<[^>]+>", "", title).strip()
        if not title or len(title) < 5:
            continue
        url = href if href.startswith("http") else base + "/" + href.lstrip("/")
        if base not in url or url in seen:
            continue
        seen.add(url)
        essays.append({"title": html.unescape(title), "url": url})
    return essays


def parse_paulgraham_index(index_html: str, base_url: str) -> list[dict]:
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


def parse_samaltman_index(index_html: str, base_url: str) -> list[dict]:
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


INDEX_PARSERS: dict[str, Callable[[str, str], list[dict]]] = {
    "generic": parse_generic_index,
    "paulgraham": parse_paulgraham_index,
    "samaltman": parse_samaltman_index,
}


def parse_index(index_html: str, source: dict) -> list[dict]:
    kind = source.get("kind", "generic")
    parser = INDEX_PARSERS.get(kind, parse_generic_index)
    base = source.get("base_url", source.get("index_url", ""))
    return parser(index_html, base)


def essay_id(title: str, prefix: str) -> str:
    return f"{prefix}-{slugify(title)}"


def discover_new_from_html(source: dict, index_html: str, folder: Path) -> list[dict]:
    """Return index entries that do not yet have a .txt file on disk."""
    folder.mkdir(parents=True, exist_ok=True)
    prefix = source.get("id_prefix", "essay")
    listed = parse_index(index_html, source)
    new = []
    for essay in listed:
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
    published: str = "Unknown",
    min_chars: int = DEFAULT_MIN_CHARS,
) -> Path | None:
    text = html_to_text(html_text)
    if len(text) < min_chars:
        return None
    source_id = essay_id(title, prefix)
    filepath = folder / f"{source_id}.txt"
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
) -> tuple[int, int, list[dict]]:
    folder = root / source["folder"]
    folder.mkdir(parents=True, exist_ok=True)
    index_html = fetch_url_fn(source["index_url"])
    new = discover_new_from_html(source, index_html, folder)
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
