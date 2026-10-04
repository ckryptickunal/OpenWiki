"""Speech-to-text fallback and Tor circuit rotation, with network and models mocked out."""

from __future__ import annotations

from pathlib import Path

from openwiki import asr, youtube
from openwiki.youtube import FetchedTranscript, NoCaptionsAvailable, extract_one_video


class RequestBlocked(Exception):
    """Same class name as youtube-transcript-api's IP-block error."""


def _no_meta(monkeypatch):
    monkeypatch.setattr(youtube, "get_oembed_metadata", lambda vid: {"title": "T", "channel_title": "C"})
    monkeypatch.setattr(youtube.time, "sleep", lambda s: None)


def _fake_asr(calls: list):
    def transcribe_video(video_id, *, languages=None):
        calls.append((video_id, languages))
        return FetchedTranscript(text="[0:00] नमस्ते", language="hi (speech-to-text: mlx_whisper)",
                                 language_code="hi", is_generated=True, snippet_count=1)
    return transcribe_video


def test_no_captions_without_asr_is_still_a_skip(tmp_path: Path, monkeypatch):
    _no_meta(monkeypatch)
    monkeypatch.setattr(youtube, "fetch_transcript", lambda *a, **k: (_ for _ in ()).throw(NoCaptionsAvailable("no captions")))
    assert extract_one_video("abc", tmp_path) == "skip"


def test_no_captions_with_asr_transcribes_audio(tmp_path: Path, monkeypatch):
    _no_meta(monkeypatch)
    calls: list = []
    monkeypatch.setattr(youtube, "fetch_transcript", lambda *a, **k: (_ for _ in ()).throw(NoCaptionsAvailable("no captions")))
    monkeypatch.setattr(asr, "transcribe_video", _fake_asr(calls))
    assert extract_one_video("abc", tmp_path, languages=["hi", "en"], asr=True) == "ok"
    assert calls == [("abc", ["hi", "en"])]
    text = (tmp_path / "abc.txt").read_text(encoding="utf-8")
    assert "speech-to-text" in text and "नमस्ते" in text


def test_ip_block_with_asr_falls_back(tmp_path: Path, monkeypatch):
    _no_meta(monkeypatch)
    calls: list = []
    monkeypatch.setattr(youtube, "fetch_transcript", lambda *a, **k: (_ for _ in ()).throw(RequestBlocked("blocked")))
    monkeypatch.setattr(asr, "transcribe_video", _fake_asr(calls))
    assert extract_one_video("abc", tmp_path, asr=True) == "ok"
    assert len(calls) == 1


def test_asr_failure_reports_failed_with_reason(tmp_path: Path, monkeypatch):
    _no_meta(monkeypatch)
    monkeypatch.setattr(youtube, "fetch_transcript", lambda *a, **k: (_ for _ in ()).throw(RequestBlocked("blocked")))

    def broken(video_id, *, languages=None):
        raise asr.ASRUnavailable("no backend")

    monkeypatch.setattr(asr, "transcribe_video", broken)
    detail: dict = {}
    assert extract_one_video("abc", tmp_path, asr=True, detail=detail) == "failed"
    assert detail["kind"] == "ip_blocked" and "no backend" in detail["reason"]


def test_tor_rotation_retries_after_block(tmp_path: Path, monkeypatch):
    _no_meta(monkeypatch)
    attempts = {"n": 0}

    def flaky(*a, **k):
        attempts["n"] += 1
        if attempts["n"] == 1:
            raise RequestBlocked("blocked")
        return FetchedTranscript(text="[0:01] hello", snippet_count=1)

    rotated: list = []
    monkeypatch.setattr(youtube, "fetch_transcript", flaky)
    monkeypatch.setattr(youtube, "new_tor_circuit", lambda port: rotated.append(port) or True)
    monkeypatch.setenv("YOUTUBE_TOR_CONTROL_PORT", "9051")
    assert extract_one_video("abc", tmp_path) == "ok"
    assert rotated == [9051] and attempts["n"] == 2


def test_asr_language_uses_first_preferred():
    assert asr.asr_language(["hi", "en"]) == "hi"
    assert asr.asr_language(["en-US"]) == "en"
    assert asr.asr_language(None) is None


def test_segments_format_like_captions():
    from openwiki.textfmt import format_timed_transcript

    text = format_timed_transcript([asr.Segment(0.0, " पहला "), asr.Segment(65.4, "second"), asr.Segment(70, " ")])
    assert text == "[0:00] पहला\n[1:05] second"


def test_asr_retries_videos_skipped_for_no_captions(tmp_path: Path, monkeypatch):
    _no_meta(monkeypatch)
    youtube.save_extract_state(tmp_path, {**youtube.empty_extract_state(), "permanent_skip": ["abc", "gone"],
                                          "skip_reasons": {"abc": "no_captions", "gone": "unplayable"}})
    calls: list = []
    monkeypatch.setattr(youtube, "fetch_transcript", lambda *a, **k: (_ for _ in ()).throw(NoCaptionsAvailable("no captions")))
    monkeypatch.setattr(asr, "transcribe_video", _fake_asr(calls))

    assert youtube.extract_videos(["abc", "gone"], tmp_path)["skip"] == 2  # without --asr: still skipped
    assert calls == []
    counts = youtube.extract_videos(["abc", "gone"], tmp_path, asr=True)
    assert counts == {"ok": 1, "skip": 1, "exists": 0, "failed": 0}  # the unplayable one is never retried
    state = youtube.load_extract_state(tmp_path)
    assert state["permanent_skip"] == ["gone"] and "abc" not in state["skip_reasons"] and "abc" in state["done"]


def test_bad_tor_control_port_is_ignored(tmp_path: Path, monkeypatch):
    _no_meta(monkeypatch)
    monkeypatch.setattr(youtube, "fetch_transcript", lambda *a, **k: (_ for _ in ()).throw(RequestBlocked("blocked")))
    monkeypatch.setattr(youtube, "new_tor_circuit", lambda port: (_ for _ in ()).throw(AssertionError("called")))
    monkeypatch.setenv("YOUTUBE_TOR_CONTROL_PORT", "not-a-port")
    assert extract_one_video("abc", tmp_path) == "failed"
