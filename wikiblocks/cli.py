"""Command-line interface for Wiki-Blocks."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from wikiblocks.env import load_dotenv_file
from wikiblocks.schema import SCHEMA_MD
from wikiblocks.workspace import Workspace


def _workspace(args) -> Workspace:
    return Workspace.resolve(getattr(args, "root", None))


def cmd_init(args) -> int:
    ws = _workspace(args)
    ws.ensure_dirs()
    example = Path(__file__).resolve().parent.parent / "sources.example.json"
    if not ws.sources_config.exists() and example.exists():
        shutil.copy(example, ws.sources_config)
        print(f"Wrote {ws.sources_config}")
    if not ws.schema_path.exists():
        ws.schema_path.write_text(SCHEMA_MD, encoding="utf-8")
        print(f"Wrote {ws.schema_path}")
    print(f"Workspace ready at {ws.root}")
    return 0


def cmd_youtube(args) -> int:
    from wikiblocks.youtube import (
        extract_channel,
        extract_one_video,
        extract_videos,
        extract_video_id,
        maybe_youtube_client,
        parse_url_file,
        safe_folder_name,
    )

    ws = _workspace(args)
    youtube = maybe_youtube_client()

    if args.channel:
        result = extract_channel(
            ws,
            args.channel,
            folder=args.folder,
            dry_run=args.dry_run,
            limit=args.limit,
        )
        print(json.dumps({k: v for k, v in result.items() if k != "new"} | {"new_count": len(result.get("new", []))}, indent=2))
        if args.dry_run:
            for vid in result.get("new", [])[:20]:
                print(f"  would extract https://www.youtube.com/watch?v={vid}")
        return 0

    if args.urls_file:
        if not args.folder:
            print("--folder is required with --urls-file", file=sys.stderr)
            return 2
        ids = parse_url_file(args.urls_file)
        if args.limit:
            ids = ids[: args.limit]
        folder = ws.root / args.folder
        if args.dry_run:
            print(f"would extract {len(ids)} video(s) into {folder}")
            return 0
        counts = extract_videos(ids, folder, channel_name=args.folder, youtube=youtube)
        print(f"ok={counts['ok']} exists={counts['exists']} skip={counts['skip']} failed={counts['failed']}")
        return 0 if counts["failed"] == 0 else 1

    target = args.video
    if not target:
        print("Pass a video URL/ID, --channel, or --urls-file", file=sys.stderr)
        return 2
    video_id = extract_video_id(target)
    folder_name = args.folder or "single_videos"
    folder = ws.root / safe_folder_name(folder_name)
    if args.dry_run:
        print(f"would extract {video_id} into {folder / (video_id + '.txt')}")
        return 0
    result = extract_one_video(video_id, folder, youtube=youtube)
    if result == "skip":
        print(f"SKIP {video_id} (no captions or unplayable)")
        return 0
    if result == "exists":
        print(f"EXISTS {folder / (video_id + '.txt')}")
        return 0
    if result == "ok":
        print(f"WROTE {folder / (video_id + '.txt')}")
        return 0
    print(f"FAILED {video_id}", file=sys.stderr)
    return 1


def cmd_essay(args) -> int:
    from wikiblocks.essays import fetch_source, fetch_url, write_article_from_html

    ws = _workspace(args)

    if args.url:
        folder = ws.root / (args.folder or "Articles")
        folder.mkdir(parents=True, exist_ok=True)
        html_text = Path(args.html_file).read_text(encoding="utf-8") if args.html_file else fetch_url(args.url)
        title = args.title or args.url.rstrip("/").split("/")[-1].replace("-", " ")
        if args.dry_run:
            print(f"would write article {title!r} into {folder}")
            return 0
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

    cfg = ws.load_sources_config()
    sources = cfg.get("essay_sources", [])
    if args.source:
        sources = [s for s in sources if s.get("name", "").lower() == args.source.lower()]
    if not sources:
        print("No essay_sources in sources.json (copy sources.example.json).", file=sys.stderr)
        return 1

    total_created = total_failed = 0
    for source in sources:
        print(f"Source: {source.get('name')} ({source.get('kind', 'generic')})")
        try:
            created, failed, new = fetch_source(
                source,
                ws.root,
                dry_run=args.dry_run,
                min_chars=args.min_chars,
            )
        except Exception as exc:
            print(f"  [warn] {exc}", file=sys.stderr)
            continue
        if args.dry_run:
            print(f"  {len(new)} new")
            for essay in new[:20]:
                print(f"    {essay['title']}  {essay['url']}")
            continue
        print(f"  created={created} skipped_or_failed={failed}")
        total_created += created
        total_failed += failed
    if not args.dry_run:
        print(f"NEW ESSAYS: {total_created} created, {total_failed} skipped/failed")
    return 0


def cmd_ingest(args) -> int:
    from wikiblocks.wiki import ingest_paths

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
    if not paths:
        print("No source .txt files found.")
        return 0
    counts = ingest_paths(
        paths,
        ws,
        force=args.force,
        analysis=analysis,
        max_chars=args.max_chars,
    )
    print(
        f"processed={counts['processed']} skipped={counts['skipped']} failed={counts['failed']}"
    )
    return 0 if counts["failed"] == 0 else 1


def cmd_lint(args) -> int:
    from wikiblocks.lint import run_lint

    ws = _workspace(args)
    _, text = run_lint(
        ws,
        fix_index=args.fix_index,
        save=args.save,
        use_gemini=args.gemini,
    )
    print(text)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wikiblocks",
        description="Extract YouTube transcripts and essays, then ingest them into a Markdown wiki.",
    )
    parser.add_argument("--root", help="Workspace directory (default: cwd or WIKI_BLOCKS_ROOT).")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="Create wiki/ directories and copy sources.example.json.")
    init.set_defaults(func=cmd_init)

    yt = sub.add_parser("youtube", help="Extract captions from a video, URL list, or channel.")
    yt.add_argument("video", nargs="?", help="YouTube URL or video ID.")
    yt.add_argument("--channel", help="Channel URL, @handle, name, or channel ID.")
    yt.add_argument("--urls-file", help="File with one YouTube URL per line.")
    yt.add_argument("--folder", help="Output folder name under --root.")
    yt.add_argument("--limit", type=int, help="Max new videos to extract.")
    yt.add_argument("--dry-run", action="store_true")
    yt.set_defaults(func=cmd_youtube)

    essay = sub.add_parser("essay", help="Extract an article URL or every new item from sources.json.")
    essay.add_argument("--url", help="Single article URL.")
    essay.add_argument("--html-file", help="Local HTML file instead of fetching --url.")
    essay.add_argument("--title", help="Title for a single article.")
    essay.add_argument("--folder", help="Output folder (single article default: Articles).")
    essay.add_argument("--channel", help="Channel/source label written into the header.")
    essay.add_argument("--id-prefix", default="essay")
    essay.add_argument("--source", help="Only this essay_sources[].name from sources.json.")
    essay.add_argument("--min-chars", type=int, default=400)
    essay.add_argument("--dry-run", action="store_true")
    essay.set_defaults(func=cmd_essay)

    ingest = sub.add_parser("ingest", help="Turn .txt sources into wiki pages via Gemini or analysis JSON.")
    ingest.add_argument("--file", help="Single transcript/essay .txt file.")
    ingest.add_argument("--folder", help="Only this source folder under --root.")
    ingest.add_argument("--all", action="store_true", help="Ingest every source folder (default if --file omitted).")
    ingest.add_argument("--analysis-file", help="Skip Gemini; use this analysis JSON.")
    ingest.add_argument("--force", action="store_true")
    ingest.add_argument("--limit", type=int)
    ingest.add_argument("--max-chars", type=int, default=120_000)
    ingest.set_defaults(func=cmd_ingest)

    lint = sub.add_parser("lint", help="Check wikilinks, frontmatter, orphans. Rebuild index with --fix-index.")
    lint.add_argument("--fix-index", action="store_true")
    lint.add_argument("--save", action="store_true")
    lint.add_argument("--gemini", action="store_true", help="Ask Gemini for maintenance suggestions.")
    lint.set_defaults(func=cmd_lint)
    return parser


def main(argv: list[str] | None = None) -> int:
    load_dotenv_file()
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
