"""Wiki health check: missing links, missing frontmatter, orphans, index rebuild.

`--review` optionally asks the configured LLM for maintenance suggestions.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from openwiki.links import extract_links, wiki_pages
from openwiki.wiki import append_log, rebuild_index, today
from openwiki.workspace import Workspace


def timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def has_frontmatter(text: str) -> bool:
    return text.startswith("---\n") and "\n---\n" in text[4:]


def build_report(workspace: Workspace) -> dict:
    pages = wiki_pages(workspace)
    canonical = {
        str(path.relative_to(workspace.wiki).with_suffix("")): path
        for path in set(pages.values())
    }
    inbound = {rel: 0 for rel in canonical}
    missing_links = []
    missing_frontmatter = []
    page_count_by_dir: dict[str, int] = {}

    for rel, path in canonical.items():
        text = path.read_text(encoding="utf-8", errors="replace")
        top_dir = rel.split("/", 1)[0] if "/" in rel else "."
        page_count_by_dir[top_dir] = page_count_by_dir.get(top_dir, 0) + 1
        if not has_frontmatter(text):
            missing_frontmatter.append(rel)
        for link in extract_links(text):
            if link in pages:
                target_rel = str(pages[link].relative_to(workspace.wiki).with_suffix(""))
                inbound[target_rel] = inbound.get(target_rel, 0) + 1
            else:
                missing_links.append({"from": rel, "target": link})

    orphan_pages = [
        rel
        for rel, count in inbound.items()
        if count == 0 and not rel.startswith("sources/")
    ]
    return {
        "generated_at": timestamp(),
        "page_count": len(canonical),
        "page_count_by_dir": page_count_by_dir,
        "orphan_pages": sorted(orphan_pages),
        "missing_links": missing_links,
        "missing_frontmatter": sorted(missing_frontmatter),
    }


def render_report(report: dict) -> str:
    lines = [
        "# Wiki Lint Report",
        "",
        f"Generated: {report['generated_at']}",
        "",
        "## Summary",
        "",
        f"- Total pages: {report['page_count']}",
    ]
    for directory, count in sorted(report["page_count_by_dir"].items()):
        lines.append(f"- `{directory}/`: {count}")

    lines.extend(["", "## Orphan Pages", ""])
    if report["orphan_pages"]:
        lines.extend(f"- `{page}`" for page in report["orphan_pages"])
    else:
        lines.append("No non-source orphan pages found.")

    lines.extend(["", "## Missing Links", ""])
    if report["missing_links"]:
        lines.extend(
            f"- `{item['from']}` links to missing page `{item['target']}`"
            for item in report["missing_links"]
        )
    else:
        lines.append("No missing wikilinks found.")

    lines.extend(["", "## Missing Frontmatter", ""])
    if report["missing_frontmatter"]:
        lines.extend(f"- `{page}`" for page in report["missing_frontmatter"])
    else:
        lines.append("All generated pages have frontmatter.")
    return "\n".join(lines)


def save_report(workspace: Workspace, report_text: str, review_text: str | None = None) -> Path:
    workspace.synthesis_dir.mkdir(parents=True, exist_ok=True)
    path = workspace.synthesis_dir / f"{today()}-wiki-lint-report.md"
    content = "\n".join(
        [
            "---",
            "type: synthesis",
            "title: Wiki Lint Report",
            f"created: {today()}",
            f"updated: {today()}",
            "sources: []",
            "tags:",
            "  - lint",
            "---",
            "",
            report_text,
            "",
        ]
    )
    if review_text:
        content += "\n## LLM Maintenance Suggestions\n\n" + review_text + "\n"
    path.write_text(content, encoding="utf-8")
    rebuild_index(workspace)
    append_log(workspace, "lint", "Wiki Lint Report", f"- Saved: `{workspace.rel(path)}`")
    return path


def llm_review(workspace: Workspace, report_text: str, provider: str | None = None) -> str:
    from openwiki.llm import make_client

    client = make_client(provider=provider, lint=True)
    index_text = (
        workspace.index_path.read_text(encoding="utf-8", errors="replace")
        if workspace.index_path.exists()
        else ""
    )
    prompt = f"""
You are maintaining an LLM-generated markdown wiki.

Review this lint report and index. Suggest the highest-value maintenance actions:
- missing cross-references
- topics/entities that likely need pages
- stale or weak synthesis opportunities
- data gaps to fill later

Keep the answer concise and actionable. Do not invent facts not present in the report/index.

Lint report:
{report_text}

Index:
{index_text[:60_000]}
"""
    return client.generate(prompt, temperature=0.2).strip()


def run_lint(
    workspace: Workspace,
    *,
    fix_index: bool = False,
    save: bool = False,
    review: bool = False,
    provider: str | None = None,
) -> tuple[dict, str]:
    if fix_index:
        workspace.ensure_dirs()
        rebuild_index(workspace)
    report = build_report(workspace)
    report_text = render_report(report)
    review_text = llm_review(workspace, report_text, provider) if review else None
    if save:
        save_report(workspace, report_text, review_text)
    if review_text:
        report_text = report_text + "\n\n## LLM Maintenance Suggestions\n\n" + review_text
    return report, report_text
