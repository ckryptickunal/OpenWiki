"""Wiki ingest: transcript/essay → sources, entities, topics, manifest, index.

Maps to Founder Book `ingest.py`. Gemini is required unless analysis JSON is supplied.
There is no bundled offline model.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Callable

from wikiblocks.env import env_value
from wikiblocks.textfmt import parse_source_file, slugify, source_url
from wikiblocks.workspace import Workspace


def today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def load_manifest(workspace: Workspace) -> dict:
    if workspace.manifest_path.exists():
        return json.loads(workspace.manifest_path.read_text(encoding="utf-8"))
    return {}


def save_manifest(workspace: Workspace, manifest: dict) -> None:
    workspace.wiki.mkdir(parents=True, exist_ok=True)
    workspace.manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
    )


def append_log(workspace: Workspace, kind: str, title: str, detail: str = "") -> None:
    workspace.log_path.parent.mkdir(parents=True, exist_ok=True)
    with workspace.log_path.open("a", encoding="utf-8") as fh:
        fh.write(f"\n## [{today()}] {kind} | {title}\n")
        if detail:
            fh.write(f"{detail}\n")


def yaml_list(items: list[str]) -> str:
    if not items:
        return " []"
    return "\n" + "\n".join(f"  - {item}" for item in items)


def source_stem(record: dict) -> str:
    return f"{record['video_id']}-{slugify(record['title'])}"


def source_link(record: dict) -> str:
    return f"[[sources/{source_stem(record)}|{record['title']}]]"


def render_source_page(record: dict, analysis: dict) -> str:
    metadata = record["metadata"]
    tags = [slugify(tag) for tag in analysis.get("tags", [])[:12]]
    entities = analysis.get("entities", [])
    topics = analysis.get("topics", [])
    video_url = source_url(record)
    channel = metadata.get("channel", metadata.get("channel_title", "Unknown"))
    published = metadata.get("published", metadata.get("published_at", "Unknown"))

    lines = [
        "---",
        "type: source",
        f"title: {json.dumps(record['title'])[1:-1]}",
        f"created: {today()}",
        f"updated: {today()}",
        f"video_id: {record['video_id']}",
        f"url: {video_url}",
        f"channel: {channel}",
        f"published: {published}",
        "tags:" + yaml_list(tags),
        "---",
        "",
        f"# {record['title']}",
        "",
        "## Metadata",
        "",
        f"- Video ID: `{record['video_id']}`",
        f"- Channel: {channel}",
        f"- Published: {published}",
        f"- URL: {video_url}",
        "",
        "## Summary",
        "",
        analysis.get("summary", "No summary generated."),
        "",
        "## Key Ideas",
        "",
    ]
    lines.extend(f"- {idea}" for idea in analysis.get("key_ideas", []))
    lines.extend(["", "## Entities", ""])
    lines.extend(
        f"- [[entities/{slugify(entity.get('name', 'unknown'))}|{entity.get('name', 'Unknown')}]] "
        f"({entity.get('type', 'other')}): {entity.get('description', '')}"
        for entity in entities
    )
    lines.extend(["", "## Topics", ""])
    lines.extend(
        f"- [[topics/{slugify(topic.get('name', 'unknown'))}|{topic.get('name', 'Unknown')}]]: "
        f"{topic.get('summary', '')}"
        for topic in topics
    )
    lines.extend(["", "## Notable Claims", ""])
    lines.extend(
        f"- {claim.get('claim', '')} Evidence: {claim.get('evidence', '')}"
        for claim in analysis.get("claims", [])
    )
    lines.extend(["", "## Quotes", ""])
    lines.extend(f"> {quote}" for quote in analysis.get("quotes", []))
    lines.append("")
    return "\n".join(lines)


def upsert_reference_page(
    path: Path, page_type: str, title: str, description: str, source: str
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mention = f"- {source}: {description}".strip()

    if path.exists():
        content = path.read_text(encoding="utf-8")
        if source in content:
            return
        content = re.sub(r"updated: \d{4}-\d{2}-\d{2}", f"updated: {today()}", content)
        if "## Source Mentions" not in content:
            content += "\n## Source Mentions\n\n"
        content = content.rstrip() + f"\n{mention}\n"
        path.write_text(content, encoding="utf-8")
        return

    content = "\n".join(
        [
            "---",
            f"type: {page_type}",
            f"title: {json.dumps(title)[1:-1]}",
            f"created: {today()}",
            f"updated: {today()}",
            "sources: []",
            "tags: []",
            "---",
            "",
            f"# {title}",
            "",
            "## Overview",
            "",
            description or "Generated from transcript references.",
            "",
            "## Source Mentions",
            "",
            mention,
            "",
        ]
    )
    path.write_text(content, encoding="utf-8")


def update_reference_pages(workspace: Workspace, record: dict, analysis: dict) -> None:
    link = source_link(record)
    for entity in analysis.get("entities", []):
        name = (entity.get("name") or "").strip()
        if not name:
            continue
        path = workspace.entities_dir / f"{slugify(name)}.md"
        description = entity.get("description") or entity.get("importance", "")
        upsert_reference_page(path, "entity", name, description, link)

    for topic in analysis.get("topics", []):
        name = (topic.get("name") or "").strip()
        if not name:
            continue
        path = workspace.topics_dir / f"{slugify(name)}.md"
        upsert_reference_page(path, "topic", name, topic.get("summary", ""), link)


def read_title(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"^title:\s*(.+)$", text, re.MULTILINE)
    if match:
        return match.group(1).strip().strip('"')
    heading = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    return heading.group(1).strip() if heading else path.stem


def rebuild_index(workspace: Workspace) -> None:
    sections = [
        ("Sources", workspace.sources_dir),
        ("Entities", workspace.entities_dir),
        ("Topics", workspace.topics_dir),
        ("Synthesis", workspace.synthesis_dir),
    ]
    lines = [
        "# Wiki Index",
        "",
        f"Last updated: {timestamp()}",
        "",
        "This index is maintained by the wiki ingest scripts.",
        "",
    ]
    for label, directory in sections:
        lines.extend([f"## {label}", ""])
        directory.mkdir(parents=True, exist_ok=True)
        pages = sorted(directory.glob("*.md"))
        if not pages:
            lines.extend([f"No {label.lower()} pages indexed yet.", ""])
            continue
        for page in pages:
            title = read_title(page)
            rel = page.relative_to(workspace.wiki).with_suffix("")
            lines.append(f"- [[{rel}|{title}]]")
        lines.append("")
    workspace.index_path.write_text("\n".join(lines), encoding="utf-8")


def should_skip(manifest: dict, record: dict, path: Path, force: bool) -> bool:
    existing = manifest.get(record["video_id"])
    if existing and not force and existing.get("mtime") == path.stat().st_mtime:
        return True
    return False


def ingest_path(
    path: Path,
    workspace: Workspace,
    manifest: dict,
    *,
    force: bool = False,
    analysis: dict | None = None,
    analyzer: Callable[[dict, int], dict] | None = None,
    max_chars: int = 120_000,
) -> str:
    """Ingest one .txt file. Returns processed | skipped | failed."""
    path = Path(path)
    if not path.exists():
        return "failed"

    record = parse_source_file(path)
    if should_skip(manifest, record, path, force):
        return "skipped"

    if analysis is None:
        if analyzer is not None:
            analysis = analyzer(record, max_chars)
        else:
            if not env_value("GEMINI_API_KEY"):
                raise RuntimeError(
                    "Set GEMINI_API_KEY to ingest, or pass analysis JSON "
                    "(--analysis-file). There is no offline model."
                )
            from wikiblocks.gemini import analyze_record, configure_gemini

            analysis = analyze_record(configure_gemini(), record, max_chars)

    workspace.ensure_dirs()
    output_path = workspace.sources_dir / f"{source_stem(record)}.md"
    output_path.write_text(render_source_page(record, analysis), encoding="utf-8")
    update_reference_pages(workspace, record, analysis)

    manifest[record["video_id"]] = {
        "source_file": workspace.rel(path),
        "wiki_page": workspace.rel(output_path),
        "title": record["title"],
        "mtime": path.stat().st_mtime,
        "ingested_at": timestamp(),
    }
    save_manifest(workspace, manifest)
    append_log(
        workspace,
        "ingest",
        record["title"],
        f"- Source: `{workspace.rel(path)}`\n- Wiki page: `{workspace.rel(output_path)}`",
    )
    return "processed"


def ingest_paths(
    paths: list[Path],
    workspace: Workspace,
    *,
    force: bool = False,
    analysis: dict | None = None,
    analyzer: Callable[[dict, int], dict] | None = None,
    max_chars: int = 120_000,
    rebuild: bool = True,
) -> dict[str, int]:
    workspace.ensure_dirs()
    manifest = load_manifest(workspace)
    counts = {"processed": 0, "skipped": 0, "failed": 0}
    for path in paths:
        try:
            result = ingest_path(
                path,
                workspace,
                manifest,
                force=force,
                analysis=analysis,
                analyzer=analyzer,
                max_chars=max_chars,
            )
        except Exception:
            result = "failed"
        key = "processed" if result == "processed" else "skipped" if result == "skipped" else "failed"
        counts[key] += 1
    if rebuild:
        rebuild_index(workspace)
        save_manifest(workspace, manifest)
    return counts
