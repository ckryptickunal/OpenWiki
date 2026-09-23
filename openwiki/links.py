"""Wikilink parsing and graph walk with a visited set (no infinite loops)."""

from __future__ import annotations

import re
from collections import deque
from pathlib import Path

from openwiki.workspace import Workspace

WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
SPECIAL_FILES = {"index.md", "log.md", "schema.md", "ingested.json"}


def extract_links(text: str) -> list[str]:
    links = []
    for match in WIKILINK_RE.findall(text):
        target = match.split("|", 1)[0].split("#", 1)[0].strip()
        if target:
            links.append(target.removesuffix(".md"))
    return links


def wiki_pages(workspace: Workspace) -> dict[str, Path]:
    pages: dict[str, Path] = {}
    if not workspace.wiki.exists():
        return pages
    for path in workspace.wiki.rglob("*.md"):
        if path.name in SPECIAL_FILES:
            continue
        rel = str(path.relative_to(workspace.wiki).with_suffix(""))
        pages[rel] = path
        pages[path.stem] = path
    return pages


def canonical_rel(workspace: Workspace, path: Path) -> str:
    return str(path.relative_to(workspace.wiki).with_suffix(""))


def walk_wiki_graph(
    workspace: Workspace,
    start: str,
    *,
    max_nodes: int = 10_000,
) -> list[str]:
    """BFS from `start` following [[wikilinks]]. Cycles are skipped via a visited set."""
    pages = wiki_pages(workspace)
    if start not in pages:
        start = start.removesuffix(".md")
    if start not in pages:
        return []

    start_rel = canonical_rel(workspace, pages[start])
    visited: set[str] = set()
    order: list[str] = []
    queue: deque[str] = deque([start_rel])

    while queue and len(order) < max_nodes:
        current = queue.popleft()
        if current in visited:
            continue
        visited.add(current)
        order.append(current)
        path = pages.get(current)
        if path is None:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for link in extract_links(text):
            if link not in pages:
                continue
            target_rel = canonical_rel(workspace, pages[link])
            if target_rel not in visited:
                queue.append(target_rel)
    return order


def walk_ingest_queue(
    source_ids: list[str],
    related: dict[str, list[str]],
    *,
    max_nodes: int = 10_000,
) -> list[str]:
    """Walk source IDs that point at each other without looping.

    `related` maps a source id to other source ids mentioned by it.
    Used when ingest follows linked sources.
    """
    visited: set[str] = set()
    order: list[str] = []
    queue: deque[str] = deque(source_ids)
    while queue and len(order) < max_nodes:
        current = queue.popleft()
        if current in visited:
            continue
        visited.add(current)
        order.append(current)
        for nxt in related.get(current, []):
            if nxt not in visited:
                queue.append(nxt)
    return order
