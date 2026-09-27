"""Offline full-text search over raw sources and wiki pages, and grounded Q&A on top.

Search needs no API key: it ranks passages with BM25. Transcript passages keep
their `[m:ss]` timestamp so a hit links to the exact moment in the video.
`ask` sends only the top passages to the configured LLM and requires citations.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from openwiki.textfmt import CUE_RE, YOUTUBE_ID_RE, format_cue_timestamp, parse_source_file
from openwiki.workspace import Workspace

PASSAGE_CHARS = 900
WORD_RE = re.compile(r"[\w']+", re.UNICODE)
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "did", "do", "does", "for", "from", "how", "i",
    "in", "is", "it", "of", "on", "or", "say", "said", "that", "the", "this", "to", "was", "what",
    "when", "where", "which", "who", "why", "with", "about", "you", "your", "my", "me", "we", "our",
    "many", "much", "should", "would", "could", "can", "will", "have", "has", "get", "there", "their",
    "they", "them", "than", "then", "so", "if", "not", "but", "all", "any", "some", "just", "also", "into",
}
NOT_IN_SOURCES = "Not in your sources."


@dataclass
class Passage:
    path: Path
    title: str
    kind: str              # "source" (raw .txt) or "wiki"
    text: str
    seconds: int | None = None
    video_id: str = ""
    score: float = 0.0

    @property
    def link(self) -> str:
        if self.seconds is not None and YOUTUBE_ID_RE.match(self.video_id):
            return f"https://www.youtube.com/watch?v={self.video_id}&t={self.seconds}s"
        return ""

    @property
    def stamp(self) -> str:
        return format_cue_timestamp(self.seconds) if self.seconds is not None else ""


def terms(text: str) -> list[str]:
    return [w for w in (m.group(0).casefold().strip("'") for m in WORD_RE.finditer(text)) if w and w not in STOPWORDS]


def _chunk_lines(lines: list[str]) -> list[tuple[str, int | None]]:
    """Group lines into ~PASSAGE_CHARS passages, remembering the first cue timestamp."""
    out: list[tuple[str, int | None]] = []
    buf: list[str] = []
    size = 0
    first: int | None = None
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        cue = CUE_RE.match(line)
        seconds = None
        if cue:
            parts = [int(x) for x in cue.groups()[:3] if x is not None]
            seconds = parts[0] * 60 + parts[1] if len(parts) == 2 else parts[0] * 3600 + parts[1] * 60 + parts[2]
            line = cue.group(4)
        if not buf:
            first = seconds
        buf.append(line)
        size += len(line) + 1
        if size >= PASSAGE_CHARS:
            out.append((" ".join(buf), first))
            buf, size, first = [], 0, None
    if buf:
        out.append((" ".join(buf), first))
    return out


def _source_passages(path: Path) -> list[Passage]:
    record = parse_source_file(path)
    return [
        Passage(path, record["title"], "source", text, seconds, record["video_id"])
        for text, seconds in _chunk_lines(record["transcript"].splitlines())
    ]


def _wiki_passages(path: Path) -> list[Passage]:
    text = path.read_text(encoding="utf-8", errors="replace")
    body = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)
    title_match = re.search(r"^title:\s*\"?(.+?)\"?\s*$", text, re.M)
    title = title_match.group(1) if title_match else path.stem
    return [Passage(path, title, "wiki", chunk, None) for chunk, _ in _chunk_lines(body.splitlines())]


def candidate_files(workspace: Workspace, scope: str = "all") -> list[tuple[Path, str]]:
    files: list[tuple[Path, str]] = []
    if scope in ("all", "sources"):
        files += [(p, "source") for p in workspace.discover_source_files()]
    if scope in ("all", "wiki") and workspace.wiki.exists():
        for folder in (workspace.sources_dir, workspace.entities_dir, workspace.topics_dir):
            if folder.exists():
                files += [(p, "wiki") for p in sorted(folder.glob("*.md"))]
    return files


def search(
    workspace: Workspace, query: str, *, scope: str = "all", limit: int = 10, per_file: int = 1, match: str = "all"
) -> list[Passage]:
    """Rank passages by BM25.

    match="all": a file must contain every query term (predictable lookups).
    match="any": a file must contain at least half the terms (natural-language questions).
    """
    q_terms = terms(query)
    if not q_terms:
        return []
    needed = len(set(q_terms)) if match == "all" else max(1, math.ceil(len(set(q_terms)) / 2))
    passages: list[Passage] = []
    for path, kind in candidate_files(workspace, scope):
        text = path.read_text(encoding="utf-8", errors="replace").casefold()
        if sum(t in text for t in set(q_terms)) < needed:
            continue
        passages += _source_passages(path) if kind == "source" else _wiki_passages(path)
    if not passages:
        return []

    tokenized = [terms(p.title + " " + p.text) for p in passages]
    avg_len = sum(len(t) for t in tokenized) / len(tokenized) or 1
    df = Counter(t for toks in tokenized for t in set(toks) & set(q_terms))
    n = len(passages)
    phrase = " ".join(q_terms)
    for passage, toks in zip(passages, tokenized, strict=True):
        counts = Counter(toks)
        score = 0.0
        for t in set(q_terms):
            tf = counts.get(t, 0)
            if not tf:
                continue
            idf = math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5))
            score += idf * tf * 2.2 / (tf + 1.2 * (0.25 + 0.75 * len(toks) / avg_len))
        if len(q_terms) > 1 and phrase in " ".join(toks):
            score *= 1.5
        passage.score = score

    ranked = sorted((p for p in passages if p.score > 0), key=lambda p: -p.score)
    picked: list[Passage] = []
    seen: Counter = Counter()
    for passage in ranked:
        if seen[passage.path] >= per_file:
            continue
        seen[passage.path] += 1
        picked.append(passage)
        if len(picked) >= limit:
            break
    return picked


def snippet(passage: Passage, query: str, width: int = 220) -> str:
    """A window of the passage centred on the first query term."""
    text = passage.text
    lowered = text.casefold()
    hits = [lowered.find(t) for t in terms(query) if lowered.find(t) >= 0]
    start = max(0, min(hits) - width // 3) if hits else 0
    piece = text[start:start + width].strip()
    return ("..." if start else "") + piece + ("..." if start + width < len(text) else "")


def _with_next(passage: Passage) -> str:
    """The passage plus the one after it in the same file, so answers are not cut at a boundary."""
    siblings = _source_passages(passage.path) if passage.kind == "source" else _wiki_passages(passage.path)
    for i, sibling in enumerate(siblings):
        if sibling.text == passage.text and i + 1 < len(siblings):
            return passage.text + " " + siblings[i + 1].text
    return passage.text


ASK_PROMPT = """Answer the question using ONLY the numbered passages from the user's own sources.

Rules:
- Cite every claim with the passage number in square brackets, like [2].
- If the passages answer only part of the question, answer that part and say briefly what they do not cover.
- If no passage is relevant to the question, reply with exactly: {not_found}
- Do not use outside knowledge. Keep the answer short and direct.

Question: {question}

Passages:
{passages}
"""


def ask(workspace: Workspace, question: str, *, provider: str | None = None, k: int = 6, client=None) -> tuple[str, list[Passage]]:
    """Grounded answer from the top-k passages. Returns (answer, passages cited as [1..k])."""
    passages = search(workspace, question, limit=k, per_file=3, match="any")
    if not passages:
        return NOT_IN_SOURCES, []
    blocks = []
    for i, passage in enumerate(passages, 1):
        where = f" at {passage.stamp}" if passage.stamp else ""
        blocks.append(f"[{i}] {passage.title}{where}\n{_with_next(passage)}")
    if client is None:
        from openwiki.llm import make_client

        client = make_client(provider=provider)
    prompt = ASK_PROMPT.format(not_found=NOT_IN_SOURCES, question=question, passages="\n\n".join(blocks))
    answer = client.generate(prompt, temperature=0.1).strip()
    return answer or NOT_IN_SOURCES, passages
