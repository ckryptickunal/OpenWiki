"""On-disk source format shared by YouTube transcripts and essays.

Every item becomes a .txt file: a metadata header, a TRANSCRIPT marker, then the body.
Raw files are the source of truth; wiki pages are derived from them.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Any

SEPARATOR = "=" * 60
YOUTUBE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")
TRANSCRIPT_MARKER = "TRANSCRIPT"
CUE_RE = re.compile(r"^\[(\d+):(\d{2})(?::(\d{2}))?\]\s*(.*)$")


def format_cue_timestamp(seconds: float) -> str:
    """Render a caption offset as `m:ss` or `h:mm:ss`."""
    total = max(0, int(seconds))
    hours, rem = divmod(total, 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def format_timed_transcript(snippets) -> str:
    """Readable caption text with a `[m:ss]` prefix on each cue."""
    lines: list[str] = []
    for snippet in snippets:
        text = str(getattr(snippet, "text", "") or "").replace("\n", " ").strip()
        if not text:
            continue
        start = getattr(snippet, "start", None)
        if start is None:
            lines.append(text)
        else:
            lines.append(f"[{format_cue_timestamp(float(start))}] {text}")
    return "\n".join(lines)


def parse_cues(transcript: str) -> list[tuple[int | None, str]]:
    """Split a transcript into (seconds or None, text) cues."""
    cues: list[tuple[int | None, str]] = []
    for raw in (transcript or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        match = CUE_RE.match(line)
        if not match:
            cues.append((None, line))
            continue
        if match.group(3) is None:
            seconds = int(match.group(1)) * 60 + int(match.group(2))
        else:
            seconds = int(match.group(1)) * 3600 + int(match.group(2)) * 60 + int(match.group(3))
        text = match.group(4).strip()
        if text:
            cues.append((seconds, text))
    return cues


def _loose(text: str) -> str:
    folded = re.sub(r"\s+", " ", (text or "").casefold())
    folded = re.sub(r"[^\w\s]", "", folded, flags=re.UNICODE)
    return re.sub(r"\s+", " ", folded).strip()


def locate_in_transcript(transcript: str, needle: str) -> tuple[bool, int | None]:
    """Find `needle` in a transcript. Returns (found, timestamp seconds or None).

    Quotes shorter than a few words are ignored so a common word is not treated as provenance.
    """
    needle_loose = _loose(needle)
    if len(needle_loose) < 12:
        return False, None
    pieces: list[str] = []
    spans: list[tuple[int, int | None]] = []
    cursor = 0
    for seconds, text in parse_cues(transcript):
        piece = _loose(text)
        if not piece:
            continue
        if pieces:
            cursor += 1
        spans.append((cursor, seconds))
        pieces.append(piece)
        cursor += len(piece)
    if not pieces:
        return False, None
    haystack = " ".join(pieces)
    pos = haystack.find(needle_loose)
    if pos < 0:
        return False, None
    stamp: int | None = None
    for start, seconds in spans:
        if start <= pos:
            stamp = seconds
        else:
            break
    return True, stamp


def slugify(value: str, fallback: str = "untitled", max_len: int = 90) -> str:
    """ASCII slug when the text has Latin letters; otherwise keep Unicode letters.

    "Café Société" -> "cafe-societe", "深度学习" -> "深度学习" (not "untitled").
    """
    value = unicodedata.normalize("NFKC", value or "").strip().lower()
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_value).strip("-")
    if not slug:
        kept = "".join(c if unicodedata.category(c)[0] in "LMN" else "-" for c in value)
        slug = re.sub(r"-+", "-", kept).strip("-")
    return slug[:max_len].strip("-") or fallback


def _write_block(fh, body: str) -> None:
    fh.write(f"\n{SEPARATOR}\n")
    fh.write(f"{TRANSCRIPT_MARKER}\n")
    fh.write(f"{SEPARATOR}\n\n")
    fh.write(body if body.endswith("\n") else body + "\n")


def write_source_file(
    path: Path | str,
    *,
    title: str,
    source_id: str,
    body: str,
    channel: str = "Unknown",
    published: str = "Unknown",
    url: str = "",
    extra: dict[str, Any] | None = None,
    description: str = "",
) -> Path:
    """Write a pipeline .txt file. `source_id` is stored as `Video ID` for ingest compatibility."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        fh.write(f"Title: {title}\n")
        fh.write(f"Video ID: {source_id}\n")
        if url:
            fh.write(f"URL: {url}\n")
        fh.write(f"Channel: {channel}\n")
        fh.write(f"Published: {published}\n")
        for key, value in (extra or {}).items():
            if value is None or value == "":
                continue
            fh.write(f"{key}: {value}\n")
        if description:
            fh.write(f"\nDescription:\n{description}\n")
        _write_block(fh, body)
    return path


