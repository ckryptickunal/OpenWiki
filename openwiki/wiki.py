"""Wiki ingest: transcript/essay → sources, entities, topics, manifest, index.

Analysis comes from the configured LLM (see `openwiki.llm`) or from
caller-supplied analysis JSON.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from openwiki.textfmt import parse_source_file, slugify, source_url
from openwiki.workspace import Workspace


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


YAML_RESERVED = {"true", "false", "yes", "no", "on", "off", "null", "~", ""}


def yaml_scalar(value: object) -> str:
    """Plain YAML scalar when unambiguous, otherwise a double-quoted (JSON) string."""
    text = str(value)
    if (
        re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 _.,()/'&+:?=%~-]*", text)
        and ": " not in text
        and not text.endswith((" ", ":"))
        and text.lower() not in YAML_RESERVED
        and not re.fullmatch(r"[0-9.+-]+", text)
    ):
        return text
    return json.dumps(text, ensure_ascii=False)


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
        f"title: {yaml_scalar(record['title'])}",
        f"created: {today()}",
        f"updated: {today()}",
        f"video_id: {yaml_scalar(record['video_id'])}",
        f"url: {yaml_scalar(video_url)}",
        f"channel: {yaml_scalar(channel)}",
        f"published: {yaml_scalar(published)}",
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
            f"title: {yaml_scalar(title)}",
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
        value = match.group(1).strip()
        if value.startswith('"'):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value.strip('"')
        return value
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
        if analyzer is None:
            analyzer = default_analyzer()
        analysis = analyzer(record, max_chars)

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


def default_analyzer(provider: str | None = None) -> Callable[[dict, int], dict]:
    """Analyzer backed by the configured LLM. Raises LLMNotConfigured if there is none."""
    from openwiki.llm import analyze_record, make_client

    client = make_client(provider=provider)
    return lambda record, max_chars: analyze_record(client, record, max_chars)


def save_failures(workspace: Workspace, failures: dict[str, str]) -> None:
    if failures:
        workspace.failures_path.write_text(json.dumps(failures, indent=2, sort_keys=True), encoding="utf-8")
    elif workspace.failures_path.exists():
        workspace.failures_path.unlink()


def ingest_paths(
    paths: list[Path],
    workspace: Workspace,
    *,
    force: bool = False,
    analysis: dict | None = None,
    analyzer: Callable[[dict, int], dict] | None = None,
    max_chars: int = 120_000,
    rebuild: bool = True,
    provider: str | None = None,
    on_error: Callable[[str, Exception], None] | None = None,
) -> dict[str, int]:
    """Ingest many files. Failures are recorded in wiki/ingest_failures.json."""
    workspace.ensure_dirs()
    manifest = load_manifest(workspace)
    if analysis is None and analyzer is None:
        pending = [p for p in paths if Path(p).exists() and not should_skip(manifest, parse_source_file(p), Path(p), force)]
        if pending:
            analyzer = default_analyzer(provider)
    failures: dict[str, str] = {}
    if workspace.failures_path.exists():
        failures = json.loads(workspace.failures_path.read_text(encoding="utf-8"))
    counts = {"processed": 0, "skipped": 0, "failed": 0}
    for path in paths:
        rel = workspace.rel(Path(path))
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
            if result == "failed":
                failures[rel] = "file not found"
        except Exception as exc:
            result = "failed"
            failures[rel] = f"{type(exc).__name__}: {exc}"[:500]
            if on_error:
                on_error(rel, exc)
        if result != "failed":
            failures.pop(rel, None)
        counts[result] += 1
    save_failures(workspace, failures)
    if rebuild:
        rebuild_index(workspace)
        save_manifest(workspace, manifest)
    return counts
