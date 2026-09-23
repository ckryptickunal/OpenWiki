from __future__ import annotations

from pathlib import Path

from openwiki.essays import (
    extract_published,
    extract_title,
    html_to_text,
    import_text_file,
    parse_generic_index,
)
from openwiki.textfmt import parse_source_file


def test_generic_index_resolves_relative_links_against_index_url():
    html = """
    <a href="posts/first-post">First post title</a>
    <a href='../about'>About this blog</a>
    <a href="https://www.example.com/blog/posts/second">Second post title</a>
    <a href="/blog/feed.xml">RSS feed link</a>
    <a href="https://example.com/blog/">Blog home page</a>
    """
    listed = parse_generic_index(html, "https://example.com/blog", "https://example.com/blog/")
    urls = [item["url"] for item in listed]
    assert urls == [
        "https://example.com/blog/posts/first-post",
        "https://www.example.com/blog/posts/second",
    ]


def test_extract_title_and_date():
    raw = """<html><head><title>Fallback | Site</title>
    <meta property="og:title" content="Why indexes beat memory">
    <meta property="article:published_time" content="2025-03-04T10:00:00Z"></head>
    <body><h1>Heading</h1></body></html>"""
    assert extract_title(raw) == "Why indexes beat memory"
    assert extract_published(raw) == "2025-03-04"
    assert extract_title("<h1>Only <em>a</em> heading</h1>") == "Only a heading"
    assert extract_published('<time datetime="2024-12-01">Dec 1</time>') == "2024-12-01"


def test_html_to_text_prefers_article_region():
    body = "Real article sentence. " * 20
    raw = f"""<html><body><div class="sidebar">Subscribe to my newsletter now</div>
    <article><h1>Title</h1><p>{body}</p></article>
    <div>Related posts you might like</div></body></html>"""
    text = html_to_text(raw)
    assert "Real article sentence." in text
    assert "newsletter" not in text
    assert "Related posts" not in text


def test_import_markdown_note_uses_heading_as_title(tmp_path: Path):
    note = tmp_path / "meeting.md"
    note.write_text("# Research call: pricing\n\nWe agreed on usage-based pricing.\n", encoding="utf-8")
    path = import_text_file(note, tmp_path / "Notes")
    record = parse_source_file(path)
    assert record["title"] == "Research call: pricing"
    assert record["video_id"] == "note-research-call-pricing"
    assert "usage-based pricing" in record["transcript"]
