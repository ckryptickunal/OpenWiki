"""YouTube discovery and caption extraction.

Maps to Founder Book:
  transcriptor.py       — channel resolve, uploads list, header writer
  fetch_transcript.py   — single-video caption fetch
  extract_channel.py    — skip no-captions, extract-state, optional proxy
  auto_sync.py          — newest-first discovery that stops at known IDs
"""

from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import parse_qs, urlparse

from wikiblocks.env import env_value, require_env
from wikiblocks.textfmt import write_youtube_file
from wikiblocks.workspace import Workspace

DISCOVERY_MAX_PAGES = 40
DISCOVERY_STOP_AFTER_KNOWN = 2

PERMANENT_NO_CAPTIONS = (
    "no transcripts",
    "transcriptsdisabled",
    "disabled",
    "no transcript",
)
PERMANENT_UNPLAYABLE = (
    "unplayable",
    "live event",
    "private video",
    "video unavailable",
)


@dataclass
class FetchedTranscript:
    text: str
    language: str = "English"
    language_code: str = "en"
    is_generated: bool = False
    snippet_count: int = 0


def extract_video_id(url_or_id: str) -> str:
    """Extract a video ID from a watch URL, youtu.be link, or bare ID."""
    value = (url_or_id or "").strip()
    if "youtube.com/watch" in value:
        query = parse_qs(urlparse(value).query)
        return query["v"][0]
    if "youtube.com/shorts/" in value:
        return value.split("youtube.com/shorts/")[1].split("?")[0].split("/")[0]
    if "youtu.be/" in value:
        return value.split("youtu.be/")[1].split("?")[0]
    return value


def parse_url_file(filepath: Path | str) -> list[str]:
    """One YouTube URL or ID per line. Blank lines and # comments are ignored."""
    ids: list[str] = []
    for line in Path(filepath).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        ids.append(extract_video_id(line))
    return ids


def classify_fetch_error(exc: BaseException) -> str:
    """Return no_captions | unplayable | ip_blocked | error."""
    message = str(exc).lower()
    name = type(exc).__name__.lower()
    blob = f"{name} {message}"
    if any(marker in blob for marker in PERMANENT_NO_CAPTIONS):
        return "no_captions"
    if any(marker in blob for marker in PERMANENT_UNPLAYABLE):
        return "unplayable"
    if "429" in blob or "blocked" in blob or "ipblocked" in blob:
        return "ip_blocked"
    return "error"


def select_new_ids(
    pages: Iterable[list[str]],
    known: set[str],
    *,
    stop_after_known_pages: int = DISCOVERY_STOP_AFTER_KNOWN,
) -> list[str]:
    """Newest-first discovery: keep unseen IDs, stop after N all-known pages."""
    new_ids: list[str] = []
    consecutive_known = 0
    for page in pages:
        page_new = 0
        for vid in page:
            if vid in known or vid in new_ids:
                continue
            new_ids.append(vid)
            page_new += 1
        if page_new == 0:
            consecutive_known += 1
            if consecutive_known >= stop_after_known_pages:
                break
        else:
            consecutive_known = 0
    return new_ids


def get_youtube_service():
    api_key = require_env("YOUTUBE_API_KEY", "channel discovery and video metadata")
    from googleapiclient.discovery import build

    return build("youtube", "v3", developerKey=api_key)


def resolve_channel_id(youtube, channel_input: str) -> tuple[str, str]:
    """Resolve a channel ID, URL, @handle, or name to (channel_id, title)."""
    if re.match(r"^UC[\w-]{22}$", channel_input):
        resp = youtube.channels().list(part="snippet", id=channel_input).execute()
        if resp.get("items"):
            return channel_input, resp["items"][0]["snippet"]["title"]

    if "youtube.com" in channel_input:
        parsed = urlparse(channel_input)
        path = parsed.path
        if "/channel/" in path:
            channel_id = path.split("/channel/")[1].split("/")[0]
            resp = youtube.channels().list(part="snippet", id=channel_id).execute()
            if resp.get("items"):
                return channel_id, resp["items"][0]["snippet"]["title"]
        if "/@" in path:
            handle = path.split("/@")[1].split("/")[0]
            resp = youtube.search().list(
                part="snippet", q=handle, type="channel", maxResults=1
            ).execute()
            if resp.get("items"):
                snippet = resp["items"][0]["snippet"]
                return snippet["channelId"], snippet["channelTitle"]
        if "/c/" in path or "/user/" in path:
            name = path.split("/")[-1]
            resp = youtube.search().list(
                part="snippet", q=name, type="channel", maxResults=1
            ).execute()
            if resp.get("items"):
                snippet = resp["items"][0]["snippet"]
                return snippet["channelId"], snippet["channelTitle"]

    query = channel_input[1:] if channel_input.startswith("@") else channel_input
    resp = youtube.search().list(
        part="snippet", q=query, type="channel", maxResults=1
    ).execute()
    if resp.get("items"):
        snippet = resp["items"][0]["snippet"]
        return snippet["channelId"], snippet["channelTitle"]
    raise RuntimeError(f"Could not find channel for {channel_input!r}")


