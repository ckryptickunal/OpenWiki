from pathlib import Path

from openwiki.textfmt import parse_source_file, slugify, write_essay_file, write_youtube_file
from openwiki.youtube import classify_fetch_error, extract_video_id


def test_extract_video_id_from_watch_and_short_urls():
    assert extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert extract_video_id("https://youtu.be/dQw4w9WgXcQ?t=12") == "dQw4w9WgXcQ"
    assert extract_video_id("https://www.youtube.com/shorts/abc123XYZ_-") == "abc123XYZ_-"
    assert extract_video_id("dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert extract_video_id("https://www.youtube.com/live/dQw4w9WgXcQ?si=x") == "dQw4w9WgXcQ"
    assert extract_video_id("https://www.youtube.com/embed/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert extract_video_id("https://m.youtube.com/watch?v=dQw4w9WgXcQ&list=PL1") == "dQw4w9WgXcQ"


def test_youtube_header_roundtrip(tmp_path: Path):
    path = tmp_path / "abc123.txt"
    write_youtube_file(
        path,
        "abc123",
        {
            "title": "Demo Talk",
            "channel_title": "Example Channel",
            "published_at": "2024-01-15T12:00:00Z",
            "description": "A short description.",
            "duration": "PT4M10S",
            "view_count": "120",
            "like_count": "8",
            "tags": ["research", "notes"],
        },
        body="Write the date first.",
        language="English",
        language_code="en",
        is_generated=False,
        snippet_count=4,
    )
    record = parse_source_file(path)
    assert record["video_id"] == "abc123"
    assert record["title"] == "Demo Talk"
    assert record["metadata"]["channel"] == "Example Channel"
    assert record["metadata"]["url"] == "https://www.youtube.com/watch?v=abc123"
    assert record["metadata"]["duration"] == "PT4M10S"
    assert record["metadata"]["transcript_language"] == "English (en)"
    assert record["metadata"]["auto-generated"] == "False"
    assert record["transcript"].startswith("Write the date first.")


def test_essay_header_roundtrip(tmp_path: Path):
    path = tmp_path / "ex-why-indexes.txt"
    write_essay_file(
        path,
        "ex-why-indexes",
        "Why indexes beat memory",
        "Unknown",
        "Example Essays (web)",
        "https://example.com/why-indexes-beat-memory",
        "A working index is better than memory.",
    )
    record = parse_source_file(path)
    assert record["video_id"] == "ex-why-indexes"
    assert record["metadata"]["source"] == "https://example.com/why-indexes-beat-memory"
    assert "working index" in record["transcript"]


def test_parse_fixture_transcript(fixtures: Path):
    record = parse_source_file(fixtures / "transcripts" / "demo-talk.txt")
    assert record["video_id"] == "demo-talk"
    assert "keep the failure" in record["transcript"]


def _named_error(name: str, message: str = "") -> Exception:
    return type(name, (Exception,), {})(message)


def test_classify_by_exception_class():
    assert classify_fetch_error(_named_error("TranscriptsDisabled")) == "no_captions"
    assert classify_fetch_error(_named_error("VideoUnavailable")) == "unplayable"
    assert classify_fetch_error(_named_error("AgeRestricted")) == "unplayable"
    # An IP block is never a permanent skip, even if the message mentions transcripts.
    assert classify_fetch_error(_named_error("IpBlocked", "no transcript, disabled")) == "ip_blocked"
    assert classify_fetch_error(_named_error("RequestBlocked")) == "ip_blocked"


def test_classify_by_message_fallback():
    assert classify_fetch_error(RuntimeError("Subtitles are disabled for this video")) == "no_captions"
    assert classify_fetch_error(RuntimeError("unplayable live event")) == "unplayable"
    assert classify_fetch_error(RuntimeError("429 Too Many Requests")) == "ip_blocked"
    assert classify_fetch_error(RuntimeError("connection reset")) == "error"


def test_slugify_keeps_non_latin_names_distinct():
    assert slugify("Café Société") == "cafe-societe"
    assert slugify("Jeff Dean: The 1% Rule") == "jeff-dean-the-1-rule"
    assert slugify("नरेंद्र मोदी") != slugify("深度学习")
    assert slugify("深度学习") == "深度学习"
    assert slugify("नरेंद्र मोदी") == "नरेंद्र-मोदी"
    assert slugify("???") == "untitled"
