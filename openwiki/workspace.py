"""Workspace paths: raw source folders + generated wiki."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

SKIP_DIRS = {
    "__pycache__", "wiki", "tests", "openwiki", "venv", "node_modules",
    "docs", "examples", "site", "build", "dist",
}
SKIP_TXT_NAMES = {"_new_urls.txt"}


@dataclass(frozen=True)
class Workspace:
    root: Path

    @classmethod
    def resolve(cls, root: str | Path | None = None) -> Workspace:
        if root:
            return cls(Path(root).expanduser().resolve())
        env = os.getenv("OPENWIKI_ROOT")
        if env:
            return cls(Path(env).expanduser().resolve())
        return cls(Path.cwd().resolve())

    @property
    def wiki(self) -> Path:
        return self.root / "wiki"

    @property
    def sources_dir(self) -> Path:
        return self.wiki / "sources"

    @property
    def entities_dir(self) -> Path:
        return self.wiki / "entities"

    @property
    def topics_dir(self) -> Path:
        return self.wiki / "topics"

    @property
    def synthesis_dir(self) -> Path:
        return self.wiki / "synthesis"

    @property
    def index_path(self) -> Path:
        return self.wiki / "index.md"

    @property
    def log_path(self) -> Path:
        return self.wiki / "log.md"

    @property
    def manifest_path(self) -> Path:
        return self.wiki / "ingested.json"

    @property
    def failures_path(self) -> Path:
        return self.wiki / "ingest_failures.json"

    @property
    def schema_path(self) -> Path:
        return self.wiki / "schema.md"

    @property
    def sources_config(self) -> Path:
        return self.root / "sources.json"

    @property
    def failed_videos_path(self) -> Path:
        return self.root / "failed_videos.json"

    def ensure_dirs(self) -> None:
        for path in [
            self.wiki,
            self.sources_dir,
            self.entities_dir,
            self.topics_dir,
            self.synthesis_dir,
        ]:
            path.mkdir(parents=True, exist_ok=True)

    def rel(self, path: Path) -> str:
        try:
            return str(path.resolve().relative_to(self.root))
        except ValueError:
            return str(path)

    def discover_source_files(self, folder: str | None = None) -> list[Path]:
        """Find raw source .txt files in each top-level folder of the workspace."""
        if folder:
            directory = (self.root / folder).resolve()
            if not directory.is_dir():
                return []
            return sorted(
                p for p in directory.glob("*.txt") if p.name not in SKIP_TXT_NAMES
            )

        paths: list[Path] = []
        for child in self.root.iterdir():
            if not child.is_dir() or child.name in SKIP_DIRS or child.name.startswith("."):
                continue
            for path in child.glob("*.txt"):
                if path.name not in SKIP_TXT_NAMES:
                    paths.append(path)
        return sorted(paths)

    def load_sources_config(self) -> dict:
        path = self.sources_config
        if not path.exists():
            return {"youtube_channels": [], "essay_sources": []}
        data = json.loads(path.read_text(encoding="utf-8"))
        return {
            "youtube_channels": data.get("youtube_channels", []),
            "essay_sources": data.get("essay_sources", []),
        }

    def known_ids_for_folder(self, folder: Path) -> set[str]:
        known: set[str] = set()
        if folder.is_dir():
            for path in folder.glob("*.txt"):
                if path.name not in SKIP_TXT_NAMES:
                    known.add(path.stem)
        state_file = folder / "_extract_state.json"
        if state_file.exists():
            try:
                state = json.loads(state_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, ValueError):
                state = {}
            known.update(state.get("done", []))
            known.update(state.get("permanent_skip", []))
        return known
