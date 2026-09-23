from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from openwiki.cli import main
from openwiki.templates import SOURCES_EXAMPLE
from openwiki.wiki import read_title, render_source_page, yaml_scalar
from openwiki.workspace import Workspace

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def no_llm(monkeypatch):
    for name in ["LLM_PROVIDER", "GEMINI_API_KEY", "OPENAI_API_KEY", "OPENAI_BASE_URL", "OPENAI_MODEL"]:
        monkeypatch.delenv(name, raising=False)


def test_sources_template_matches_repo_example():
    assert SOURCES_EXAMPLE == (REPO_ROOT / "sources.example.json").read_text(encoding="utf-8")


def test_init_creates_workspace(tmp_path: Path):
    root = tmp_path / "my-wiki"
    assert main(["init", "--root", str(root)]) == 0
    assert json.loads((root / "sources.json").read_text())["youtube_channels"]
    assert (root / "wiki" / "schema.md").exists()
    assert ".env" in (root / ".gitignore").read_text()


def test_root_works_before_or_after_command(tmp_path: Path):
    assert main(["--root", str(tmp_path / "a"), "init"]) == 0
    assert main(["init", "--root", str(tmp_path / "b")]) == 0
    assert (tmp_path / "a" / "sources.json").exists()
    assert (tmp_path / "b" / "sources.json").exists()


def test_text_then_ingest_then_lint(tmp_path: Path, fixtures: Path):
    note = tmp_path / "note.md"
    note.write_text("# Lab notebook habits\n\nWrite the date first.\n", encoding="utf-8")
    assert main(["text", str(note), "--root", str(tmp_path), "--folder", "Notes"]) == 0
    src = tmp_path / "Notes" / "note-lab-notebook-habits.txt"
    assert src.exists()
    assert main([
        "ingest", "--root", str(tmp_path), "--file", str(src),
        "--analysis-file", str(fixtures / "analysis" / "demo-talk.json"),
    ]) == 0
    assert main(["lint", "--root", str(tmp_path), "--fix-index", "--strict"]) == 0


def test_ingest_without_llm_exits_2_with_hint(tmp_path: Path, fixtures: Path, no_llm, capsys):
    folder = tmp_path / "Talks"
    folder.mkdir()
    shutil.copy(fixtures / "transcripts" / "demo-talk.txt", folder / "demo-talk.txt")
    assert main(["ingest", "--root", str(tmp_path)]) == 2
    err = capsys.readouterr().err
    assert "GEMINI_API_KEY" in err and "OPENAI_BASE_URL" in err


def test_ingest_failure_is_recorded_then_cleared(tmp_path: Path, fixtures: Path, demo_analysis: dict):
    from openwiki.wiki import ingest_paths

    ws = Workspace(tmp_path)
    folder = tmp_path / "Talks"
    folder.mkdir()
    src = folder / "demo-talk.txt"
    shutil.copy(fixtures / "transcripts" / "demo-talk.txt", src)

    def broken(record, max_chars):
        raise ValueError("model timed out")

    counts = ingest_paths([src], ws, analyzer=broken)
    assert counts["failed"] == 1
    failures = json.loads(ws.failures_path.read_text())
    assert "model timed out" in failures["Talks/demo-talk.txt"]

    counts = ingest_paths([src], ws, analysis=demo_analysis)
    assert counts["processed"] == 1
    assert not ws.failures_path.exists()


def test_discover_skips_repo_folders(tmp_path: Path):
    for name in ["examples", "docs", "Talks"]:
        (tmp_path / name).mkdir()
        (tmp_path / name / "x.txt").write_text("Title: x\n", encoding="utf-8")
    found = Workspace(tmp_path).discover_source_files()
    assert [p.parent.name for p in found] == ["Talks"]


@pytest.mark.parametrize("title", [
    "Jeff Dean: The 1% Rule for Building in AI",
    'Peter Steinberger: "Fun Is Velocity"',
    "#1 Open-Source Coding Agent",
    "yes",
    "2024",
])
def test_titles_with_yaml_special_chars_are_quoted(tmp_path: Path, title: str):
    record = {"video_id": "abcdefghijk", "title": title, "metadata": {"channel": "YC"}, "transcript": ""}
    page = render_source_page(record, {"summary": "s"})
    line = next(line for line in page.splitlines() if line.startswith("title: "))
    assert line == f"title: {json.dumps(title)}"
    path = tmp_path / "p.md"
    path.write_text(page, encoding="utf-8")
    assert read_title(path) == title


def test_plain_titles_and_urls_stay_readable():
    assert yaml_scalar("How to keep a lab notebook") == "How to keep a lab notebook"
    assert yaml_scalar("https://example.com/a?b=1") == "https://example.com/a?b=1"
