"""Command-line interface for OpenWiki."""

from __future__ import annotations

import argparse
import json
import sys
import warnings
from pathlib import Path

from openwiki import __version__
from openwiki.env import load_dotenv_file
from openwiki.workspace import Workspace


def _workspace(args) -> Workspace:
    return Workspace.resolve(getattr(args, "root", None))


def _languages(args) -> list[str] | None:
    value = getattr(args, "lang", None)
    return [code.strip() for code in value.split(",") if code.strip()] if value else None


def cmd_init(args) -> int:
    from openwiki.templates import SCHEMA_MD, SOURCES_EXAMPLE, WORKSPACE_GITIGNORE

    ws = _workspace(args)
    ws.root.mkdir(parents=True, exist_ok=True)
    ws.ensure_dirs()
    for path, content in [
        (ws.sources_config, SOURCES_EXAMPLE),
        (ws.schema_path, SCHEMA_MD),
        (ws.root / ".gitignore", WORKSPACE_GITIGNORE),
    ]:
        if not path.exists():
            path.write_text(content, encoding="utf-8")
            print(f"Wrote {path}")
    print(f"Workspace ready at {ws.root}")
    print("Next: edit sources.json, add API keys to .env, then run `openwiki sync`.")
    return 0


def cmd_youtube(args) -> int:
    from openwiki.youtube import (
        extract_channel,
        extract_one_video,
        extract_playlist,
        extract_video_id,
        extract_videos,
        maybe_youtube_client,
        parse_url_file,
        safe_folder_name,
    )

    ws = _workspace(args)
    languages = _languages(args)

    if args.channel or args.playlist:
        if args.channel:
            result = extract_channel(
                ws, args.channel, folder=args.folder, dry_run=args.dry_run,
                limit=args.limit, languages=languages,
            )
        else:
            if not args.folder:
                print("--folder is required with --playlist", file=sys.stderr)
                return 2
            result = extract_playlist(
                ws, args.playlist, folder=args.folder, dry_run=args.dry_run,
                limit=args.limit, languages=languages,
            )
        new = result.pop("new", [])
        print(json.dumps(result | {"new_count": len(new)}, indent=2))
        if args.dry_run:
            for vid in new[:20]:
                print(f"  would extract https://www.youtube.com/watch?v={vid}")
            return 0
        return 0 if result["counts"]["failed"] == 0 else 1

    youtube = maybe_youtube_client()
    if args.urls_file:
        if not args.folder:
            print("--folder is required with --urls-file", file=sys.stderr)
            return 2
        ids = parse_url_file(args.urls_file)
        if args.limit:
            ids = ids[: args.limit]
        folder = ws.root / safe_folder_name(args.folder)
        if args.dry_run:
            print(f"would extract {len(ids)} video(s) into {folder}")
            return 0
        counts = extract_videos(ids, folder, channel_name=args.folder, youtube=youtube, languages=languages)
        print(f"ok={counts['ok']} exists={counts['exists']} skip={counts['skip']} failed={counts['failed']}")
        return 0 if counts["failed"] == 0 else 1

    if not args.video:
        print("Pass a video URL/ID, --channel, --playlist, or --urls-file", file=sys.stderr)
        return 2
    video_id = extract_video_id(args.video)
    folder = ws.root / safe_folder_name(args.folder or "Videos")
    target = folder / f"{video_id}.txt"
    if args.dry_run:
        print(f"would extract {video_id} into {target}")
        return 0
    result = extract_one_video(video_id, folder, youtube=youtube, languages=languages)
    if result == "skip":
        print(f"SKIP {video_id} (no captions or unplayable)")
        return 0
    if result in {"ok", "exists"}:
        print(f"{'WROTE' if result == 'ok' else 'EXISTS'} {target}")
        return 0
    print(f"FAILED {video_id}", file=sys.stderr)
    return 1


