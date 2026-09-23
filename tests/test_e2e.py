"""Dry local end-to-end: fixture extract → ingest → lint. No network, no keys."""

from __future__ import annotations

import json
from pathlib import Path

from wikiblocks.cli import main
from wikiblocks.essays import write_article_from_html
from wikiblocks.lint import build_report
from wikiblocks.wiki import ingest_path, rebuild_index
from wikiblocks.workspace import Workspace


def test_fixture_extract_ingest_lint(workspace: Workspace, fixtures: Path):
    talks = workspace.root / "Talks"
    essays = workspace.root / "Essays"
    talks.mkdir()
    essays.mkdir()

    transcript = (fixtures / "transcripts" / "demo-talk.txt").read_text(encoding="utf-8")
    (talks / "demo-talk.txt").write_text(transcript, encoding="utf-8")

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
    assert essay_path is not None
    assert essay_path.exists()

    talk_analysis = json.loads((fixtures / "analysis" / "demo-talk.json").read_text())
    essay_analysis = json.loads((fixtures / "analysis" / "sample-essay.json").read_text())
    manifest: dict = {}
    assert ingest_path(talks / "demo-talk.txt", workspace, manifest, analysis=talk_analysis) == "processed"
    assert ingest_path(essay_path, workspace, manifest, analysis=essay_analysis) == "processed"
    rebuild_index(workspace)

    report = build_report(workspace)
    assert report["page_count"] >= 5
    assert report["missing_frontmatter"] == []
    assert report["missing_links"] == []
    assert (workspace.wiki / "index.md").exists()
    assert "demo-talk" in manifest
    assert any(key.startswith("ex-") for key in manifest)


def test_cli_ingest_and_lint_on_fixtures(tmp_path: Path, fixtures: Path):
    talks = tmp_path / "Talks"
    talks.mkdir()
    (talks / "demo-talk.txt").write_text(
        (fixtures / "transcripts" / "demo-talk.txt").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    analysis = fixtures / "analysis" / "demo-talk.json"
    assert main([
        "--root",
        str(tmp_path),
        "ingest",
        "--file",
        str(talks / "demo-talk.txt"),
        "--analysis-file",
        str(analysis),
    ]) == 0
    assert main(["--root", str(tmp_path), "lint", "--fix-index"]) == 0
    ws = Workspace(tmp_path)
    assert (ws.entities_dir / "ada-lovelace.md").exists()
    assert ws.index_path.exists()
