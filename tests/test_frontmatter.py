import re
import shutil

from wikiblocks.lint import has_frontmatter
from wikiblocks.wiki import ingest_path, render_source_page
from wikiblocks.workspace import Workspace


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
