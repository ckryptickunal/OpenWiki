import shutil

from wikiblocks.links import extract_links, walk_wiki_graph
from wikiblocks.lint import build_report
from wikiblocks.wiki import ingest_path, rebuild_index
from wikiblocks.workspace import Workspace


def test_entity_and_topic_links_created(workspace: Workspace, fixtures, demo_analysis: dict):
    folder = workspace.root / "Example Channel"
    folder.mkdir()
    path = folder / "demo-talk.txt"
    shutil.copy(fixtures / "transcripts" / "demo-talk.txt", path)
    ingest_path(path, workspace, {}, analysis=demo_analysis)
    rebuild_index(workspace)

    source = next(workspace.sources_dir.glob("demo-talk-*.md")).read_text(encoding="utf-8")
    assert "[[entities/ada-lovelace|Ada Lovelace]]" in source
    assert "[[topics/lab-notebooks|Lab notebooks]]" in source

    entity = (workspace.entities_dir / "ada-lovelace.md").read_text(encoding="utf-8")
    assert "[[sources/demo-talk-how-to-keep-a-lab-notebook|How to keep a lab notebook]]" in entity

    report = build_report(workspace)
    assert report["missing_links"] == []
    assert report["missing_frontmatter"] == []


def test_extract_links_splits_alias_and_hash():
    assert extract_links("See [[entities/ada-lovelace|Ada]] and [[topics/lab#section]]") == [
        "entities/ada-lovelace",
        "topics/lab",
    ]


def test_index_lists_created_pages(workspace: Workspace, fixtures, demo_analysis: dict):
    folder = workspace.root / "Example Channel"
    folder.mkdir()
    shutil.copy(fixtures / "transcripts" / "demo-talk.txt", folder / "demo-talk.txt")
    ingest_path(folder / "demo-talk.txt", workspace, {}, analysis=demo_analysis)
    rebuild_index(workspace)
    index = workspace.index_path.read_text(encoding="utf-8")
    assert "[[sources/demo-talk-how-to-keep-a-lab-notebook|" in index
    assert "[[entities/ada-lovelace|" in index
    assert "[[topics/lab-notebooks|" in index
