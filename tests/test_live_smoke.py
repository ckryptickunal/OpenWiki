"""Optional live smoke tests. Skipped unless keys are already in the environment.

Never prints secret values. Uses a short public video. Does not touch the
Founder Book corpus.
"""

from __future__ import annotations

import os

import pytest

from wikiblocks.env import env_value

# First YouTube video (19s). If captions are missing, extract_one_video returns skip.
PUBLIC_VIDEO_ID = "jNQXAC9IVRw"


@pytest.mark.live
@pytest.mark.skipif(not env_value("YOUTUBE_API_KEY") and not os.getenv("YOUTUBE_API_KEY"), reason="YOUTUBE_API_KEY not set")
def test_live_youtube_one_public_video(tmp_path):
    from wikiblocks.youtube import extract_one_video, maybe_youtube_client

    youtube = maybe_youtube_client()
    result = extract_one_video(PUBLIC_VIDEO_ID, tmp_path / "single_videos", youtube=youtube)
    assert result in {"ok", "skip", "exists"}
    if result == "ok":
        text = (tmp_path / "single_videos" / f"{PUBLIC_VIDEO_ID}.txt").read_text(encoding="utf-8")
        assert text.startswith("Title:")
        assert "TRANSCRIPT" in text


@pytest.mark.live
@pytest.mark.skipif(not env_value("GEMINI_API_KEY") and not os.getenv("GEMINI_API_KEY"), reason="GEMINI_API_KEY not set")
def test_live_gemini_ingest_fixture_only(tmp_path, fixtures):
    from wikiblocks.wiki import ingest_path
    from wikiblocks.workspace import Workspace

    ws = Workspace(tmp_path)
    ws.ensure_dirs()
    folder = ws.root / "Talks"
    folder.mkdir()
    dest = folder / "demo-talk.txt"
    dest.write_text((fixtures / "transcripts" / "demo-talk.txt").read_text(encoding="utf-8"), encoding="utf-8")
    result = ingest_path(dest, ws, {})
    assert result == "processed"
    assert list(ws.sources_dir.glob("demo-talk-*.md"))