def write_youtube_file(
    path: Path | str,
    video_id: str,
    metadata: dict,
    *,
    body: str,
    language: str = "English",
    language_code: str = "en",
    is_generated: bool = False,
    snippet_count: int = 0,
) -> Path:
    """Write a YouTube transcript with the standard metadata header."""
    extra: dict[str, Any] = {}
    if metadata.get("duration"):
        extra["Duration"] = metadata.get("duration", "Unknown")
    if metadata.get("view_count"):
        extra["Views"] = metadata.get("view_count", "N/A")
    if metadata.get("like_count"):
        extra["Likes"] = metadata.get("like_count", "N/A")
    tags = metadata.get("tags") or []
    if tags:
        extra["Tags"] = ", ".join(tags[:15])
    extra["Transcript Language"] = f"{language} ({language_code})"
    extra["Auto-generated"] = is_generated
    extra["Snippets"] = snippet_count

    description = metadata.get("description") or ""
    if description:
        description = description[:500]

    return write_source_file(
        path,
        title=metadata.get("title") or "Unknown",
        source_id=video_id,
        body=body,
        channel=metadata.get("channel_title") or metadata.get("channel") or "Unknown",
        published=metadata.get("published_at") or metadata.get("published") or "Unknown",
        url=metadata.get("url") or f"https://www.youtube.com/watch?v={video_id}",
        extra=extra,
        description=description,
    )


def write_essay_file(
    path: Path | str,
    source_id: str,
    title: str,
    date: str,
    channel: str,
    source: str,
    text: str,
) -> Path:
    """Write an essay/article with the standard metadata header."""
    return write_source_file(
        path,
        title=title,
        source_id=source_id,
        body=text,
        channel=channel,
        published=date,
        extra={"Source": source},
    )


def parse_source_file(path: Path | str) -> dict:
    """Parse a source .txt file into {path, video_id, title, metadata, transcript}."""
    path = Path(path)
    text = path.read_text(encoding="utf-8", errors="replace")
    metadata: dict[str, str] = {}

    marker_index = text.find(TRANSCRIPT_MARKER)
    header_text = text[:marker_index] if marker_index != -1 else text[:2000]
    transcript_text = text[marker_index + len(TRANSCRIPT_MARKER) :] if marker_index != -1 else text
    transcript_text = re.sub(r"^=+\s*", "", transcript_text.strip())

    for line in header_text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip().lower().replace(" ", "_")] = value.strip()

    video_id = metadata.get("video_id") or path.stem
    title = metadata.get("title") or path.stem
    return {
        "path": str(path),
        "video_id": video_id,
        "title": title,
        "metadata": metadata,
        "transcript": transcript_text,
    }


def source_url(record: dict) -> str:
    """Prefer an explicit URL, then a Source: http… field, then a YouTube watch URL."""
    metadata = record.get("metadata") or {}
    url = (metadata.get("url") or "").strip()
    if url:
        return url
    source = (metadata.get("source") or "").strip()
    if source.startswith("http"):
        return source
    video_id = record.get("video_id") or ""
    if YOUTUBE_ID_RE.match(video_id):
        return f"https://www.youtube.com/watch?v={video_id}"
    return source
