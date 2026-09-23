import shutil
from pathlib import Path

from openwiki.wiki import ingest_path, load_manifest
from openwiki.workspace import Workspace


def _copy_demo(workspace: Workspace, fixtures: Path) -> Path:
    folder = workspace.root / "Example Channel"
    folder.mkdir()
    dest = folder / "demo-talk.txt"
    shutil.copy(fixtures / "transcripts" / "demo-talk.txt", dest)
    return dest


def test_same_file_not_ingested_twice(workspace: Workspace, fixtures: Path, demo_analysis: dict):
    path = _copy_demo(workspace, fixtures)
    manifest: dict = {}
    first = ingest_path(path, workspace, manifest, analysis=demo_analysis)
    second = ingest_path(path, workspace, manifest, analysis=demo_analysis)
    assert first == "processed"
    assert second == "skipped"
    saved = load_manifest(workspace)
    assert list(saved) == ["demo-talk"]

    entity = (workspace.entities_dir / "ada-lovelace.md").read_text(encoding="utf-8")
    assert entity.count("[[sources/demo-talk-how-to-keep-a-lab-notebook|How to keep a lab notebook]]") == 1


def test_force_reingest_updates_mtime_record(workspace: Workspace, fixtures: Path, demo_analysis: dict):
    path = _copy_demo(workspace, fixtures)
    manifest: dict = {}
    ingest_path(path, workspace, manifest, analysis=demo_analysis)
    third = ingest_path(path, workspace, manifest, analysis=demo_analysis, force=True)
    assert third == "processed"
    assert "demo-talk" in manifest
