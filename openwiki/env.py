"""Environment loading. Reads variable NAMES only; never logs values."""

from __future__ import annotations

import os
from pathlib import Path

PLACEHOLDER_KEYS = {
    "",
    "your-gemini-api-key-here",
    "your-youtube-data-api-key-here",
}


def load_dotenv_file(*roots: Path | str | None) -> None:
    """Load `.env` from each root (e.g. the workspace) and the current directory.

    Existing environment variables always win, and the first file that sets a
    variable wins over later ones. Missing files are ignored.
    """
    seen: set[Path] = set()
    for root in [*roots, Path.cwd()]:
        if root is None:
            continue
        candidate = (Path(root).expanduser() / ".env").resolve()
        if candidate in seen or not candidate.is_file():
            continue
        seen.add(candidate)
        _load_file(candidate)


def _load_file(path: Path) -> None:
    try:
        from dotenv import dotenv_values
    except ImportError:
        values = _parse_manual(path)
    else:
        values = dotenv_values(path)
    for key, value in values.items():
        if key and value is not None and key not in os.environ:
            os.environ[key] = value


def _parse_manual(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("'").strip('"')
    return values


def env_value(name: str) -> str | None:
    value = os.getenv(name)
    if value is None:
        return None
    stripped = value.strip()
    if stripped in PLACEHOLDER_KEYS:
        return None
    return stripped


def require_env(name: str, why: str) -> str:
    value = env_value(name)
    if not value:
        raise RuntimeError(f"Set {name} in .env or the environment. Needed for: {why}")
    return value
