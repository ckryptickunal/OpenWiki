"""YouTube discovery and caption extraction.

- Single videos need no API key (title/channel come from YouTube's public oEmbed endpoint).
- Channel and playlist listing use the YouTube Data API v3 (`YOUTUBE_API_KEY`).
- Captions come from `youtube-transcript-api`, optionally through `YOUTUBE_PROXY`.
- `<folder>/_extract_state.json` remembers finished and permanently skipped videos.
"""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.parse
import urllib.request
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from openwiki.env import env_value, require_env
from openwiki.textfmt import write_youtube_file
from openwiki.workspace import Workspace

DISCOVERY_MAX_PAGES = 40
DISCOVERY_STOP_AFTER_KNOWN = 2
DEFAULT_LANGUAGES = ["en"]

# youtube-transcript-api exception class names, lower-cased.
NO_CAPTION_ERRORS = {"transcriptsdisabled", "nocaptionsavailable"}
UNPLAYABLE_ERRORS = {"videounavailable", "videounplayable", "agerestricted", "invalidvideoid"}
BLOCKED_ERRORS = {"requestblocked", "ipblocked"}

# Message fallbacks for exceptions raised by other layers.
PERMANENT_NO_CAPTIONS = ("subtitles are disabled", "transcripts disabled", "no captions")
PERMANENT_UNPLAYABLE = ("unplayable", "live event", "private video", "video unavailable")


class NoCaptionsAvailable(Exception):
    """The video lists no caption tracks at all."""


@dataclass
class FetchedTranscript:
    text: str
    language: str = "English"
    language_code: str = "en"
    is_generated: bool = False
    snippet_count: int = 0


def extract_video_id(url_or_id: str) -> str:
    """Extract a video ID from a watch URL, youtu.be link, shorts/live/embed URL, or bare ID."""
    value = (url_or_id or "").strip()
    parsed = urlparse(value)
    if parsed.netloc.endswith("youtu.be"):
        return parsed.path.lstrip("/").split("/")[0]
    if "youtube.com" in parsed.netloc:
        query = parse_qs(parsed.query)
        if "v" in query:
            return query["v"][0]
        for prefix in ("/shorts/", "/live/", "/embed/"):
            if parsed.path.startswith(prefix):
                return parsed.path[len(prefix):].split("/")[0]
    return value


def extract_playlist_id(url_or_id: str) -> str:
    """Return the `list=` parameter of a playlist URL, or the input unchanged."""
    value = (url_or_id or "").strip()
    query = parse_qs(urlparse(value).query)
    return query["list"][0] if "list" in query else value


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
    """Return no_captions | unplayable | ip_blocked | error.

    no_captions and unplayable are permanent: the video is never retried.
    Anything else (blocks, network errors) stays retryable on the next run.
    """
    name = type(exc).__name__.lower()
    if name in BLOCKED_ERRORS:
        return "ip_blocked"
    if name in NO_CAPTION_ERRORS:
        return "no_captions"
    if name in UNPLAYABLE_ERRORS:
        return "unplayable"
    message = str(exc).lower()
    if "429" in message or "blocking requests" in message or "ip blocked" in message:
        return "ip_blocked"
    if any(marker in message for marker in PERMANENT_NO_CAPTIONS):
        return "no_captions"
    if any(marker in message for marker in PERMANENT_UNPLAYABLE):
        return "unplayable"
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
    api_key = require_env("YOUTUBE_API_KEY", "channel/playlist discovery and video metadata")
    from googleapiclient.discovery import build

    return build("youtube", "v3", developerKey=api_key, cache_discovery=False)


def _channel_by(youtube, **kwargs) -> tuple[str, str] | None:
    resp = youtube.channels().list(part="snippet", **kwargs).execute()
    if resp.get("items"):
        item = resp["items"][0]
        return item["id"], item["snippet"]["title"]
    return None


def _search_channel(youtube, query: str) -> tuple[str, str] | None:
    resp = youtube.search().list(part="snippet", q=query, type="channel", maxResults=1).execute()
    if resp.get("items"):
        snippet = resp["items"][0]["snippet"]
        return snippet["channelId"], snippet["channelTitle"]
    return None


def resolve_channel_id(youtube, channel_input: str) -> tuple[str, str]:
    """Resolve a channel ID, URL, @handle, or name to (channel_id, title).

    IDs and handles use channels.list (1 quota unit). Only free-text names fall
    back to search (100 units).
    """
    value = channel_input.strip()
    path = urlparse(value).path if "youtube.com" in value else ""

    channel_id = None
    if re.match(r"^UC[\w-]{22}$", value):
        channel_id = value
    elif "/channel/" in path:
        channel_id = path.split("/channel/")[1].split("/")[0]
    if channel_id:
        found = _channel_by(youtube, id=channel_id)
        if found:
            return found

    handle = None
    if "/@" in path:
        handle = path.split("/@")[1].split("/")[0]
    elif value.startswith("@"):
        handle = value[1:]
    if handle:
        found = _channel_by(youtube, forHandle=handle)
        if found:
            return found

    if "/user/" in path:
        found = _channel_by(youtube, forUsername=path.split("/user/")[1].split("/")[0])
        if found:
            return found

    query = handle or (path.rstrip("/").split("/")[-1] if path else value)
    found = _search_channel(youtube, query)
    if found:
        return found
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


