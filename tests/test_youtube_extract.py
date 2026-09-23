"""Caption selection and extract bookkeeping, with the network mocked out."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from openwiki import youtube
from openwiki.youtube import (
    NoCaptionsAvailable,
    classify_fetch_error,
    extract_one_video,
    extract_playlist_id,
    extract_videos,
    pick_transcript,
)


class NoTranscriptFound(Exception):
    """Same class name as youtube-transcript-api's language-miss error."""


class FakeTranscriptList:
    def __init__(self, tracks: list[str]):
        self.tracks = tracks

    def find_transcript(self, languages):
        for code in languages:
            if code in self.tracks:
                return code
        raise NoTranscriptFound("no match for requested languages")

    def __iter__(self):
        return iter(self.tracks)


def test_pick_transcript_prefers_requested_language():
    assert pick_transcript(FakeTranscriptList(["de", "en"]), ["en"]) == "en"


def test_pick_transcript_falls_back_to_any_language():
    # A Hindi-only video must not be treated as "no captions" just because English is missing.
    assert pick_transcript(FakeTranscriptList(["hi"]), ["en"]) == "hi"


def test_pick_transcript_with_no_tracks_is_permanent_skip():
    with pytest.raises(NoCaptionsAvailable) as info:
        pick_transcript(FakeTranscriptList([]), ["en"])
    assert classify_fetch_error(info.value) == "no_captions"


def test_extract_playlist_id():
    assert extract_playlist_id("https://www.youtube.com/playlist?list=PLabc123") == "PLabc123"
    assert extract_playlist_id("https://www.youtube.com/watch?v=x&list=PLxyz") == "PLxyz"
    assert extract_playlist_id("PLbare") == "PLbare"


def test_single_video_uses_oembed_title_without_api_key(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(
        youtube, "get_oembed_metadata",
        lambda vid: {"title": "Me at the zoo", "channel_title": "jawed"},
    )
    monkeypatch.setattr(
        youtube, "fetch_transcript",
        lambda vid, languages=None, proxy=None: youtube.FetchedTranscript(text="the elephants", snippet_count=1),
    )
    assert extract_one_video("jNQXAC9IVRw", tmp_path, youtube=None) == "ok"
    text = (tmp_path / "jNQXAC9IVRw.txt").read_text(encoding="utf-8")
    assert "Title: Me at the zoo" in text
    assert "Channel: jawed" in text


def test_extract_videos_records_permanent_skips(tmp_path: Path, monkeypatch):
    def fake_fetch(vid, languages=None, proxy=None):
        if vid == "nocaptions1":
            raise type("TranscriptsDisabled", (Exception,), {})("off")
        return youtube.FetchedTranscript(text=f"body of {vid}", snippet_count=1)

    monkeypatch.setattr(youtube, "get_oembed_metadata", lambda vid: {})
    monkeypatch.setattr(youtube, "fetch_transcript", fake_fetch)
    counts = extract_videos(["okvideo0001", "nocaptions1"], tmp_path)
    assert counts == {"ok": 1, "skip": 1, "exists": 0, "failed": 0}
    state = json.loads((tmp_path / "_extract_state.json").read_text(encoding="utf-8"))
    assert state["done"] == ["okvideo0001"]
    assert state["permanent_skip"] == ["nocaptions1"]

    # Second run: nothing is fetched again.
    monkeypatch.setattr(youtube, "fetch_transcript", lambda *a, **k: pytest.fail("refetched"))
    again = extract_videos(["okvideo0001", "nocaptions1"], tmp_path)
    assert again == {"ok": 0, "skip": 1, "exists": 1, "failed": 0}


def test_ip_block_is_retryable_not_skipped(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(youtube, "get_oembed_metadata", lambda vid: {})
    monkeypatch.setattr(youtube.time, "sleep", lambda s: None)
    monkeypatch.setattr(
        youtube, "fetch_transcript",
        lambda *a, **k: (_ for _ in ()).throw(type("IpBlocked", (Exception,), {})("blocked")),
    )
    counts = extract_videos(["blocked0001"], tmp_path)
    assert counts["failed"] == 1
    state = json.loads((tmp_path / "_extract_state.json").read_text(encoding="utf-8"))
    assert state["permanent_skip"] == []