def cmd_essay(args) -> int:
    from openwiki.essays import extract_title, fetch_url, write_article_from_html

    ws = _workspace(args)

    if args.url:
        folder = ws.root / (args.folder or "Articles")
        html_text = Path(args.html_file).read_text(encoding="utf-8") if args.html_file else fetch_url(args.url)
        title = args.title or extract_title(html_text) or args.url.rstrip("/").split("/")[-1].replace("-", " ")
        if args.dry_run:
            print(f"would write article {title!r} into {folder}")
            return 0
        folder.mkdir(parents=True, exist_ok=True)
        path = write_article_from_html(
            html_text,
            folder=folder,
            title=title,
            url=args.url,
            channel=args.channel or f"{args.folder or 'Articles'} (web)",
            prefix=args.id_prefix,
            min_chars=args.min_chars,
        )
        if path is None:
            print("SKIP (article text shorter than --min-chars)", file=sys.stderr)
            return 1
        print(f"WROTE {path}")
        return 0

    sources = ws.load_sources_config().get("essay_sources", [])
    if args.source:
        sources = [s for s in sources if s.get("name", "").lower() == args.source.lower()]
    if not sources:
        print("No matching essay_sources in sources.json (run `openwiki init`).", file=sys.stderr)
        return 1

    total_created = total_failed = 0
    for source in sources:
        created, failed = _run_essay_source(ws, source, dry_run=args.dry_run, min_chars=args.min_chars, limit=args.limit)
        total_created += created
        total_failed += failed
    if not args.dry_run:
        print(f"NEW ESSAYS: {total_created} created, {total_failed} skipped/failed")
    return 0


def _run_essay_source(ws: Workspace, source: dict, *, dry_run: bool, min_chars: int, limit: int | None = None) -> tuple[int, int]:
    from openwiki.essays import fetch_source

    print(f"Essays: {source.get('name')} ({source.get('kind', 'generic')})")
    try:
        created, failed, new = fetch_source(source, ws.root, dry_run=dry_run, min_chars=min_chars, limit=limit)
    except Exception as exc:
        print(f"  [warn] {exc}", file=sys.stderr)
        return 0, 0
    if dry_run:
        print(f"  {len(new)} new")
        for essay in new[:20]:
            print(f"    {essay['title']}  {essay['url']}")
        return 0, 0
    print(f"  created={created} skipped_or_failed={failed}")
    return created, failed


def cmd_text(args) -> int:
    from openwiki.essays import import_text_file

    ws = _workspace(args)
    folder = ws.root / (args.folder or "Notes")
    written = []
    for name in args.files:
        path = Path(name).expanduser()
        if not path.is_file():
            print(f"Not a file: {path}", file=sys.stderr)
            return 2
        written.append(import_text_file(
            path, folder, title=args.title if len(args.files) == 1 else None,
            url=args.url or "", prefix=args.id_prefix,
        ))
    for path in written:
        print(f"WROTE {path}")
    return 0


def _ingest(ws: Workspace, paths: list[Path], *, analysis=None, force=False, max_chars=120_000, provider=None) -> int:
    from openwiki.llm import LLMNotConfigured
    from openwiki.wiki import ingest_paths

    if not paths:
        print("No source .txt files found.")
        return 0

    def report(rel: str, exc: Exception) -> None:
        print(f"  [failed] {rel}: {exc}", file=sys.stderr)

    try:
        counts = ingest_paths(
            paths, ws, force=force, analysis=analysis, max_chars=max_chars,
            provider=provider, on_error=report,
        )
    except LLMNotConfigured as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(f"processed={counts['processed']} skipped={counts['skipped']} failed={counts['failed']}")
    if counts["failed"]:
        print(f"Failures are listed in {ws.rel(ws.failures_path)}", file=sys.stderr)
    return 0 if counts["failed"] == 0 else 1