def get_video_metadata(youtube, video_id: str) -> dict:
    resp = youtube.videos().list(part="snippet,contentDetails,statistics", id=video_id).execute()
    if not resp.get("items"):
        return {}
    item = resp["items"][0]
    snippet = item["snippet"]
    stats = item.get("statistics", {})
    return {
        "title": snippet.get("title", "Unknown"),
        "published_at": snippet.get("publishedAt", "Unknown"),
        "description": snippet.get("description", ""),
        "channel_title": snippet.get("channelTitle", ""),
        "duration": item.get("contentDetails", {}).get("duration", "Unknown"),
        "view_count": stats.get("viewCount", "N/A"),
        "like_count": stats.get("likeCount", "N/A"),
        "tags": snippet.get("tags", []),
    }


def iter_upload_pages(youtube, channel_id: str, *, max_pages: int = DISCOVERY_MAX_PAGES):
    resp = youtube.channels().list(part="contentDetails", id=channel_id).execute()
    items = resp.get("items", [])
    if not items:
        return
    uploads = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
    page_token = None
    for _ in range(max_pages):
        playlist = youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=uploads,
            maxResults=50,
            pageToken=page_token,
        ).execute()
        page: list[dict] = []
        for item in playlist.get("items", []):
            snippet = item.get("snippet", {})
            video_id = (
                item.get("contentDetails", {}).get("videoId")
                or snippet.get("resourceId", {}).get("videoId")
            )
            if not video_id:
                continue
            page.append({
                "id": video_id,
                "title": snippet.get("title", "Unknown"),
                "published_at": snippet.get("publishedAt", "Unknown"),
                "description": snippet.get("description", ""),
                "channel_title": snippet.get("channelTitle", ""),
            })
        yield page
        page_token = playlist.get("nextPageToken")
        if not page_token:
            break


def get_all_videos(youtube, channel_id: str) -> list[dict]:
    videos: list[dict] = []
    for page in iter_upload_pages(youtube, channel_id):
        videos.extend(page)
    return videos


def discover_new_video_ids(youtube, channel_id: str, known: set[str]) -> list[str]:
    pages = ([item["id"] for item in page] for page in iter_upload_pages(youtube, channel_id))
    return select_new_ids(pages, known)


def _transcript_api(proxy: str | None = None):
    from youtube_transcript_api import YouTubeTranscriptApi

    proxy = proxy or env_value("YOUTUBE_PROXY")
    if not proxy:
        return YouTubeTranscriptApi()
    from youtube_transcript_api.proxies import GenericProxyConfig

    return YouTubeTranscriptApi(proxy_config=GenericProxyConfig(https_url=proxy))


def fetch_transcript(
    video_id: str,
    *,
    languages: list[str] | None = None,
    proxy: str | None = None,
) -> FetchedTranscript:
    from youtube_transcript_api.formatters import TextFormatter

    api = _transcript_api(proxy)
    transcript = api.fetch(video_id, languages=languages or ["en"])
    text = TextFormatter().format_transcript(transcript)
    return FetchedTranscript(
        text=text,
        language=getattr(transcript, "language", "English"),
        language_code=getattr(transcript, "language_code", "en"),
        is_generated=bool(getattr(transcript, "is_generated", False)),
        snippet_count=len(transcript),
    )


def empty_extract_state() -> dict:
    return {
        "done": [],
        "permanent_skip": [],
        "stats": {"success": 0, "skipped": 0, "failed": 0},
    }


def load_extract_state(folder: Path) -> dict:
    path = folder / "_extract_state.json"
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, ValueError):
            pass
    return empty_extract_state()


