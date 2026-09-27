"""Keyless channel/playlist listing, long-transcript chunking, provenance and ingest plans."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from openwiki import llm, youtube
from openwiki.textfmt import first_mention, write_source_file
from openwiki.wiki import ingest_path, ingest_plan, render_source_page
from openwiki.workspace import Workspace


@pytest.mark.parametrize("given,expected", [
    ("@ycombinator", "https://www.youtube.com/@ycombinator/videos"),
    ("UCcefcZRL2oaA_uBNeo5UOWg", "https://www.youtube.com/channel/UCcefcZRL2oaA_uBNeo5UOWg/videos"),
    ("https://www.youtube.com/@ycombinator/featured", "https://www.youtube.com/@ycombinator/videos"),
    ("https://www.youtube.com/c/SomeName?x=1", "https://www.youtube.com/c/SomeName/videos"),
])
def test_channel_listing_url(given, expected):
    assert youtube.channel_listing_url(given) == expected


def test_channel_listing_url_rejects_free_text_without_api_key():
    with pytest.raises(youtube.ListingUnavailable):
        youtube.channel_listing_url("y combinator")


def test_ytdlp_list_reads_flat_and_nested_entries(monkeypatch):
    monkeypatch.setattr(youtube, "_ytdlp_json", lambda url: {
        "channel": "Example",
        "entries": [
            {"_type": "playlist", "entries": [{"id": "aaaaaaaaaaa"}, {"id": "bbbbbbbbbbb"}]},
            {"id": "ccccccccccc", "ie_key": "Youtube"},
            {"id": "aaaaaaaaaaa"},
        ],
    })
    assert youtube.ytdlp_list("u") == ("Example", ["aaaaaaaaaaa", "bbbbbbbbbbb", "ccccccccccc"])


def test_playlist_uses_ytdlp_without_api_key(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(youtube, "maybe_youtube_client", lambda: None)
    monkeypatch.setattr(youtube, "ytdlp_available", lambda: True)
    monkeypatch.setattr(youtube, "ytdlp_list", lambda url: ("Course", ["aaaaaaaaaaa", "bbbbbbbbbbb"]))
    (tmp_path / "Course").mkdir()
    (tmp_path / "Course" / "aaaaaaaaaaa.txt").write_text("done", encoding="utf-8")
    result = youtube.extract_playlist(Workspace(tmp_path), "https://www.youtube.com/playlist?list=PLx", folder="Course", dry_run=True)
    assert result["listing"] == "yt-dlp"
    assert result["new"] == ["bbbbbbbbbbb"]


def test_listing_without_key_or_ytdlp_explains_the_fix(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(youtube, "maybe_youtube_client", lambda: None)
    monkeypatch.setattr(youtube, "ytdlp_available", lambda: False)
    with pytest.raises(youtube.ListingUnavailable, match="pip install yt-dlp"):
        youtube.extract_channel(Workspace(tmp_path), "@example", dry_run=True)


def test_split_transcript_keeps_lines_whole():
    text = "".join(f"[0:{i:02d}] line {i}\n" for i in range(40))
    parts = llm.split_transcript(text, 100)
    assert len(parts) > 1
    assert "".join(parts) == text
    assert all(len(p) <= 100 for p in parts)


class CountingClient:
    provider = "fake"

    def __init__(self):
        self.calls = 0

    def generate(self, prompt, *, json_mode=False, temperature=0.2):
        self.calls += 1
        if not json_mode:
            return "Whole summary."
        return json.dumps({
            "summary": f"part {self.calls}",
            "key_ideas": ["shared idea", f"idea {self.calls}"],
            "entities": [{"name": "Ada Lovelace"}, {"name": f"Person {self.calls}"}],
            "topics": [{"name": "Notebooks"}],
            "claims": [], "quotes": [], "tags": ["notes"],
        })


def test_long_source_is_analyzed_in_parts_and_merged():
    record = {"title": "Long talk", "video_id": "v", "metadata": {}, "transcript": "word " * 1000}
    client = CountingClient()
    analysis = llm.analyze_record(client, record, max_chars=1500)
    parts = len(llm.split_transcript(record["transcript"], 1500))
    assert parts >= 3
    assert client.calls == parts + 1  # one per part plus the merged summary
    assert analysis["summary"] == "Whole summary."
    assert [e["name"] for e in analysis["entities"]][0] == "Ada Lovelace"
    assert len([e for e in analysis["entities"] if e["name"] == "Ada Lovelace"]) == 1
    assert analysis["key_ideas"].count("shared idea") == 1


def test_first_mention_finds_whole_words_only():
    transcript = "[0:05] We talked about Adam.\n[1:10] Then Ada Lovelace came up.\n"
    assert first_mention(transcript, "Ada Lovelace") == 70
    assert first_mention(transcript, "Ada") == 70
    assert first_mention(transcript, "Grace Hopper") is None


def test_entity_mention_links_to_first_timestamp(workspace: Workspace, demo_analysis: dict):
    path = write_source_file(
        workspace.root / "Talks" / "abcdefghijk.txt", title="Lab notes", source_id="abcdefghijk",
        body="[0:03] Keep a notebook.\n[2:05] Ada Lovelace wrote notes others could follow.\n",
    )
    ingest_path(path, workspace, {}, analysis=demo_analysis)
    entity = (workspace.entities_dir / "ada-lovelace.md").read_text(encoding="utf-8")
    assert "[2:05](https://www.youtube.com/watch?v=abcdefghijk&t=125s)" in entity


def test_quotes_are_separate_blockquotes():
    transcript = "[0:01] alpha beta gamma delta epsilon.\n[0:09] zeta eta theta iota kappa lambda.\n"
    record = {"video_id": "abcdefghijk", "title": "T", "metadata": {}, "transcript": transcript}
    page = render_source_page(record, {"summary": "s", "quotes": ["alpha beta gamma delta epsilon", "zeta eta theta iota kappa"]})
    quotes = page.split("## Quotes")[1]
    assert "\n\n> zeta" in quotes


def test_ingest_plan_counts_pending_work(tmp_path: Path, fixtures: Path):
    ws = Workspace(tmp_path)
    folder = tmp_path / "Talks"
    folder.mkdir()
    shutil.copy(fixtures / "transcripts" / "demo-talk.txt", folder / "demo-talk.txt")
    (folder / "empty.txt").write_text("Title: Empty\n\n" + "=" * 60 + "\nTRANSCRIPT\n" + "=" * 60 + "\n", encoding="utf-8")
    plan = ingest_plan(ws, ws.discover_source_files())
    assert plan["files"] == 1 and plan["empty"] == 1 and plan["llm_calls"] == 1
    assert plan["approx_input_tokens"] > 600