def get_oembed_metadata(video_id: str, timeout: int = 15) -> dict:
    """Title and channel name from YouTube's public oEmbed endpoint. No API key."""
    watch = f"https://www.youtube.com/watch?v={video_id}"
    url = "https://www.youtube.com/oembed?" + urllib.parse.urlencode({"url": watch, "format": "json"})
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return {
        "title": data.get("title") or "Unknown",
        "channel_title": data.get("author_name") or "",
    }


def iter_playlist_pages(youtube, playlist_id: str, *, max_pages: int = DISCOVERY_MAX_PAGES):
    """Yield pages (lists of dicts) of a playlist, in playlist order."""
    page_token = None
    for _ in range(max_pages):
        playlist = youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=playlist_id,
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
                "channel_title": snippet.get("channelTitle", ""),
            })
        yield page
        page_token = playlist.get("nextPageToken")
        if not page_token:
            break


def uploads_playlist_id(youtube, channel_id: str) -> str | None:
    resp = youtube.channels().list(part="contentDetails", id=channel_id).execute()
    items = resp.get("items", [])
    if not items:
        return None
    return items[0]["contentDetails"]["relatedPlaylists"]["uploads"]


def iter_upload_pages(youtube, channel_id: str, *, max_pages: int = DISCOVERY_MAX_PAGES):
    """Yield pages of a channel's uploads, newest first."""
    uploads = uploads_playlist_id(youtube, channel_id)
    if uploads:
        yield from iter_playlist_pages(youtube, uploads, max_pages=max_pages)


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

    return YouTubeTranscriptApi(proxy_config=GenericProxyConfig(http_url=proxy, https_url=proxy))


def pick_transcript(transcript_list, languages: list[str]):
    """Preferred language first; otherwise the first manual track, then the first generated one."""
    try:
        return transcript_list.find_transcript(languages)
    except Exception as exc:
        if type(exc).__name__ != "NoTranscriptFound":
            raise
    for transcript in transcript_list:
        return transcript
    raise NoCaptionsAvailable("no captions")


def fetch_transcript(
    video_id: str,
    *,
    languages: list[str] | None = None,
    proxy: str | None = None,
) -> FetchedTranscript:
    from youtube_transcript_api.formatters import TextFormatter

    api = _transcript_api(proxy)
    chosen = pick_transcript(api.list(video_id), languages or DEFAULT_LANGUAGES)
    transcript = chosen.fetch()
    return FetchedTranscript(
        text=TextFormatter().format_transcript(transcript),
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
    try:
        fetched = get_video_metadata(youtube, video_id) if youtube else get_oembed_metadata(video_id)
        meta.update({k: v for k, v in fetched.items() if v})
    except Exception:
        pass
    meta.setdefault("title", "Unknown")
    meta.setdefault("channel_title", folder.name)

    last_error: BaseException | None = None
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
            last_error = exc
            if classify_fetch_error(exc) in {"no_captions", "unplayable"}:
                return "skip"
            if attempt < retries - 1:
                time.sleep((attempt + 1) * 2)

    kind = classify_fetch_error(last_error) if last_error else "error"
    hint = " (set YOUTUBE_PROXY, see README)" if kind == "ip_blocked" else ""
    reason = str(last_error).strip().splitlines()[0] if last_error else "unknown error"
    print(f"  [failed] {video_id}: {kind}{hint}: {reason[:200]}", file=sys.stderr)
    return "failed"


def extract_videos(
    video_ids: list[str],
    folder: Path,
    *,
    channel_name: str | None = None,
    youtube=None,
    languages: list[str] | None = None,
    proxy: str | None = None,
) -> dict[str, int]:
    """Extract many videos. Skips existing files and videos with no captions."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    state = load_extract_state(folder)
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
            languages=languages,
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
        state["stats"]["failed"] = counts["failed"]
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
    languages: list[str] | None = None,
) -> dict:
    """Resolve a channel, find uploads not on disk yet (newest first), extract their captions."""
    youtube = get_youtube_service()
    channel_id, title = resolve_channel_id(youtube, channel_input)
    folder_name = safe_folder_name(folder or title)
    out = workspace.root / folder_name
    new_ids = discover_new_video_ids(youtube, channel_id, workspace.known_ids_for_folder(out))
    if limit is not None:
        new_ids = new_ids[:limit]
    result = {"channel_id": channel_id, "title": title, "folder": folder_name, "new": new_ids}
    if not dry_run:
        result["counts"] = extract_videos(
            new_ids, out, channel_name=title, youtube=youtube, languages=languages
        )
    return result


def extract_playlist(
    workspace: Workspace,
    playlist_input: str,
    *,
    folder: str,
    dry_run: bool = False,
    limit: int | None = None,
    languages: list[str] | None = None,
) -> dict:
    """Extract every video of a playlist that is not on disk yet, in playlist order."""
    youtube = get_youtube_service()
    playlist_id = extract_playlist_id(playlist_input)
    out = workspace.root / safe_folder_name(folder)
    known = workspace.known_ids_for_folder(out)
    new_ids: list[str] = []
    for page in iter_playlist_pages(youtube, playlist_id, max_pages=200):
        new_ids.extend(v["id"] for v in page if v["id"] not in known and v["id"] not in new_ids)
    if limit is not None:
        new_ids = new_ids[:limit]
    result = {"playlist_id": playlist_id, "folder": out.name, "new": new_ids}
    if not dry_run:
        result["counts"] = extract_videos(
            new_ids, out, channel_name=folder, youtube=youtube, languages=languages
        )
    return result
