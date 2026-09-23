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