def save_extract_state(folder: Path, state: dict) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "_extract_state.json").write_text(
        json.dumps(state, indent=2), encoding="utf-8"
    )


def extract_one_video(
    video_id: str,
    folder: Path,
    *,
    metadata: dict | None = None,
    youtube=None,
    languages: list[str] | None = None,
    proxy: str | None = None,
    retries: int = 3,
) -> str:
    """Fetch one video. Returns ok | skip | exists | failed."""
    folder.mkdir(parents=True, exist_ok=True)
    filepath = folder / f"{video_id}.txt"
    if filepath.exists():
        return "exists"

    meta = dict(metadata or {})
    if youtube:
        try:
            fetched = get_video_metadata(youtube, video_id)
            if fetched:
                meta.update(fetched)
        except Exception:
            pass
    meta.setdefault("title", "Unknown")
    meta.setdefault("channel_title", folder.name)

    last_kind = "error"
    for attempt in range(retries):
        try:
            transcript = fetch_transcript(video_id, languages=languages, proxy=proxy)
            write_youtube_file(
                filepath,
                video_id,
                meta,
                body=transcript.text,
                language=transcript.language,
                language_code=transcript.language_code,
                is_generated=transcript.is_generated,
                snippet_count=transcript.snippet_count,
            )
            return "ok"
        except Exception as exc:
            last_kind = classify_fetch_error(exc)
            if last_kind in {"no_captions", "unplayable"}:
                return "skip"
            if attempt < retries - 1:
                time.sleep((attempt + 1) * 2)
    return "failed" if last_kind != "skip" else "skip"


def extract_videos(
    video_ids: list[str],
    folder: Path,
    *,
    channel_name: str | None = None,
    youtube=None,
    proxy: str | None = None,
) -> dict[str, int]:
    """Extract many videos. Skips existing files and videos with no captions."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    state = load_extract_state(folder)
    done = set(state.get("done", []))
    skipped = set(state.get("permanent_skip", []))
    counts = {"ok": 0, "skip": 0, "exists": 0, "failed": 0}

    for video_id in video_ids:
        if video_id in skipped:
            counts["skip"] += 1
            continue
        result = extract_one_video(
            video_id,
            folder,
            metadata={"channel_title": channel_name or folder.name},
            youtube=youtube,
            proxy=proxy,
        )
        counts[result] = counts.get(result, 0) + 1
        if result in {"ok", "exists"}:
            if video_id not in state["done"]:
                state["done"].append(video_id)
        elif result == "skip":
            if video_id not in state["permanent_skip"]:
                state["permanent_skip"].append(video_id)
        state["stats"]["success"] = len(state["done"])
        state["stats"]["skipped"] = len(state["permanent_skip"])
        save_extract_state(folder, state)

    return counts


def maybe_youtube_client():
    if not env_value("YOUTUBE_API_KEY"):
        return None
    try:
        return get_youtube_service()
    except Exception:
        return None


def safe_folder_name(name: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', "_", name).strip() or "channel"


def extract_channel(
    workspace: Workspace,
    channel_input: str,
    *,
    folder: str | None = None,
    dry_run: bool = False,
    limit: int | None = None,
) -> dict:
    """Resolve a channel, discover new videos, extract captions for the missing ones."""
    youtube = get_youtube_service()
    channel_id, title = resolve_channel_id(youtube, channel_input)
    folder_name = folder or safe_folder_name(title)
    out = workspace.root / folder_name
    known = workspace.known_ids_for_folder(out)
    videos = get_all_videos(youtube, channel_id)
    remaining = [v for v in videos if v["id"] not in known]
    if limit is not None:
        remaining = remaining[:limit]
    if dry_run:
        return {
            "channel_id": channel_id,
            "title": title,
            "folder": folder_name,
            "total": len(videos),
            "new": [v["id"] for v in remaining],
            "extracted": 0,
        }
    counts = extract_videos(
        [v["id"] for v in remaining],
        out,
        channel_name=title,
        youtube=youtube,
        proxy=os.getenv("YOUTUBE_PROXY") or None,
    )
    return {
        "channel_id": channel_id,
        "title": title,
        "folder": folder_name,
        "total": len(videos),
        "new": [v["id"] for v in remaining],
        "counts": counts,
    }
