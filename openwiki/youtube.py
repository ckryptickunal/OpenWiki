"""YouTube discovery and caption extraction.

- Single videos need no API key (title/channel come from YouTube's public oEmbed endpoint).
- Channel and playlist listing use the YouTube Data API v3 (`YOUTUBE_API_KEY`).
- Captions come from `youtube-transcript-api`, optionally through `YOUTUBE_PROXY` (a Tor proxy can rotate its
  circuit on a block via `YOUTUBE_TOR_CONTROL_PORT`).
- With `--asr`, videos without fetchable captions are transcribed locally from audio (openwiki/asr.py).
- `<folder>/_extract_state.json` remembers finished and permanently skipped videos.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from openwiki.env import env_value, require_env
from openwiki.textfmt import format_timed_transcript, write_youtube_file
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
    """Return no_captions | unplayable | ip_blocked | rate_limited | error.

    no_captions and unplayable are permanent: the video is never retried.
    ip_blocked and rate_limited stay retryable on a later run. A 429 is not an IP ban.
    """
    name = type(exc).__name__.lower()
    if name in BLOCKED_ERRORS:
        return "ip_blocked"
    if name in NO_CAPTION_ERRORS:
        return "no_captions"
    if name in UNPLAYABLE_ERRORS:
        return "unplayable"
    message = str(exc).lower()
    if "429" in message or "too many requests" in message or "rate limit" in message:
        return "rate_limited"
    if "blocking requests" in message or "ip blocked" in message:
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



# ---------- Keyless listing with yt-dlp (no YouTube Data API key) ----------

class ListingUnavailable(RuntimeError):
    """Neither a YouTube Data API key nor yt-dlp is available for listing."""


LISTING_HELP = (
    "Listing a channel or playlist needs either YOUTUBE_API_KEY or yt-dlp. "
    "Install yt-dlp for keyless listing: pip install yt-dlp (or brew install yt-dlp)."
)


def ytdlp_available() -> bool:
    try:
        import yt_dlp  # noqa: F401
        return True
    except ImportError:
        return shutil.which("yt-dlp") is not None


class _SilentLogger:
    def debug(self, msg: str) -> None: ...
    def info(self, msg: str) -> None: ...
    def warning(self, msg: str) -> None: ...

    def error(self, msg: str) -> None:
        print(msg, file=sys.stderr)


def _ytdlp_json(url: str) -> dict:
    """Flat listing of a channel/playlist page as yt-dlp JSON (no downloads)."""
    try:
        import yt_dlp
    except ImportError:
        yt_dlp = None
    if yt_dlp is not None:
        options = {
            "extract_flat": "in_playlist", "quiet": True, "no_warnings": True, "skip_download": True,
            "logger": _SilentLogger(),  # yt-dlp otherwise prints notices (e.g. Python version) to stdout
        }
        with yt_dlp.YoutubeDL(options) as ydl:
            return ydl.extract_info(url, download=False)
    binary = shutil.which("yt-dlp")
    if not binary:
        raise ListingUnavailable(LISTING_HELP)
    proc = subprocess.run(
        [binary, "--flat-playlist", "--dump-single-json", "--no-warnings", url],
        capture_output=True, text=True, timeout=600,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"yt-dlp could not list {url}: {proc.stderr.strip()[-300:]}")
    return json.loads(proc.stdout)


def channel_listing_url(channel_input: str) -> str:
    """The uploads tab URL for a channel URL, @handle, or UC... id (newest first)."""
    value = channel_input.strip()
    if re.match(r"^UC[\w-]{22}$", value):
        return f"https://www.youtube.com/channel/{value}/videos"
    if value.startswith("@"):
        return f"https://www.youtube.com/{value}/videos"
    if "youtube.com" in value:
        base = value.split("?")[0].rstrip("/")
        base = re.sub(r"/(videos|featured|streams|shorts|playlists|about)$", "", base)
        return base + "/videos"
    raise ListingUnavailable(
        f"Without YOUTUBE_API_KEY, pass the channel as a URL, @handle, or UC... id (got {channel_input!r})."
    )


def ytdlp_list(url: str) -> tuple[str, list[str]]:
    """(title, video ids) for a channel uploads tab or playlist, in page order."""
    info = _ytdlp_json(url)
    title = info.get("channel") or info.get("uploader") or info.get("title") or ""
    title = re.sub(r"\s+-\s+Videos$", "", title)
    ids: list[str] = []
    for entry in info.get("entries") or []:
        if entry and entry.get("_type") == "playlist":  # a channel page nests tabs
            ids.extend(e["id"] for e in entry.get("entries") or [] if e and e.get("id"))
        elif entry and entry.get("id") and entry.get("ie_key", "Youtube") in ("Youtube", None):
            ids.append(entry["id"])
    seen: set[str] = set()
    return title, [i for i in ids if not (i in seen or seen.add(i))]


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
    api = _transcript_api(proxy)
    chosen = pick_transcript(api.list(video_id), languages or DEFAULT_LANGUAGES)
    transcript = chosen.fetch()
    text = format_timed_transcript(transcript)
    if not text.strip():
        raise RuntimeError("transcript was empty")
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
        "skip_reasons": {},
        "failures": {},
        "stats": {"success": 0, "skipped": 0, "failed": 0},
    }


def _ensure_state_keys(state: dict) -> dict:
    fresh = empty_extract_state()
    for key, value in fresh.items():
        state.setdefault(key, value)
    return state


ASR_FALLBACK_KINDS = {"no_captions", "ip_blocked", "rate_limited"}

FAILURE_HINTS = {
    "ip_blocked": " (YouTube blocked this IP; set YOUTUBE_PROXY, use --asr, or retry later. Not a permanent skip.)",
    "rate_limited": " (rate limited; wait and rerun, or use --limit. Not a permanent skip.)",
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


def new_tor_circuit(control_port: int, host: str = "127.0.0.1") -> bool:
    """Ask a local Tor ControlPort (started with `--CookieAuthentication 0`) for a new circuit (SIGNAL NEWNYM)."""
    import socket

    try:
        with socket.create_connection((host, control_port), timeout=5) as sock:
            sock.sendall(b'AUTHENTICATE ""\r\nSIGNAL NEWNYM\r\nQUIT\r\n')
            reply = b""
            while chunk := sock.recv(256):  # Tor closes the connection after QUIT
                reply += chunk
            return reply.count(b"250 OK") >= 2
    except OSError:
        return False


def extract_one_video(
    video_id: str,
    folder: Path,
    *,
    metadata: dict | None = None,
    youtube=None,
    languages: list[str] | None = None,
    proxy: str | None = None,
    retries: int = 3,
    detail: dict | None = None,
    asr: bool = False,
) -> str:
    """Fetch one video. Returns ok | skip | exists | failed.

    `detail`, when passed, receives `kind` and `reason` for skips and failures.
    With `asr=True`, a video with no captions, or whose captions are blocked or rate limited, is transcribed
    locally from its audio (see openwiki/asr.py).
    """
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

    def _note(kind: str, reason: str) -> None:
        if detail is not None:
            detail["kind"] = kind
            detail["reason"] = reason

    def _write(transcript: FetchedTranscript) -> str:
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

    tor_port_value = (env_value("YOUTUBE_TOR_CONTROL_PORT") or "").strip()
    tor_port = int(tor_port_value) if tor_port_value.isdigit() else None
    last_error: BaseException | None = None
    for attempt in range(retries):
        try:
            return _write(fetch_transcript(video_id, languages=languages, proxy=proxy))
        except Exception as exc:
            last_error = exc
            kind = classify_fetch_error(exc)
            if kind == "unplayable" or (kind == "no_captions" and not asr):
                _note(kind, str(exc).strip().splitlines()[0][:200])
                return "skip"
            if kind == "no_captions":
                break
            # Behind Tor, a fresh circuit usually means a fresh exit IP: retry right away.
            if kind in {"ip_blocked", "rate_limited"} and tor_port and new_tor_circuit(tor_port):
                time.sleep(5)
                continue
            # A 429 gets worse if we hammer it again in the same run.
            if kind == "rate_limited":
                break
            if attempt < retries - 1:
                time.sleep((attempt + 1) * 2)

    kind = classify_fetch_error(last_error) if last_error else "error"
    reason = str(last_error).strip().splitlines()[0] if last_error else "unknown error"
    if asr and kind in ASR_FALLBACK_KINDS:
        from openwiki.asr import transcribe_video

        try:
            return _write(transcribe_video(video_id, languages=languages))
        except Exception as exc:  # noqa: BLE001 - any ASR/download failure is reported, not raised
            reason = f"{reason}; speech-to-text fallback failed: {str(exc).strip().splitlines()[0] if str(exc).strip() else type(exc).__name__}"
            if kind == "no_captions":
                _note(kind, reason[:200])
                return "skip"
    reason = reason[:200]
    _note(kind, reason)
    print(f"  [failed] {video_id}: {kind}{FAILURE_HINTS.get(kind, '')}: {reason}", file=sys.stderr)
    return "failed"


def extract_videos(
    video_ids: list[str],
    folder: Path,
    *,
    channel_name: str | None = None,
    youtube=None,
    languages: list[str] | None = None,
    proxy: str | None = None,
    asr: bool = False,
) -> dict[str, int]:
    """Extract many videos. Skips existing files and videos with no captions."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    state = _ensure_state_keys(load_extract_state(folder))
    skipped = set(state.get("permanent_skip", []))
    reasons = state.get("skip_reasons", {})
    counts = {"ok": 0, "skip": 0, "exists": 0, "failed": 0}

    for video_id in video_ids:
        # --asr can now handle videos skipped earlier for having no captions (or skipped before reasons were kept).
        if video_id in skipped and not (asr and reasons.get(video_id) in (None, "no_captions")):
            counts["skip"] += 1
            continue
        detail: dict = {}
        result = extract_one_video(
            video_id,
            folder,
            metadata={"channel_title": channel_name or folder.name},
            youtube=youtube,
            languages=languages,
            proxy=proxy,
            detail=detail,
            asr=asr,
        )
        counts[result] = counts.get(result, 0) + 1
        if result in {"ok", "exists"}:
            if video_id not in state["done"]:
                state["done"].append(video_id)
            if video_id in state["permanent_skip"]:
                state["permanent_skip"].remove(video_id)
            state["skip_reasons"].pop(video_id, None)
            state["failures"].pop(video_id, None)
        elif result == "skip":
            if video_id not in state["permanent_skip"]:
                state["permanent_skip"].append(video_id)
            if detail.get("kind"):
                state["skip_reasons"][video_id] = detail["kind"]
            state["failures"].pop(video_id, None)
        elif result == "failed" and detail.get("kind"):
            state["failures"][video_id] = {"kind": detail["kind"], "reason": detail.get("reason", "")}
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
    asr: bool = False,
) -> dict:
    """Find uploads not on disk yet (newest first) and extract their captions.

    Uses the YouTube Data API when YOUTUBE_API_KEY is set, otherwise yt-dlp.
    """
    youtube = maybe_youtube_client()
    if youtube is not None:
        channel_id, title = resolve_channel_id(youtube, channel_input)
        folder_name = safe_folder_name(folder or title)
        known = workspace.known_ids_for_folder(workspace.root / folder_name)
        new_ids = discover_new_video_ids(youtube, channel_id, known)
        backend = "youtube-api"
    else:
        if not ytdlp_available():
            raise ListingUnavailable(LISTING_HELP)
        title, ids = ytdlp_list(channel_listing_url(channel_input))
        channel_id = ""
        folder_name = safe_folder_name(folder or title or "channel")
        known = workspace.known_ids_for_folder(workspace.root / folder_name)
        new_ids = [i for i in ids if i not in known]
        backend = "yt-dlp"
    out = workspace.root / folder_name
    if limit is not None:
        new_ids = new_ids[:limit]
    result = {"channel_id": channel_id, "title": title, "folder": folder_name, "listing": backend, "new": new_ids}
    if not dry_run:
        result["counts"] = extract_videos(
            new_ids, out, channel_name=title, youtube=youtube, languages=languages, asr=asr
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
    asr: bool = False,
) -> dict:
    """Extract every video of a playlist that is not on disk yet, in playlist order.

    Uses the YouTube Data API when YOUTUBE_API_KEY is set, otherwise yt-dlp.
    """
    playlist_id = extract_playlist_id(playlist_input)
    out = workspace.root / safe_folder_name(folder)
    known = workspace.known_ids_for_folder(out)
    youtube = maybe_youtube_client()
    ids: list[str] = []
    if youtube is not None:
        for page in iter_playlist_pages(youtube, playlist_id, max_pages=200):
            ids.extend(v["id"] for v in page)
        backend = "youtube-api"
    else:
        if not ytdlp_available():
            raise ListingUnavailable(LISTING_HELP)
        _title, ids = ytdlp_list(f"https://www.youtube.com/playlist?list={playlist_id}")
        backend = "yt-dlp"
    new_ids: list[str] = []
    for vid in ids:
        if vid not in known and vid not in new_ids:
            new_ids.append(vid)
    if limit is not None:
        new_ids = new_ids[:limit]
    result = {"playlist_id": playlist_id, "folder": out.name, "listing": backend, "new": new_ids}
    if not dry_run:
        result["counts"] = extract_videos(
            new_ids, out, channel_name=folder, youtube=youtube, languages=languages, asr=asr
        )
    return result
