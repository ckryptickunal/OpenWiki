import re
import shutil

from openwiki.lint import has_frontmatter
from openwiki.wiki import ingest_path, render_source_page
from openwiki.workspace import Workspace


def test_source_frontmatter_fields(workspace: Workspace, fixtures, demo_analysis: dict):
    src = workspace.root / "Example Channel"
    src.mkdir()
    path = src / "demo-talk.txt"
    shutil.copy(fixtures / "transcripts" / "demo-talk.txt", path)
    ingest_path(path, workspace, {}, analysis=demo_analysis)

    page = next(workspace.sources_dir.glob("demo-talk-*.md"))
    text = page.read_text(encoding="utf-8")
    assert has_frontmatter(text)
    assert text.startswith("---\n")
    assert "type: source" in text
    assert "title: How to keep a lab notebook" in text
    assert "video_id: demo-talk" in text
    assert re.search(r"^created: \d{4}-\d{2}-\d{2}$", text, re.M)
    assert "  - research" in text
    assert "  - notes" in text


def test_entity_and_topic_frontmatter(workspace: Workspace, fixtures, demo_analysis: dict):
    src = workspace.root / "Example Channel"
    src.mkdir()
    path = src / "demo-talk.txt"
    shutil.copy(fixtures / "transcripts" / "demo-talk.txt", path)
    ingest_path(path, workspace, {}, analysis=demo_analysis)

    entity = (workspace.entities_dir / "ada-lovelace.md").read_text(encoding="utf-8")
    topic = (workspace.topics_dir / "lab-notebooks.md").read_text(encoding="utf-8")
    assert "type: entity" in entity
    assert "title: Ada Lovelace" in entity
    assert "type: topic" in topic
    assert "title: Lab notebooks" in topic


def test_quotes_need_a_transcript_match_and_keep_timestamps():
    record = {
        "video_id": "dQw4w9WgXcQ",
        "title": "Demo",
        "metadata": {"channel": "C", "published": "Unknown", "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
        "transcript": "[1:05] If a step failed, keep the failure.\n[2:00] Something else entirely.",
    }
    page = render_source_page(record, {
        "summary": "s",
        "quotes": [
            "If a step failed, keep the failure.",
            "This sentence was never spoken.",
        ],
        "claims": [{"claim": "Failures belong in the notes.", "evidence": "If a step failed, keep the failure."}],
    })
    assert "> If a step failed, keep the failure." in page
    assert "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=65s" in page
    assert "This sentence was never spoken." not in page
    assert "t=65s" in page.split("## Notable Claims", 1)[1].split("## Quotes", 1)[0]


def test_empty_analysis_is_not_written(workspace: Workspace, fixtures):
    from openwiki.wiki import ingest_paths

    src = workspace.root / "Talks"
    src.mkdir()
    path = src / "demo-talk.txt"
    shutil.copy(fixtures / "transcripts" / "demo-talk.txt", path)
    counts = ingest_paths([path], workspace, analysis={})
    assert counts["failed"] == 1
    assert list(workspace.sources_dir.glob("*.md")) == []


def test_render_uses_source_url_for_essays(fixtures):
    record = {
        "video_id": "ex-why-indexes",
        "title": "Why indexes beat memory",
        "metadata": {
            "channel": "Example Essays (web)",
            "published": "Unknown",
            "source": "https://example.com/why-indexes-beat-memory",
        },
        "transcript": "body",
    }
    page = render_source_page(record, {"summary": "s", "tags": [], "entities": [], "topics": [], "claims": [], "quotes": []})
    assert "url: https://example.com/why-indexes-beat-memory" in page
    assert "youtube.com" not in page
