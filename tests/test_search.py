from __future__ import annotations

from pathlib import Path

from openwiki.cli import main
from openwiki.search import NOT_IN_SOURCES, ask, search, snippet
from openwiki.textfmt import write_source_file
from openwiki.workspace import Workspace

TIMED = "\n".join([
    "[0:05] Welcome to the talk about outbound sales.",
    "[0:40] Do at least one hundred outreaches by hand before you automate anything.",
    "[1:15] Reply rates of two or three percent are a great start.",
])


def _workspace(tmp_path: Path) -> Workspace:
    ws = Workspace(tmp_path)
    ws.ensure_dirs()
    write_source_file(tmp_path / "Talks" / "abcdefghijk.txt", title="Cold email basics", source_id="abcdefghijk", body=TIMED)
    write_source_file(tmp_path / "Notes" / "note-garden.txt", title="Garden notes", source_id="note-garden", body="Tomatoes need full sun.")
    return ws


def test_search_links_to_the_moment_in_the_video(tmp_path: Path):
    ws = _workspace(tmp_path)
    hits = search(ws, "outreaches automate")
    assert len(hits) == 1
    hit = hits[0]
    assert hit.title == "Cold email basics"
    assert hit.stamp == "0:05"  # passage starts at the first cue it contains
    assert hit.link == "https://www.youtube.com/watch?v=abcdefghijk&t=5s"
    assert "outreaches" in snippet(hit, "outreaches")


def test_search_requires_every_term_but_any_mode_does_not(tmp_path: Path):
    ws = _workspace(tmp_path)
    assert search(ws, "outreaches tomatoes") == []
    assert {h.title for h in search(ws, "outreaches tomatoes", match="any", per_file=1)} == {"Cold email basics", "Garden notes"}


def test_search_non_youtube_source_has_no_link(tmp_path: Path):
    ws = _workspace(tmp_path)
    hit = search(ws, "tomatoes")[0]
    assert hit.link == ""


class FakeClient:
    provider = "fake"

    def __init__(self, reply: str):
        self.reply = reply
        self.prompts: list[str] = []

    def generate(self, prompt, *, json_mode=False, temperature=0.2):
        self.prompts.append(prompt)
        return self.reply


def test_ask_sends_numbered_passages_and_returns_them(tmp_path: Path):
    ws = _workspace(tmp_path)
    client = FakeClient("Do one hundred by hand first [1].")
    answer, passages = ask(ws, "How many outreaches before I automate?", client=client)
    assert answer == "Do one hundred by hand first [1]."
    assert passages[0].title == "Cold email basics"
    assert "[1] Cold email basics at 0:05" in client.prompts[0]
    assert NOT_IN_SOURCES in client.prompts[0]


def test_ask_abstains_without_calling_the_model_when_nothing_matches(tmp_path: Path):
    ws = _workspace(tmp_path)
    client = FakeClient("should not be used")
    answer, passages = ask(ws, "boiling point of tungsten", client=client)
    assert answer == NOT_IN_SOURCES and passages == [] and client.prompts == []


def test_cli_search_prints_timestamp_link(tmp_path: Path, capsys):
    _workspace(tmp_path)
    assert main(["search", "reply", "rates", "--root", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "Cold email basics [0:05]" in out
    assert "watch?v=abcdefghijk&t=5s" in out
    assert main(["search", "nothing-here-xyz", "--root", str(tmp_path)]) == 1


def test_cli_ask_lists_grouped_citations(tmp_path: Path, capsys, monkeypatch):
    _workspace(tmp_path)
    import openwiki.search as search_module

    monkeypatch.setattr("openwiki.llm.make_client", lambda provider=None, lint=False: FakeClient("Answer [1, 2]."))
    assert main(["ask", "outreaches", "tomatoes", "--root", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "[1]" in out.split("Sources:")[1] and "[2]" in out.split("Sources:")[1]
    assert search_module.NOT_IN_SOURCES not in out