def cmd_ingest(args) -> int:
    ws = _workspace(args)
    analysis = None
    if args.analysis_file:
        analysis = json.loads(Path(args.analysis_file).read_text(encoding="utf-8"))
    if args.file:
        paths = [Path(args.file).expanduser()]
    else:
        paths = ws.discover_source_files(args.folder)
        if args.limit:
            paths = paths[: args.limit]
    return _ingest(ws, paths, analysis=analysis, force=args.force, max_chars=args.max_chars, provider=args.provider)


def cmd_sync(args) -> int:
    """Pull every source in sources.json, then ingest whatever is new."""
    from openwiki.env import env_value
    from openwiki.youtube import extract_channel

    ws = _workspace(args)
    config = ws.load_sources_config()
    channels, essay_sources = config["youtube_channels"], config["essay_sources"]
    if not channels and not essay_sources:
        print("sources.json has no youtube_channels or essay_sources (run `openwiki init`).", file=sys.stderr)
        return 1

    failed = 0
    if channels and not env_value("YOUTUBE_API_KEY"):
        print(f"Skipping {len(channels)} YouTube channel(s): set YOUTUBE_API_KEY to list channel uploads.", file=sys.stderr)
        channels = []
    for channel in channels:
        target = channel.get("channel_id") or channel.get("query") or channel.get("name")
        print(f"YouTube: {channel.get('name', target)}")
        try:
            result = extract_channel(
                ws, target, folder=channel.get("folder") or channel.get("name"),
                dry_run=args.dry_run, limit=args.limit, languages=_languages(args),
            )
        except Exception as exc:
            print(f"  [warn] {exc}", file=sys.stderr)
            failed += 1
            continue
        if args.dry_run:
            print(f"  {len(result['new'])} new")
        else:
            counts = result["counts"]
            failed += counts["failed"]
            print(f"  ok={counts['ok']} skip={counts['skip']} failed={counts['failed']}")

    for source in essay_sources:
        _run_essay_source(ws, source, dry_run=args.dry_run, min_chars=args.min_chars, limit=args.limit)

    if args.dry_run or args.no_ingest:
        return 0 if failed == 0 else 1
    code = _ingest(ws, ws.discover_source_files(), provider=args.provider)
    return code if code else (0 if failed == 0 else 1)


