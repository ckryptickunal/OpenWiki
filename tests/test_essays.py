from pathlib import Path

from openwiki.essays import (
    discover_new_from_html,
    html_to_text,
    parse_generic_index,
    parse_paulgraham_index,
    write_article_from_html,
)


def test_html_to_text_strips_nav_and_script(fixtures: Path):
    raw = (fixtures / "articles" / "sample-essay.html").read_text(encoding="utf-8")
    text = html_to_text(raw)
    assert "void 0" not in text
    assert "Home | About" not in text
    assert "indexes beat memory" in text.lower()
    assert "ignore me" not in text.lower()


def test_generic_index_stays_on_base(fixtures: Path):
    html = (fixtures / "articles" / "index.html").read_text(encoding="utf-8")
    listed = parse_generic_index(html, "https://example.com")
    urls = [item["url"] for item in listed]
    assert "https://example.com/why-indexes-beat-memory" in urls
    assert all("other.example" not in url for url in urls)


def test_paulgraham_index_kind():
    html = '<a href="avg.html">Beating the Averages</a><a href="articles.html">Essays</a>'
    listed = parse_paulgraham_index(html, "https://www.paulgraham.com/")
    assert listed == [{"title": "Beating the Averages", "url": "https://www.paulgraham.com/avg.html"}]


def test_discover_skips_existing_files(tmp_path: Path, fixtures: Path):
    folder = tmp_path / "Example Essays"
    folder.mkdir()
    source = {
        "kind": "generic",
        "base_url": "https://example.com",
        "id_prefix": "ex",
    }
    html = (fixtures / "articles" / "index.html").read_text(encoding="utf-8")
    first = discover_new_from_html(source, html, folder)
    titles = {item["title"] for item in first}
    assert "Why indexes beat memory" in titles

    (folder / "ex-why-indexes-beat-memory.txt").write_text("already here", encoding="utf-8")
    second = discover_new_from_html(source, html, folder)
    assert all(item["title"] != "Why indexes beat memory" for item in second)


def test_write_article_from_saved_html(tmp_path: Path, fixtures: Path):
    raw = (fixtures / "articles" / "sample-essay.html").read_text(encoding="utf-8")
    path = write_article_from_html(
        raw,
        folder=tmp_path,
        title="Why indexes beat memory",
        url="https://example.com/why-indexes-beat-memory",
        channel="Example Essays (web)",
        prefix="ex",
        min_chars=40,
    )
    assert path is not None
    assert path.name == "ex-why-indexes-beat-memory.txt"
    assert "TRANSCRIPT" in path.read_text(encoding="utf-8")
