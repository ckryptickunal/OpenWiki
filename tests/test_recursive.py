import json
import shutil
from pathlib import Path

from wikiblocks.links import walk_ingest_queue, walk_wiki_graph
from wikiblocks.wiki import ingest_path
from wikiblocks.workspace import Workspace


def test_cycle_walk_is_finite(tmp_path: Path, fixtures: Path):
    wiki = tmp_path / "wiki"
    shutil.copytree(fixtures / "wiki", wiki)
    ws = Workspace(tmp_path)

    order = walk_wiki_graph(ws, "sources/alpha-source")
    assert order[0] == "sources/alpha-source"
    assert "entities/alice" in order
    assert "topics/recursion" in order
    assert len(order) == len(set(order))
    assert len(order) == 3

    again = walk_wiki_graph(ws, "entities/alice")
    assert set(again) == {"sources/alpha-source", "entities/alice", "topics/recursion"}


def test_ingest_shared_entity_does_not_loop(workspace: Workspace, fixtures: Path):
    talk = workspace.root / "Talks"
    essays = workspace.root / "Essays"
    talk.mkdir()
    essays.mkdir()
    shutil.copy(fixtures / "transcripts" / "demo-talk.txt", talk / "demo-talk.txt")

    from wikiblocks.essays import write_article_from_html

    html = (fixtures / "articles" / "sample-essay.html").read_text(encoding="utf-8")
    essay_path = write_article_from_html(
        html,
        folder=essays,
        title="Why indexes beat memory",
        url="https://example.com/why-indexes-beat-memory",
        channel="Example Essays (web)",
        prefix="ex",
        min_chars=40,
    )
    talk_analysis = json.loads((fixtures / "analysis" / "demo-talk.json").read_text())
    essay_analysis = json.loads((fixtures / "analysis" / "sample-essay.json").read_text())

    manifest: dict = {}
    ingest_path(talk / "demo-talk.txt", workspace, manifest, analysis=talk_analysis)
    ingest_path(essay_path, workspace, manifest, analysis=essay_analysis)
    ingest_path(talk / "demo-talk.txt", workspace, manifest, analysis=talk_analysis)

    entity = (workspace.entities_dir / "ada-lovelace.md").read_text(encoding="utf-8")
    assert entity.count("[[sources/demo-talk-") == 1
    assert "Why indexes beat memory" in entity

    order = walk_wiki_graph(workspace, "sources/demo-talk-how-to-keep-a-lab-notebook")
    assert "entities/ada-lovelace" in order
    assert any(node.startswith("sources/ex-why-indexes") for node in order)
    assert len(order) == len(set(order))


def test_walk_ingest_queue_breaks_cycles():
    related = {
        "a": ["b"],
        "b": ["a", "c"],
        "c": ["a"],
    }
    order = walk_ingest_queue(["a"], related)
    assert order == ["a", "b", "c"]