def cmd_lint(args) -> int:
    from openwiki.lint import run_lint
    from openwiki.llm import LLMNotConfigured

    ws = _workspace(args)
    try:
        report, text = run_lint(ws, fix_index=args.fix_index, save=args.save, review=args.review, provider=args.provider)
    except LLMNotConfigured as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(text)
    if args.strict and (report["missing_links"] or report["missing_frontmatter"]):
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--root", default=argparse.SUPPRESS,
        help="Workspace directory (default: $OPENWIKI_ROOT or the current directory).",
    )

    parser = argparse.ArgumentParser(
        prog="openwiki",
        parents=[common],
        description=(
            "Turn YouTube videos, playlists, channels, blogs, and notes into a linked "
            "Markdown wiki (Obsidian-compatible) with an LLM."
        ),
        epilog="Docs: https://github.com/ckryptickunal/OpenWiki",
    )
    parser.add_argument("--version", action="version", version=f"openwiki {__version__}")
    sub = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")

    def add(name: str, help_text: str, func):
        cmd = sub.add_parser(name, parents=[common], help=help_text, description=help_text)
        cmd.set_defaults(func=func)
        return cmd

    add("init", "Create a workspace: wiki/ folders, sources.json, schema, .gitignore.", cmd_init)

    yt = add("youtube", "Download captions for a video, URL list, playlist, or channel.", cmd_youtube)
    yt.add_argument("video", nargs="?", help="YouTube URL or video ID.")
    yt.add_argument("--channel", help="Channel URL, @handle, name, or UC... id (needs YOUTUBE_API_KEY).")
    yt.add_argument("--playlist", help="Playlist URL or id (needs YOUTUBE_API_KEY).")
    yt.add_argument("--urls-file", help="File with one YouTube URL per line.")
    yt.add_argument("--folder", help="Output folder under the workspace (default: Videos or channel title).")
    yt.add_argument("--lang", help="Preferred caption languages, comma-separated (default: en, then any).")
    yt.add_argument("--limit", type=int, help="Max new videos to extract.")
    yt.add_argument("--dry-run", action="store_true")

    essay = add("essay", "Extract one article URL, or every new article from sources.json.", cmd_essay)
    essay.add_argument("--url", help="Single article URL.")
    essay.add_argument("--html-file", help="Saved HTML file to use instead of fetching --url.")
    essay.add_argument("--title", help="Title for a single article (default: taken from the page).")
    essay.add_argument("--folder", help="Output folder (single article default: Articles).")
    essay.add_argument("--channel", help="Author/site label written into the header.")
    essay.add_argument("--id-prefix", default="essay")
    essay.add_argument("--source", help="Only this essay_sources[].name from sources.json.")
    essay.add_argument("--min-chars", type=int, default=400, help="Skip pages with less text (default: 400).")
    essay.add_argument("--limit", type=int, help="Max new articles per source.")
    essay.add_argument("--dry-run", action="store_true")

    text = add("text", "Add local .txt, .md, or .html files (notes, transcripts, exports).", cmd_text)
    text.add_argument("files", nargs="+", help="One or more local files.")
    text.add_argument("--folder", help="Output folder (default: Notes).")
    text.add_argument("--title", help="Title (single file only; default: first # heading or filename).")
    text.add_argument("--url", help="Original URL, if any.")
    text.add_argument("--id-prefix", default="note")

    ingest = add("ingest", "Build wiki pages from .txt sources with an LLM or analysis JSON.", cmd_ingest)
    ingest.add_argument("--file", help="Single source .txt file.")
    ingest.add_argument("--folder", help="Only this source folder.")
    ingest.add_argument("--all", action="store_true", help="Every source folder (the default).")
    ingest.add_argument("--analysis-file", help="Use this analysis JSON instead of calling an LLM.")
    ingest.add_argument("--provider", choices=["gemini", "openai"], help="Override LLM_PROVIDER.")
    ingest.add_argument("--force", action="store_true", help="Re-ingest files that did not change.")
    ingest.add_argument("--limit", type=int)
    ingest.add_argument("--max-chars", type=int, default=120_000, help="Transcript characters sent to the LLM.")

    sync = add("sync", "Pull every channel and essay site in sources.json, then ingest new files.", cmd_sync)
    sync.add_argument("--no-ingest", action="store_true", help="Only download; skip the LLM step.")
    sync.add_argument("--provider", choices=["gemini", "openai"], help="Override LLM_PROVIDER.")
    sync.add_argument("--lang", help="Preferred caption languages, comma-separated.")
    sync.add_argument("--limit", type=int, help="Max new items per source.")
    sync.add_argument("--min-chars", type=int, default=400)
    sync.add_argument("--dry-run", action="store_true")

    lint = add("lint", "Check wikilinks, frontmatter, and orphans; rebuild the index.", cmd_lint)
    lint.add_argument("--fix-index", action="store_true", help="Rebuild wiki/index.md first.")
    lint.add_argument("--save", action="store_true", help="Save the report under wiki/synthesis/.")
    lint.add_argument("--review", action="store_true", help="Ask the configured LLM for maintenance suggestions.")
    lint.add_argument("--provider", choices=["gemini", "openai"], help="Override LLM_PROVIDER.")
    lint.add_argument("--strict", action="store_true", help="Exit 1 on missing links or frontmatter.")
    return parser


def main(argv: list[str] | None = None) -> int:
    # google-api-core warns on every run under Python 3.10; it is not actionable mid-command.
    warnings.filterwarnings("ignore", category=FutureWarning, module=r"google\.")
    parser = build_parser()
    args = parser.parse_args(argv)
    load_dotenv_file(getattr(args, "root", None))
    return args.func(args)
