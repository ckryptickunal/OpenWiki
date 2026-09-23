import shutil

import pytest

from openwiki.wiki import ingest_path


def test_ingest_without_key_or_analysis_raises(workspace, fixtures, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    folder = workspace.root / "Talks"
    folder.mkdir()
    shutil.copy(fixtures / "transcripts" / "demo-talk.txt", folder / "demo-talk.txt")
    with pytest.raises(RuntimeError, match="GEMINI_API_KEY"):
        ingest_path(folder / "demo-talk.txt", workspace, {})
